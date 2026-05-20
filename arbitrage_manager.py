```python
"""
Arbitrage Manager v1.0 - Cross-Venue Funding Rate Arbitrage
Cash & Carry and Reverse Cash & Carry Strategies for Kraken Spot ↔ Perpetual
Integrates with Titan v4.1 for capital allocation signaling
"""

import os
import json
import time
import subprocess
import sys
from datetime import datetime
from typing import Dict, Optional, List, Tuple
import requests

class ArbitrageManager:
    """
    Manages cash-and-carry and reverse cash-and-carry arbitrage strategies
    Monitors Kraken Spot vs Perpetual pricing and funding rates
    """
    
    def __init__(self, use_paper_trading: bool = True):
        self.use_paper_trading = use_paper_trading
        self.min_yield_bps = 50  # Minimum yield in basis points (50 bps = 0.5%)
        self.trading_pairs = ["BTCUSD", "ETHUSD", "SOLUSD", "LINKUSD"]
        self.positions = {}
        self.session = requests.Session()
        
        print("\n" + "=" * 70)
        print("ARBITRAGE MANAGER v1.0 INITIALIZED")
        print("=" * 70)
        print(f"Mode: {'PAPER TRADING' if use_paper_trading else 'LIVE TRADING'}")
        print(f"Min Yield Threshold: {self.min_yield_bps} bps")
        print(f"Monitoring Pairs: {', '.join(self.trading_pairs)}")
        print("=" * 70)
    
    def fetch_kraken_spot_ticker(self, pair: str) -> Optional[Dict]:
        """Fetch Kraken Spot ticker via CLI"""
        try:
            result = subprocess.run(
                ["kraken", "ticker", pair, "-o", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"   ⚠️  Spot ticker fetch failed for {pair}: {result.stderr.strip()}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error fetching spot ticker for {pair}: {e}")
            return None
    
    def fetch_kraken_futures_ticker(self, pair: str) -> Optional[Dict]:
        """Fetch Kraken Perpetual ticker via CLI"""
        try:
            perp_pair = pair.replace("USD", "-PERP")
            result = subprocess.run(
                ["kraken", "ticker", perp_pair, "-o", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"   ⚠️  Futures ticker fetch failed for {perp_pair}: {result.stderr.strip()}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error fetching futures ticker for {pair}: {e}")
            return None
    
    def _parse_ticker_prices(self, ticker_payload: Dict, pair: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Safely extracts best ask and bid prices from Kraken CLI JSON layouts.
        Handles nested assets under standard "result" blocks or flat keys.
        """
        if not ticker_payload:
            return None, None
            
        # Isolate results block if wrapped inside a result key
        data = ticker_payload.get("result", ticker_payload)
        
        # Look for the asset details inside the dictionary
        pair_data = data.get(pair)
        
        if not pair_data:
            # Check for alternative naming conventions (e.g. BTCUSD vs XXBTZUSD)
            clean_pairs = {k.replace("/", "").replace("-", ""): v for k, v in data.items() if isinstance(v, dict)}
            clean_target = pair.replace("/", "").replace("-", "")
            pair_data = clean_pairs.get(clean_target)
            
        if not pair_data and isinstance(data, dict):
            # Fallback if asks/bids are directly at root level
            ask_val = data.get("ask") or data.get("a")
            bid_val = data.get("bid") or data.get("b")
            
            if ask_val and bid_val:
                final_ask = float(ask_val[0]) if isinstance(ask_val, list) else float(ask_val)
                final_bid = float(bid_val[0]) if isinstance(bid_val, list) else float(bid_val)
                return final_ask, final_bid
                
        if isinstance(pair_data, dict):
            # Extract standard Kraken ticker properties: 'a' for ask, 'b' for bid
            ask_val = pair_data.get("a") or pair_data.get("ask")
            bid_val = pair_data.get("b") or pair_data.get("bid")
            
            try:
                final_ask = float(ask_val[0]) if isinstance(ask_val, list) else float(ask_val)
                final_bid = float(bid_val[0]) if isinstance(bid_val, list) else float(bid_val)
                return final_ask, final_bid
            except (IndexError, ValueError, TypeError):
                pass
                
        return None, None

    def fetch_funding_rate(self, pair: str) -> Optional[float]:
        """Fetch current funding rate for perpetual contract"""
        try:
            perp_pair = pair.replace("USD", "-PERP")
            result = subprocess.run(
                ["kraken", "funding_rate", perp_pair, "-o", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                unwrapped = data.get("result", data)
                val = unwrapped.get("fundingRate") or unwrapped.get("funding_rate")
                return float(val) if val is not None else None
            else:
                print(f"   ⚠️  Funding rate fetch failed for {perp_pair}: {result.stderr.strip()}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error fetching funding rate for {pair}: {e}")
            return None
    
    def calculate_cash_and_carry_yield(
        self, 
        spot_ask: float, 
        perp_bid: float, 
        funding_rate: float,
        funding_epochs: int = 56  # 7 days * 8 epochs/day
    ) -> Tuple[float, float]:
        """
        Calculate net yield for cash-and-carry (BUY spot + SHORT perp)
        
        Returns: (net_yield_bps, annualized_yield_pct)
        """
        premium_pct = ((perp_bid - spot_ask) / spot_ask) * 100
        funding_yield_pct = funding_rate * funding_epochs * 100
        
        # Estimate fees: 0.16% maker + taker for spot, 0.05% for futures
        estimated_fees_pct = 0.21
        
        net_yield_pct = premium_pct + funding_yield_pct - estimated_fees_pct
        net_yield_bps = net_yield_pct * 100
        
        # Annualize: 7-day yield * 52 weeks per year
        annualized_yield_pct = net_yield_pct * 52
        
        return net_yield_bps, annualized_yield_pct
    
    def check_arbitrage_opportunity(self, pair: str) -> Optional[Dict]:
        """
        Check if cash-and-carry opportunity exists for a given pair
        """
        print(f"\n   📊 Scanning {pair}...")
        
        # Fetch raw market data
        spot_ticker_payload = self.fetch_kraken_spot_ticker(pair)
        if not spot_ticker_payload:
            return None
        
        futures_ticker_payload = self.fetch_kraken_futures_ticker(pair)
        if not futures_ticker_payload:
            return None
        
        funding_rate = self.fetch_funding_rate(pair)
        if funding_rate is None:
            return None
        
        # Safely extract bid/ask prices via parsing utility
        spot_ask, spot_bid = self._parse_ticker_prices(spot_ticker_payload, pair)
        perp_ask, perp_bid = self._parse_ticker_prices(futures_ticker_payload, pair.replace("USD", "-PERP"))
        
        if not spot_ask or not perp_bid:
            print(f"   ⚠️  Incomplete or unparsed price data for {pair}")
            return None
        
        # Calculate yields
        net_yield_bps, annualized_yield = self.calculate_cash_and_carry_yield(
            spot_ask, perp_bid, funding_rate
        )
        
        print(f"      Spot Ask: ${spot_ask:.2f}")
        print(f"      Perp Bid: ${perp_bid:.2f}")
        print(f"      Premium: {((perp_bid - spot_ask) / spot_ask * 100):.4f}%")
        print(f"      Funding Rate: {funding_rate * 100:.4f}% per epoch")
        print(f"      Net Yield: {net_yield_bps:.0f} bps ({annualized_yield:.1f}% annualized)")
        
        if net_yield_bps >= self.min_yield_bps:
            print(f"      ✅ OPPORTUNITY FOUND!")
            
            return {
                "pair": pair,
                "spot_ask": spot_ask,
                "spot_bid": spot_bid,
                "perp_bid": perp_bid,
                "perp_ask": perp_ask,
                "funding_rate": funding_rate,
                "net_yield_bps": net_yield_bps,
                "annualized_yield": annualized_yield,
                "signal_strength": min(net_yield_bps / 100, 1.0)  # Confidence metric
            }
        else:
            print(f"      ⏸️  Below minimum threshold")
            return None
    
    def execute_cash_and_carry(self, opportunity: Dict, position_size: float = 1.0) -> bool:
        """
        Execute cash-and-carry: BUY spot + SHORT perpetual
        """
        pair = opportunity["pair"]
        print(f"\n   ⚡ EXECUTING CASH & CARRY: {pair}")
        print(f"      Position Size: {position_size}")
        print(f"      Expected Yield: {opportunity['net_yield_bps']:.0f} bps")
        
        try:
            # BUY spot
            if self.use_paper_trading:
                buy_cmd = ["kraken", "paper", "order", "buy", pair, "market", str(position_size)]
            else:
                buy_cmd = ["kraken", "order", "buy", pair, "market", str(position_size)]
            
            buy_result = subprocess.run(buy_cmd, capture_output=True, text=True, timeout=10)
            
            if buy_result.returncode != 0:
                print(f"   ❌ Spot buy failed: {buy_result.stderr.strip()}")
                return False
            
            print(f"   ✅ Spot BUY executed")
            
            # SHORT perpetual
            perp_pair = pair.replace("USD", "-PERP")
            if self.use_paper_trading:
                short_cmd = ["kraken", "paper", "order", "sell", perp_pair, "market", str(position_size)]
            else:
                short_cmd = ["kraken", "order", "sell", perp_pair, "market", str(position_size)]
            
            short_result = subprocess.run(short_cmd, capture_output=True, text=True, timeout=10)
            
            if short_result.returncode != 0:
                print(f"   ❌ Futures SHORT failed: {short_result.stderr.strip()}")
                return False
            
            print(f"   ✅ Perpetual SHORT executed")
            
            # Track position
            self.positions[pair] = {
                "entry_time": datetime.now().isoformat(),
                "spot_position": position_size,
                "futures_position": -position_size,
                "entry_premium": opportunity["net_yield_bps"],
                "expected_yield": opportunity["annualized_yield"]
            }
            
            print(f"   ✅ Position tracked")
            return True
            
        except Exception as e:
            print(f"   ❌ Execution error: {e}")
            return False
    
    def scan_all_pairs(self) -> List[Dict]:
        """Scan all trading pairs for opportunities"""
        opportunities = []
        
        print(f"\n{'=' * 70}")
        print(f"ARBITRAGE SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"{'=' * 70}")
        
        for pair in self.trading_pairs:
            opportunity = self.check_arbitrage_opportunity(pair)
            if opportunity:
                opportunities.append(opportunity)
        
        return opportunities
    
    def run_continuous_monitor(self, scan_interval: int = 60):
        """Run continuous monitoring loop"""
        print(f"\n🔄 Starting continuous arbitrage monitor (every {scan_interval}s)")
        print("Press Ctrl+C to stop\n")
        
        scan_count = 0
        opportunities_found = 0
        
        try:
            while True:
                scan_count += 1
                opportunities = self.scan_all_pairs()
                
                if opportunities:
                    opportunities_found += len(opportunities)
                    print(f"\n🎯 {len(opportunities)} opportunity(ies) found!")
                    
                    # Execute arbitrage on best opportunity
                    best_opp = max(opportunities, key=lambda x: x["net_yield_bps"])
                    self.execute_cash_and_carry(best_opp)
                
                print(f"\n   ⏰ Next scan in {scan_interval} seconds...")
                print(f"   📊 Total scans: {scan_count} | Opportunities: {opportunities_found}")
                
                time.sleep(scan_interval)
        
        except KeyboardInterrupt:
            print(f"\n\n⏹️  ARBITRAGE MONITOR STOPPED")
        
        finally:
            print(f"\n{'=' * 70}")
            print(f"ARBITRAGE SESSION COMPLETE")
            print(f"{'=' * 70}")
            print(f"Total Scans: {scan_count}")
            print(f"Opportunities Found: {opportunities_found}")
            print(f"Active Positions: {len(self.positions)}")
            print(f"{'=' * 70}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "single"
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    
    manager = ArbitrageManager(use_paper_trading=True)
    
    if mode == "loop":
        manager.run_continuous_monitor(scan_interval=interval)
    else:
        opportunities = manager.scan_all_pairs()
        if opportunities:
            print(f"\n✅ Found {len(opportunities)} opportunity(ies)")

```
