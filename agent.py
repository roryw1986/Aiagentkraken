```python
#!/usr/bin/env python3
"""
AI-Native Kraken Trading Agent - Phase 1 (Robust Edition)
Initializes Kraken CLI connection and performs market analysis
Compatible with standard Kraken nested JSON responses
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file securely
load_dotenv()

class KrakenAgent:
    """Orchestrates Kraken CLI interactions for the AI trading system"""
    
    def __init__(self):
        self.api_key = os.getenv("KRAKEN_API_KEY")
        self.api_secret = os.getenv("KRAKEN_API_SECRET")
        self.pair = "ONDOUSD"
        
    def verify_installation(self):
        """Verify Kraken CLI is installed and accessible"""
        print("🔍 Verifying Kraken CLI installation...")
        try:
            result = subprocess.run(
                ["kraken", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            print(f"✅ Kraken CLI verified: {result.stdout.strip()}")
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            print(f"❌ Kraken CLI not found: {e}")
            print("   Run 'bash setup.sh' to install")
            return False
    
    def check_credentials(self):
        """Verify API credentials are set"""
        print("\n🔐 Checking API credentials...")
        if not self.api_key or not self.api_secret:
            print("❌ API credentials not found in environment variables")
            print("   Copy .env.example to .env and add your Kraken API keys")
            return False
        print("✅ API credentials loaded")
        return True

    def _unwrap_payload(self, raw_payload, key_target=None):
        """
        Safely extracts the active data layer from Kraken CLI JSON structures.
        Bypasses the outer 'result' block and nested asset keys dynamically.
        """
        if not raw_payload:
            return {}
        
        # Unwrap standard Kraken response nesting
        data = raw_payload.get("result", raw_payload)
        
        if key_target and isinstance(data, dict):
            # Look for explicit key matching (e.g., ONDOUSD)
            if key_target in data:
                return data[key_target]
            
            # Look for alternative key transformations
            clean_pairs = {k.replace("/", "").replace("-", ""): v for k, v in data.items() if isinstance(v, dict)}
            clean_target = key_target.replace("/", "").replace("-", "")
            if clean_target in clean_pairs:
                return clean_pairs[clean_target]
                
        return data
    
    def get_ticker(self, pair=None):
        """Fetch ticker data for a trading pair safely un-wrapping metadata"""
        if pair is None:
            pair = self.pair
            
        print(f"\n📊 Fetching {pair} ticker data...")
        try:
            result = subprocess.run(
                ["kraken", "ticker", pair, "-o", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                raw_data = json.loads(result.stdout)
                data = self._unwrap_payload(raw_data, pair)
                print(f"✅ Ticker data retrieved:")
                print(json.dumps(data, indent=2))
                return data
            else:
                print(f"❌ Error fetching ticker: {result.stderr.strip()}")
                return None
                
        except Exception as e:
            print(f"❌ Exception during ticker fetch: {e}")
            return None
    
    def check_paper_balance(self):
        """Check paper trading account balance"""
        print("\n💰 Checking paper trading balance...")
        try:
            result = subprocess.run(
                ["kraken", "paper", "balance", "-o", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                raw_data = json.loads(result.stdout)
                data = self._unwrap_payload(raw_data)
                print(f"✅ Paper balance:")
                print(json.dumps(data, indent=2))
                return data
            else:
                print(f"⚠️  Paper trading may not be initialized")
                return None
                
        except Exception as e:
            print(f"❌ Exception during balance check: {e}")
            return None
    
    def analyze_orderbook(self, pair=None, depth=10):
        """Analyze order book safely processing nested bids and asks"""
        if pair is None:
            pair = self.pair
            
        print(f"\n📈 Analyzing {pair} order book (depth={depth})...")
        try:
            result = subprocess.run(
                ["kraken", "orderbook", pair, "--depth", str(depth), "-o", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                raw_data = json.loads(result.stdout)
                data = self._unwrap_payload(raw_data, pair)
                
                bids = data.get("bids", [])
                asks = data.get("asks", [])
                
                # Verify that unwrapped order book metrics are present
                if bids and asks:
                    best_bid = float(bids[0][0])
                    best_ask = float(asks[0][0])
                    spread = best_ask - best_bid
                    spread_pct = (spread / best_bid) * 100
                    
                    analysis = {
                        "pair": pair,
                        "best_bid": best_bid,
                        "best_ask": best_ask,
                        "spread": spread,
                        "spread_percentage": round(spread_pct, 4),
                        "market_condition": "tight" if spread_pct < 0.1 else "normal" if spread_pct < 0.5 else "wide"
                    }
                    
                    print(f"✅ Order book analysis:")
                    print(json.dumps(analysis, indent=2))
                    return analysis
                else:
                    print(f"❌ Invalid or empty unwrapped order book data: {data}")
                    return None
            else:
                print(f"❌ Error fetching order book: {result.stderr.strip()}")
                return None
                
        except Exception as e:
            print(f"❌ Exception during order book analysis: {e}")
            return None
    
    def run_phase_1_tests(self):
        """Execute Phase 1 initialization and testing"""
        print("=" * 60)
        print("🚀 PHASE 1: AI AGENT INFRASTRUCTURE INITIALIZATION")
        print("=" * 60)
        
        # Step 1: Verify Installation
        if not self.verify_installation():
            sys.exit(1)
        
        # Step 2: Check Credentials
        has_credentials = self.check_credentials()
        if not has_credentials:
            print("⚠️  Continuing with public endpoints only (no trading)")
        
        # Step 3: Fetch Market Data
        ticker = self.get_ticker()
        
        # Step 4: Check Paper Balance
        balance = self.check_paper_balance()
        
        # Step 5: Analyze Order Book
        analysis = self.analyze_orderbook()
        
        # Summary Report
        print("\n" + "=" * 60)
        print("📋 PHASE 1 TEST SUMMARY")
        print("=" * 60)
        print("✅ Kraken CLI installed and verified")
        print("✅ API credentials configured" if has_credentials else "⚠️  Running in public mode")
        print("✅ Market data retrieval functional" if ticker else "❌ Market data retrieval failed")
        print("✅ Paper trading available" if balance else "⚠️  Paper trading not initialized")
        print("✅ Order book analysis operational" if analysis else "❌ Order book analysis failed")
        print("=" * 60)
        print("\n✨ Phase 1 infrastructure ready for Phase 2 integration!")
        print("   Next: Integrate Gemini 2.5 Pro for autonomous decision-making\n")

if __name__ == "__main__":
    agent = KrakenAgent()
    agent.run_phase_1_tests()

```
