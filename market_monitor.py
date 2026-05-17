"""
Real-Time Market Monitor - AI-Native Kraken Trading Agent
Continuous autonomous trading with Gemini 3.1 Pro decision-making
"""

import os
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List

load_dotenv()

class RealtimeMarketMonitor:
    """Continuous market monitoring with autonomous trading decisions"""
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.kraken_api_key = os.getenv("KRAKEN_API_KEY")
        self.kraken_api_secret = os.getenv("KRAKEN_API_SECRET")
        
        self.pair = os.getenv("TRADING_PAIR", "ONDOUSD")
        self.check_interval = int(os.getenv("CHECK_INTERVAL", "30"))
        self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.75"))
        self.min_risk_reward = float(os.getenv("MIN_RISK_REWARD_RATIO", "1.5"))
        self.max_daily_trades = int(os.getenv("MAX_DAILY_TRADES", "10"))
        
        self.trades_today = 0
        self.trade_history: List[Dict[str, Any]] = []
        self.monitoring_start = datetime.now()
        
    def get_market_data(self) -> Optional[Dict[str, Any]]:
        """Fetch current market data via Kraken CLI"""
        try:
            result = subprocess.run(
                ["kraken", "ticker", self.pair, "-o", "json"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            return None
        except Exception as e:
            print(f"   ⚠️  Market data fetch failed: {e}")
            return None
    
    def get_orderbook_snapshot(self, depth: int = 5) -> Optional[Dict[str, Any]]:
        """Get order book snapshot"""
        try:
            result = subprocess.run(
                ["kraken", "orderbook", self.pair, "--depth", str(depth), "-o", "json"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            return None
        except Exception as e:
            print(f"   ⚠️  Order book fetch failed: {e}")
            return None
    
    def gemini_analyze_market(self, market_data: Dict[str, Any], orderbook: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Gemini 3.1 Pro analyzes market data and returns trading decision.
        
        Returns:
        {
            "action": "BUY|SELL|HOLD",
            "confidence": 0.0-1.0,
            "entry_price": float,
            "stop_loss": float,
            "take_profit": float,
            "size": float,
            "reason": "explanation"
        }
        """
        print(f"   🧠 Gemini analyzing {self.pair}...")
        
        # In production, this calls Gemini API with MCP
        # For now, simulating with decision logic
        try:
            if not market_data or not orderbook:
                return {"action": "HOLD", "confidence": 0.0, "reason": "Insufficient data"}
            
            # Simulated Gemini decision based on market conditions
            decision = {
                "action": "HOLD",
                "confidence": 0.68,
                "entry_price": None,
                "stop_loss": None,
                "take_profit": None,
                "size": 0.0,
                "reason": "Awaiting stronger market signals"
            }
            
            return decision
            
        except Exception as e:
            print(f"   ❌ Gemini analysis error: {e}")
            return None
    
    def validate_trade(self, decision: Dict[str, Any]) -> bool:
        """Validate trade meets safety criteria before execution"""
        
        # Check confidence threshold
        if decision["confidence"] < self.confidence_threshold:
            print(f"   ❌ Confidence {decision['confidence']:.2f} < threshold {self.confidence_threshold}")
            return False
        
        # Check daily trade limit
        if self.trades_today >= self.max_daily_trades:
            print(f"   ❌ Daily trade limit reached ({self.max_daily_trades})")
            return False
        
        # Check action is valid
        if decision["action"] not in ["BUY", "SELL"]:
            print(f"   ⏸️  Action is {decision['action']} - holding")
            return False
        
        # Check risk/reward ratio
        if decision["stop_loss"] and decision["take_profit"]:
            entry = decision["entry_price"]
            sl = decision["stop_loss"]
            tp = decision["take_profit"]
            
            risk = abs(entry - sl)
            reward = abs(tp - entry)
            
            if reward > 0:
                ratio = reward / risk
                if ratio < self.min_risk_reward:
                    print(f"   ❌ Risk/Reward {ratio:.2f} < threshold {self.min_risk_reward}")
                    return False
        
        return True
    
    def execute_trade(self, decision: Dict[str, Any]) -> bool:
        """Execute paper trade with all safety checks"""
        print(f"   📈 Executing {decision['action']} signal...")
        
        try:
            trade_record = {
                "timestamp": datetime.now().isoformat(),
                "pair": self.pair,
                "action": decision["action"],
                "entry_price": decision["entry_price"],
                "stop_loss": decision["stop_loss"],
                "take_profit": decision["take_profit"],
                "size": decision["size"],
                "confidence": decision["confidence"],
                "status": "SIMULATED_PAPER_TRADE"
            }
            
            self.trade_history.append(trade_record)
            self.trades_today += 1
            
            print(f"   ✅ Trade #{self.trades_today} placed:")
            print(f"      • Action: {decision['action']}")
            print(f"      • Entry: ${decision['entry_price']:.2f}")
            print(f"      • Stop Loss: ${decision['stop_loss']:.2f}")
            print(f"      • Take Profit: ${decision['take_profit']:.2f}")
            print(f"      • Confidence: {decision['confidence']:.0%}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Trade execution failed: {e}")
            return False
    
    def check_daily_reset(self):
        """Reset daily trade counter at midnight"""
        if datetime.now().hour == 0 and datetime.now().minute < 1:
            self.trades_today = 0
            print("🔄 Daily trade counter reset")
    
    def print_session_stats(self):
        """Print current session statistics"""
        elapsed = datetime.now() - self.monitoring_start
        
        print("\n" + "=" * 60)
        print("📊 SESSION STATISTICS")
        print("=" * 60)
        print(f"Elapsed Time: {elapsed}")
        print(f"Market: {self.pair}")
        print(f"Trades Today: {self.trades_today}/{self.max_daily_trades}")
        print(f"Check Interval: {self.check_interval}s")
        print(f"Confidence Threshold: {self.confidence_threshold:.0%}")
        
        if self.trade_history:
            buy_trades = sum(1 for t in self.trade_history if t["action"] == "BUY")
            sell_trades = sum(1 for t in self.trade_history if t["action"] == "SELL")
            print(f"\nTrades Executed:")
            print(f"  • BUY:  {buy_trades}")
            print(f"  • SELL: {sell_trades}")
        else:
            print(f"\nNo trades executed yet")
        
        print("=" * 60)
    
    def run_monitoring_loop(self, duration_minutes: int = 5):
        """
        Main monitoring loop - continuous market analysis and autonomous trading
        
        Args:
            duration_minutes: How long to run monitoring (default 5 minutes for testing)
        """
        print("\n" + "=" * 70)
        print("🔄 REAL-TIME MARKET MONITOR - AUTONOMOUS TRADING ACTIVE")
        print("=" * 70)
        print(f"Monitoring: {self.pair}")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Check Interval: {self.check_interval} seconds")
        print(f"Safety: Paper trading only, no real capital at risk")
        print("=" * 70)
        
        start_time = time.time()
        duration_seconds = duration_minutes * 60
        cycle = 0
        
        try:
            while time.time() - start_time < duration_seconds:
                cycle += 1
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                print(f"\n[{timestamp}] Monitoring Cycle #{cycle}")
                print("-" * 70)
                
                # Check for daily reset
                self.check_daily_reset()
                
                # Fetch market data
                market_data = self.get_market_data()
                orderbook = self.get_orderbook_snapshot()
                
                if not market_data:
                    print("   ⚠️  Skipping cycle - no market data")
                    time.sleep(self.check_interval)
                    continue
                
                # Gemini analyzes market
                decision = self.gemini_analyze_market(market_data, orderbook)
                
                if decision:
                    print(f"   💭 Gemini Decision: {decision['action']} (confidence: {decision['confidence']:.0%})")
                    print(f"      Reason: {decision['reason']}")
                    
                    # Validate and execute if criteria met
                    if self.validate_trade(decision):
                        self.execute_trade(decision)
                    else:
                        print(f"   ⏸️  Trade blocked by safety checks")
                else:
                    print("   ❌ Analysis failed")
                
                # Wait before next check
                remaining = duration_seconds - (time.time() - start_time)
                if remaining > 0:
                    time.sleep(min(self.check_interval, remaining))
        
        except KeyboardInterrupt:
            print("\n⚠️  Monitoring interrupted by user")
        
        finally:
            print("\n" + "=" * 70)
            print("✅ MONITORING SESSION COMPLETE")
            print("=" * 70)
            self.print_session_stats()

if __name__ == "__main__":
    # Run for 5 minutes in test mode, or pass duration as argument
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    
    monitor = RealtimeMarketMonitor()
    monitor.run_monitoring_loop(duration_minutes=duration)
