"""
Titan Predator v4.0 - Phase 2 Architecture (Multi-Asset)
Two-Tier Institutional Gateway for Autonomous Quantitative Trading
================================================================================
TIER 1: Local Quantitative Pre-Compute (The Gatekeeper)
    - Runs every 60 seconds on cloud server across target basket
    - Processes top 10 depth tiers of live Kraken Pro order book
    - Validates strict structural compression thresholds

TIER 2: Generative Intelligence (The Execution Brain)
    - Gemini 2.5 Pro analyzes pre-filtered signals
    - Evaluates Value Compression & Liquidity Springs (NO BREAKOUTS)
    - Returns definitive JSON payload for execution
================================================================================
"""

import os
import json
import subprocess
import time
from datetime import datetime
from typing import Optional, Dict, Any, Tuple, List
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Initialize Google GenAI Client
client = genai.Client()

# High-Conviction Digital Infrastructure Basket
TARGET_PAIRS = ["ONDOUSD", "LINKUSD", "SOLUSD", "CFGUSD", "BTCUSD", "SKYUSD", "ZKUSD"]

# ============================================================================
# TIER 1: LOCAL QUANTITATIVE PRE-COMPUTE (The Gatekeeper)
# ============================================================================

class Tier1Gatekeeper:
    """
    Local quantitative analysis running on cloud server.
    Processes order book to validate strict structural compression.
    """
    
    def __init__(self, pair: str):
        # Fixed double underscores and accepts pair dynamically
        self.pair = pair
        self.depth_tiers = 10
        self.spread_compression_threshold = 0.09
        self.obi_threshold = 0.30  # +0.30 OBI (>65% bid dominance)
    
    def fetch_orderbook_snapshot(self) -> Optional[Dict[str, Any]]:
        try:
            result = subprocess.run(
                ["kraken", "orderbook", self.pair, "--depth", str(self.depth_tiers), "-o", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"   ⚠️  Order book fetch failed for {self.pair}")
                return None
            
            return json.loads(result.stdout)
        
        except Exception as e:
            print(f"   ❌ Error fetching order book: {e}")
            return None
    
    def calculate_spread_compression(self, orderbook: Dict[str, Any]) -> Optional[float]:
        try:
            bids = orderbook.get("bids", [])
            asks = orderbook.get("asks", [])
            
            if not bids or not asks:
                return None
            
            best_bid_price = float(bids[0][0])
            best_ask_price = float(asks[0][0])
            mid_price = (best_bid_price + best_ask_price) / 2
            
            return (best_ask_price - best_bid_price) / mid_price
        
        except (KeyError, IndexError, ValueError, TypeError):
            return None
    
    def calculate_order_book_imbalance(self, orderbook: Dict[str, Any]) -> Optional[float]:
        try:
            bids = orderbook.get("bids", [])
            asks = orderbook.get("asks", [])
            
            if not bids or not asks:
                return None
            
            bid_volume = sum(float(bid[1]) for bid in bids[:self.depth_tiers])
            ask_volume = sum(float(ask[1]) for ask in asks[:self.depth_tiers])
            total_volume = bid_volume + ask_volume
            
            if total_volume == 0:
                return None
            
            return (bid_volume - ask_volume) / total_volume
        
        except (KeyError, IndexError, ValueError, TypeError):
            return None
    
    def execute_tier1_validation(self) -> Tuple[bool, Dict[str, Any]]:
        print(f"\n   🔍 Scanning {self.pair}...")
        orderbook = self.fetch_orderbook_snapshot()
        
        if not orderbook:
            return False, {"status": "orderbook_fetch_failed"}
        
        spread = self.calculate_spread_compression(orderbook)
        if spread is None:
            return False, {"status": "spread_calc_failed"}
        
        spread_pct = spread * 100
        passes_spread_check = spread_pct < self.spread_compression_threshold
        
        obi = self.calculate_order_book_imbalance(orderbook)
        if obi is None:
            return False, {"status": "obi_calc_failed"}
        
        bid_dominance_pct = ((obi + 1) / 2) * 100
        passes_obi_check = obi > self.obi_threshold
        
        both_pass = passes_spread_check and passes_obi_check
        
        metrics = {
            "pair": self.pair,
            "spread_compression": spread_pct,
            "obi_score": obi,
            "bid_dominance_pct": bid_dominance_pct,
            "orderbook": orderbook,
        }
        
        if both_pass:
            print(f"   🎯 [COIL MATCH] {self.pair} satisfies parameters!")
            print(f"      Spread: {spread_pct:.4f}% | Bid Dominance: {bid_dominance_pct:.1f}%")
            print(f"   ✅ Forwarding to Tier 2 Execution Brain...")
        else:
            print(f"   💤 [LOOSE STRUCTURE] {self.pair} (Spread: {spread_pct:.3f}%, OBI: {obi:.2f}). Skipping.")
        
        return both_pass, metrics


# ============================================================================
# TIER 2: GENERATIVE INTELLIGENCE (The Execution Brain)
# ============================================================================

TIER2_SYSTEM_INSTRUCTION = """
You are the Execution Brain of Titan Predator v4.0 - Phase 2 Institutional Gateway.
Your role is stripped of basic arithmetic. You focus EXCLUSIVELY on high-level institutional pattern evaluation.

INPUTS FROM TIER 1:
- Spread Compression: < 0.09% ✅
- Order Book Imbalance: > +0.30 (>65% bid dominance) ✅

YOUR CRITICAL EVALUATIONS:
1. TITAN DIRECTIVE: Titan DOES NOT trade breakout patterns. Focus exclusively on VALUE COMPRESSION and LIQUIDITY SPRINGS.
2. SPOOFING DETECTION: Verify if the buy wall represents high-conviction passive buying or fleeting algorithmic noise.
3. LIQUIDITY SWEEP VALIDATION: Ensure this coil is a true liquidity spring indicating imminent upward expansion from accumulated value.

OUTPUT REQUIREMENT:
Respond ONLY with valid JSON. No markdown, no prose.
If institutional markers are weak, recommend HOLD to protect capital.

Expected JSON Schema:
{
    "action": "BUY" | "HOLD",
    "confidence": 0.0-1.0,
    "rationale": "Brief structural reasoning focusing on value compression.",
    "volume": 10
}
"""

class Tier2ExecutionBrain:
    def __init__(self):
        self.model = "gemini-2.5-pro"
    
    def analyze_institutional_patterns(self, tier1_metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pair = tier1_metrics.get("pair", "UNKNOWN")
        analysis_prompt = f"""
TIER 1 QUANTITATIVE VALIDATION PASSED FOR {pair}:
- Spread Compression: {tier1_metrics['spread_compression']:.4f}%
- Order Book Imbalance (OBI): {tier1_metrics['obi_score']:.4f}
- Bid Dominance: {tier1_metrics['bid_dominance_pct']:.1f}%

Live Order Book (top 10 tiers):
{json.dumps(tier1_metrics['orderbook'], indent=2)}

Evaluate this structure for authentic value compression and liquidity spring mechanics.
Respond ONLY in JSON.
"""
        try:
            print(f"   📡 Querying {self.model} for pattern analysis...")
            response = client.models.generate_content(
                model=self.model,
                contents=analysis_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=TIER2_SYSTEM_INSTRUCTION,
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )
            
            decision = json.loads(response.text.strip())
            print(f"   🧠 Brain Output: {decision.get('rationale')}")
            return decision
            
        except Exception as e:
            print(f"   ❌ Gemini analysis error: {e}")
            return None


# ============================================================================
# EXECUTION ROUTING
# ============================================================================

def execute_kraken_paper_order(decision: Dict[str, Any], pair: str) -> bool:
    action = decision.get("action", "HOLD")
    if action == "HOLD":
        print(f"   ⏸️  Decision: HOLD. Capital protected.")
        return False
    
    volume = decision.get("volume", 10)
    
    try:
        print(f"   ⚡ TITAN BUY TRIGGER ACTIVE! Routing paper order for {volume} {pair}...")
        cmd = ["kraken", "paper", "order", "buy", pair, "market", str(volume)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"   ✅ KRAKEN CONFIRMATION: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ KRAKEN ERROR: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"   ❌ Execution error: {e}")
        return False


# ============================================================================
# MAIN EXECUTION LOOP
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 TITAN PREDATOR v4.0 - HYBRID MULTI-ASSET ENGAGE")
    print("=" * 70)
    print(f"Architecture: Two-Tier Institutional Gateway")
    print(f"Target Basket: {', '.join(TARGET_PAIRS)}")
    print("=" * 70)
    
    tier2 = Tier2ExecutionBrain()
    cycle_count = 0
    trades_executed = 0
    tier1_signals = 0
    
    try:
        while True:
            cycle_count += 1
            print(f"\n🔄 --- GLOBAL BASKET SCAN CYCLE #{cycle_count} ---")
            
            for current_pair in TARGET_PAIRS:
                tier1 = Tier1Gatekeeper(pair=current_pair)
                tier1_passes, tier1_metrics = tier1.execute_tier1_validation()
                
                if tier1_passes:
                    tier1_signals += 1
                    decision = tier2.analyze_institutional_patterns(tier1_metrics)
                    
                    if decision:
                        success = execute_kraken_paper_order(decision, current_pair)
                        if success:
                            trades_executed += 1
                
                time.sleep(2)  # 2-second breath between API calls
            
            print("\n" + "=" * 70)
            print("SESSION SUMMARY:")
            print(f" • Total Cycles: {cycle_count}")
            print(f" • Tier 1 Matches (🎯 COIL MATCH): {tier1_signals}")
            print(f" • Trades Executed: {trades_executed}")
            print("======================================================================")
            print("⏰ Next global scan in 60 seconds...")
            time.sleep(60)
            
    except KeyboardInterrupt:
        print(f"\n\n⏹️ TITAN ENGINE SHUTDOWN SEQUENCED BY USER.")
