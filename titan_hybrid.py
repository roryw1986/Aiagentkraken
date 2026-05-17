"""
Titan Predator v4.0 - Phase 2 Architecture
Two-Tier Institutional Gateway for Autonomous Quantitative Trading
================================================================================
TIER 1: Local Quantitative Pre-Compute (The Gatekeeper)
    - Runs every 60 seconds on cloud server
    - Processes top 10 depth tiers of live Kraken Pro order book
    - Validates strict structural compression thresholds
    - Protects API limits and keeps logs clean

TIER 2: Generative Intelligence (The Execution Brain)
    - Gemini 2.5 Pro analyzes pre-filtered signals
    - Verifies spoofing vs. true accumulation
    - Validates liquidity sweep conditions
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

# ============================================================================
# TIER 1: LOCAL QUANTITATIVE PRE-COMPUTE (The Gatekeeper)
# ============================================================================

class Tier1Gatekeeper:
    """
    Local quantitative analysis running on cloud server every 60 seconds.
    Processes order book to validate strict structural compression.
    """
    
    def __init__(self):
        self.pair = "ONDOUSD"
        self.depth_tiers = 10
        self.spread_compression_threshold = 0.0009  # 0.09%
        self.obi_threshold = 0.30  # +0.30 OBI (>65% bid dominance)
    
    def fetch_orderbook_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Fetch live Kraken Pro order book at specified depth.
        Returns: Raw order book data or None if fetch fails
        """
        try:
            result = subprocess.run(
                ["kraken", "orderbook", self.pair, "--depth", str(self.depth_tiers), "-o", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"   ⚠️  Order book fetch failed: {result.stderr}")
                return None
            
            return json.loads(result.stdout)
        
        except Exception as e:
            print(f"   ❌ Error fetching order book: {e}")
            return None
    
    def calculate_spread_compression(self, orderbook: Dict[str, Any]) -> Optional[float]:
        """
        CRITERION 1: The Coiled Spring Spread Compression
        
        Measures absolute tightness of market maker's spread relative to asset's price.
        When institutional players match massive blocks, spread pinches to razor-thin margin.
        
        Formula: (ask_price - bid_price) / mid_price
        Threshold: < 0.09% (0.0009)
        
        Returns: Spread percentage or None if calculation fails
        """
        try:
            # Extract best bid and ask from orderbook top tier
            bids = orderbook.get("bids", [])
            asks = orderbook.get("asks", [])
            
            if not bids or not asks:
                print("   ⚠️  Incomplete order book data (missing bids or asks)")
                return None
            
            best_bid_price = float(bids[0][0])
            best_ask_price = float(asks[0][0])
            mid_price = (best_bid_price + best_ask_price) / 2
            
            # Calculate spread as percentage of mid price
            spread_compression = (best_ask_price - best_bid_price) / mid_price
            
            return spread_compression
        
        except (KeyError, IndexError, ValueError, TypeError) as e:
            print(f"   ❌ Spread compression calculation error: {e}")
            return None
    
    def calculate_order_book_imbalance(self, orderbook: Dict[str, Any]) -> Optional[float]:
        """
        CRITERION 2: Deep Order Book Imbalance (OBI)
        
        Evaluates net buying vs selling pressure across top 10 micro-price horizons.
        Looks past immediate top bid to detect institutional "buy wall" supporting price.
        
        Formula: (sum(bid_volumes) - sum(ask_volumes)) / (sum(bid_volumes) + sum(ask_volumes))
        Threshold: > +0.30 (>65% absolute bid dominance)
        Range: -1.0 (pure sell-side) to +1.0 (pure buy-side)
        
        Returns: OBI score (-1.0 to 1.0) or None if calculation fails
        """
        try:
            bids = orderbook.get("bids", [])
            asks = orderbook.get("asks", [])
            
            if not bids or not asks:
                print("   ⚠️  Incomplete order book data (missing bids or asks)")
                return None
            
            # Aggregate volumes across top 10 tiers
            bid_volume = sum(float(bid[1]) for bid in bids[:self.depth_tiers])
            ask_volume = sum(float(ask[1]) for ask in asks[:self.depth_tiers])
            
            total_volume = bid_volume + ask_volume
            
            if total_volume == 0:
                print("   ⚠️  Zero total volume detected")
                return None
            
            # Calculate OBI: ranges from -1.0 to +1.0
            obi = (bid_volume - ask_volume) / total_volume
            
            return obi
        
        except (KeyError, IndexError, ValueError, TypeError) as e:
            print(f"   ❌ OBI calculation error: {e}")
            return None
    
    def execute_tier1_validation(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Execute Tier 1 quantitative gatekeeper analysis.
        
        Returns: 
            - Tuple of (passes_both_criteria: bool, metrics: Dict)
            - If both criteria pass: forward to Tier 2 (Gemini)
            - If either fails: safely skip asset, protect API limits
        """
        print(f"\n{'='*70}")
        print(f"🎯 TIER 1: LOCAL QUANTITATIVE PRE-COMPUTE (The Gatekeeper)")
        print(f"{'='*70}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"Pair: {self.pair}")
        print(f"Depth Tiers: {self.depth_tiers}")
        
        # Fetch order book
        print("\n   📊 Fetching live order book snapshot...")
        orderbook = self.fetch_orderbook_snapshot()
        
        if not orderbook:
            print("   ⏭️  [GATE REJECTED] Failed to fetch order book")
            return False, {"status": "orderbook_fetch_failed"}
        
        print("   ✅ Order book retrieved")
        
        # Calculate Criterion 1: Spread Compression
        print("\n   📐 Criterion 1: Coiled Spring Spread Compression")
        spread = self.calculate_spread_compression(orderbook)
        
        if spread is None:
            print(f"   ⏭️  [GATE REJECTED] Spread calculation failed")
            return False, {"status": "spread_calc_failed"}
        
        spread_pct = spread * 100
        passes_spread_check = spread < self.spread_compression_threshold
        
        print(f"      Spread: {spread_pct:.4f}%")
        print(f"      Threshold: {self.spread_compression_threshold*100:.2f}%")
        print(f"      Status: {'✅ PASS' if passes_spread_check else '❌ FAIL (Fragmented/Illiquid Book)'}")
        
        # Calculate Criterion 2: Order Book Imbalance
        print("\n   📊 Criterion 2: Deep Order Book Imbalance (OBI)")
        obi = self.calculate_order_book_imbalance(orderbook)
        
        if obi is None:
            print(f"   ⏭️  [GATE REJECTED] OBI calculation failed")
            return False, {"status": "obi_calc_failed"}
        
        bid_dominance_pct = ((obi + 1) / 2) * 100  # Convert to 0-100% scale
        passes_obi_check = obi > self.obi_threshold
        
        print(f"      OBI Score: {obi:.4f}")
        print(f"      Bid Dominance: {bid_dominance_pct:.1f}%")
        print(f"      Threshold: {self.obi_threshold} (>65% bid dominance)")
        print(f"      Status: {'✅ PASS' if passes_obi_check else '❌ FAIL (No Institutional Wall)'}")
        
        # Final Gate Decision
        both_pass = passes_spread_check and passes_obi_check
        
        metrics = {
            "spread_compression": spread_pct,
            "spread_check_pass": passes_spread_check,
            "obi_score": obi,
            "bid_dominance_pct": bid_dominance_pct,
            "obi_check_pass": passes_obi_check,
            "orderbook": orderbook,
            "gate_decision": "COIL_MATCH ✅" if both_pass else "LOOSE_MARKET_STRUCTURE 💤"
        }
        
        print("\n" + "-" * 70)
        if both_pass:
            print(f"   🎯 [COIL MATCH] Both criteria satisfied!")
            print(f"   ✅ Forwarding to Tier 2: Gemini 2.5 Pro for decision...")
        else:
            print(f"   💤 [LOOSE MARKET STRUCTURE] Institutional setup not detected")
            print(f"   ⏭️  Safely skipping asset to protect API limits")
        
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

YOUR THREE CRITICAL EVALUATIONS:

1. SPOOFING DETECTION vs. TRUE ACCUMULATION
   - Algorithmic market makers flash large artificial walls to trap retail shorts
   - Analyze relationship between compressed spread and OBI density
   - Verify if wall represents high-conviction passive buying or fleeting algorithmic noise
   - Red Flags: Sudden wall disappearance, zero volume beneath wall, flash orders

2. LIQUIDITY SWEEP VALIDATION
   - Look at mid-price context against compressed spread parameters
   - Identify if current coil = TRUE "liquidity spring" (before sharp upward expansion)
   - Detect FALSE breakout patterns that risk capital slippage
   - Check: Is bid wall stacked ACROSS multiple price levels (institutional) or concentrated in one level (retail)?

3. EXECUTION CONFIRMATION
   - If structural footprints look authentic, return definitive execution signal
   - Determine appropriate position sizing for paper trading
   - Calculate stop loss (1.5-2.0% below entry) and take profit levels

OUTPUT REQUIREMENT:
Respond ONLY with valid JSON. No markdown, no prose, no explanations outside JSON.
If conditions warrant a BUY, structure must be institutional-grade (not retail noise).
If institutional markers are weak, recommend HOLD until clearer setup emerges.

Expected JSON Schema:
{
    "action": "BUY" | "HOLD" | "SELL",
    "confidence": 0.0-1.0,
    "rationale": "High-density bid wall confirming absorption at strict structural compression limit.",
    "spoofing_risk": "low" | "medium" | "high",
    "liquidity_spring": true | false,
    "entry_price": price_or_null,
    "volume": size_or_null,
    "stop_loss": price_or_null,
    "take_profit": price_or_null
}
"""


class Tier2ExecutionBrain:
    """
    Gemini 2.5 Pro analyzes pre-filtered Tier 1 signals.
    Strips away arithmetic, focuses on institutional pattern validation.
    """
    
    def __init__(self):
        self.pair = "ONDOUSD"
        self.model = "gemini-2.5-pro"
    
    def analyze_institutional_patterns(self, tier1_metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send Tier 1 metrics to Gemini 2.5 Pro for high-level institutional analysis.
        
        Args:
            tier1_metrics: Dictionary containing spread, OBI, and orderbook data from Tier 1
        
        Returns:
            JSON decision object or None if analysis fails
        """
        print(f"\n{'='*70}")
        print(f"🧠 TIER 2: GENERATIVE INTELLIGENCE (The Execution Brain)")
        print(f"{'='*70}")
        print(f"Model: {self.model}")
        print(f"Analysis Type: Institutional Pattern Validation")
        
        # Package Tier 1 data for Gemini
        analysis_prompt = f"""
TIER 1 QUANTITATIVE VALIDATION (PASSED):
- Spread Compression: {tier1_metrics['spread_compression']:.4f}% (threshold: 0.09%)
- Order Book Imbalance (OBI): {tier1_metrics['obi_score']:.4f}
- Bid Dominance: {tier1_metrics['bid_dominance_pct']:.1f}%
- Live Order Book (top 10 tiers):
{json.dumps(tier1_metrics['orderbook'], indent=2)}

ANALYSIS REQUEST:
Evaluate this market structure for institutional accumulation patterns.

1. SPOOFING CHECK: Is this a real institutional buy wall or algorithmic spoofing?
2. LIQUIDITY SPRING: Does this setup suggest imminent upward price expansion?
3. EXECUTION: Should Titan execute a BUY at current levels?

Respond ONLY with valid JSON. No markdown, no explanations outside the JSON block.
"""
        
        try:
            print(f"\n   📡 Sending to {self.model} for pattern analysis...")
            
            response = client.models.generate_content(
                model=self.model,
                contents=analysis_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=TIER2_SYSTEM_INSTRUCTION,
                    temperature=0.2,  # Low temperature for deterministic analysis
                    max_output_tokens=1024,
                    response_mime_type="application/json"
                )
            )
            
            # Parse response
            decision_text = response.text.strip()
            
            # Clean up markdown if present
            if decision_text.startswith("```json"):
                decision_text = decision_text[7:]
            if decision_text.endswith("```"):
                decision_text = decision_text[:-3]
            
            decision = json.loads(decision_text)
            
            print(f"   ✅ Gemini analysis complete")
            print(f"\n   [EXECUTION DECISION]:")
            print(json.dumps(decision, indent=6))
            
            return decision
        
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parsing error: {e}")
            return None
        except Exception as e:
            print(f"   ❌ Gemini analysis error: {e}")
            return None
    
    def validate_execution_signal(self, decision: Dict[str, Any]) -> bool:
        """
        Final safety validation before execution routing.
        
        Returns: True if decision passes all safety checks, False otherwise
        """
        # Confidence threshold
        confidence = decision.get("confidence", 0)
        if confidence < 0.75:
            print(f"   ⚠️  Confidence {confidence:.0%} below threshold 75%")
            return False
        
        # Action validation
        action = decision.get("action", "HOLD")
        if action not in ["BUY", "SELL", "HOLD"]:
            print(f"   ⚠️  Invalid action: {action}")
            return False
        
        # Position sizing validation
        if action in ["BUY", "SELL"]:
            volume = decision.get("volume")
            if not volume or volume <= 0:
                print(f"   ⚠️  Invalid volume: {volume}")
                return False
        
        return True


# ============================================================================
# EXECUTION ROUTING
# ============================================================================

def execute_kraken_paper_order(decision: Dict[str, Any], pair: str = "ONDOUSD") -> Optional[Dict[str, Any]]:
    """
    Route execution decision to Kraken Paper Trading Engine.
    Translates Titan JSON into Kraken CLI commands.
    """
    action = decision.get("action", "HOLD")
    
    if action == "HOLD":
        print(f"\n   ⏸️  Holding: Market conditions do not meet Titan criteria. Standby.")
        return None
    
    volume = decision.get("volume")
    price = decision.get("entry_price")
    confidence = decision.get("confidence", 0)
    
    if volume is None or volume <= 0:
        print(f"   ⚠️  Invalid volume. Order not executed.")
        return None
    
    try:
        if action == "BUY":
            print(f"\n   ⚡ TITAN BUY TRIGGER ACTIVE!")
            print(f"      Confidence: {confidence:.0%}")
            print(f"      Volume: {volume} units")
            print(f"      Routing to Kraken Paper Trading Engine...")
            
            # Construct Kraken CLI command
            cmd = ["kraken", "paper", "order", "buy", pair, "market", str(volume)]
            
            # Execute paper trade
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"   ✅ KRAKEN PAPER CONFIRMATION:")
                print(f"      {result.stdout}")
                return {"status": "success", "action": "BUY", "output": result.stdout}
            else:
                print(f"   ❌ KRAKEN ERROR: {result.stderr}")
                return {"status": "error", "action": "BUY", "error": result.stderr}
        
        elif action == "SELL":
            print(f"\n   🔥 TITAN SELL TRIGGER ACTIVE!")
            print(f"      Confidence: {confidence:.0%}")
            print(f"      Volume: {volume} units")
            print(f"      Routing to Kraken Paper Trading Engine...")
            
            cmd = ["kraken", "paper", "order", "sell", pair, "market", str(volume)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"   ✅ KRAKEN PAPER CONFIRMATION:")
                print(f"      {result.stdout}")
                return {"status": "success", "action": "SELL", "output": result.stdout}
            else:
                print(f"   ❌ KRAKEN ERROR: {result.stderr}")
                return {"status": "error", "action": "SELL", "error": result.stderr}
    
    except subprocess.TimeoutExpired:
        print(f"   ⚠️  Kraken command timeout")
        return {"status": "timeout", "action": action}
    except Exception as e:
        print(f"   ❌ Execution error: {e}")
        return {"status": "error", "action": action, "error": str(e)}


# ============================================================================
# MAIN EXECUTION LOOP
# ============================================================================

def run_titan_phase2_hybrid(loop_duration_seconds: int = 300, check_interval: int = 60):
    """
    Main Titan Predator v4.0 Phase 2 execution cycle.
    
    Two-tier institutional gateway architecture:
    - Tier 1: Local quantitative validation every 60 seconds
    - Tier 2: Gemini pattern analysis on validated signals
    
    Args:
        loop_duration_seconds: Total runtime (default 5 minutes)
        check_interval: Seconds between Tier 1 validation runs (default 60)
    """
    
    print("\n" + "=" * 70)
    print("🚀 TITAN PREDATOR v4.0 - PHASE 2 HYBRID ARCHITECTURE ACTIVE")
    print("=" * 70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Architecture: Two-Tier Institutional Gateway")
    print(f"Tier 1: Local Quantitative Pre-Compute (every {check_interval}s)")
    print(f"Tier 2: Gemini 2.5 Pro Pattern Analysis")
    print(f"Duration: {loop_duration_seconds}s | Check Interval: {check_interval}s")
    print("=" * 70)
    
    tier1 = Tier1Gatekeeper()
    tier2 = Tier2ExecutionBrain()
    
    cycle_count = 0
    trades_executed = 0
    tier1_signals = 0
    start_time = time.time()
    
    try:
        while time.time() - start_time < loop_duration_seconds:
            cycle_count += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            print(f"\n[{timestamp}] Monitoring Cycle #{cycle_count}")
            print("-" * 70)
            
            # TIER 1: Local Quantitative Validation
            tier1_passes, tier1_metrics = tier1.execute_tier1_validation()
            
            # TIER 2: Conditional Gemini Analysis
            if tier1_passes:
                tier1_signals += 1
                decision = tier2.analyze_institutional_patterns(tier1_metrics)
                
                if decision and tier2.validate_execution_signal(decision):
                    # Route to Kraken Paper Trading
                    execution_result = execute_kraken_paper_order(decision)
                    
                    if execution_result and execution_result.get("status") == "success":
                        trades_executed += 1
                        print(f"\n   📈 Trades Executed This Session: {trades_executed}")
            else:
                print(f"\n   💤 Loose Market Structure - Tier 2 analysis skipped")
            
            # Wait before next cycle
            remaining_duration = loop_duration_seconds - (time.time() - start_time)
            if remaining_duration > 0:
                sleep_duration = min(check_interval, remaining_duration)
                print(f"\n   ⏰ Next Tier 1 scan in {int(sleep_duration)} seconds...")
                time.sleep(sleep_duration)
    
    except KeyboardInterrupt:
        print(f"\n\n⏹️  TITAN PHASE 2 HYBRID INTERRUPTED BY USER")
    
    finally:
        print("\n" + "=" * 70)
        print("✅ TITAN PREDATOR v4.0 - PHASE 2 SESSION COMPLETE")
        print("=" * 70)
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"\nSESSION SUMMARY:")
        print(f"  • Total Cycles: {cycle_count}")
        print(f"  • Tier 1 Matches (🎯 COIL MATCH): {tier1_signals}")
        print(f"  • Tier 2 Analyses: {tier1_signals}")
        print(f"  • Trades Executed: {trades_executed}")
        print(f"  • Architecture: Two-Tier Institutional Gateway ✅")
        print("=" * 70)


if __name__ == "__main__":
    import sys
    
    # Command line options:
    # python3 titan_hybrid.py                (5 min test)
    # python3 titan_hybrid.py loop           (continuous)
    # python3 titan_hybrid.py 600 60         (duration_seconds check_interval)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "loop":
            # Continuous mode with keyboard interrupt
            run_titan_phase2_hybrid(loop_duration_seconds=3600, check_interval=60)
        else:
            # Custom duration and interval
            duration = int(sys.argv[1]) if len(sys.argv) > 1 else 300
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            run_titan_phase2_hybrid(loop_duration_seconds=duration, check_interval=interval)
    else:
        # Default: 5 minute test
        run_titan_phase2_hybrid(loop_duration_seconds=300, check_interval=60)
