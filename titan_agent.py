"""
Titan Predator v4.0 - Autonomous Quantitative Trading Agent
Integrates Kraken MCP with Gemini 3.1 Pro for institutional-grade execution decisions
With Full Execution Routing to Kraken Paper Trading Engine
"""

import os
import json
import subprocess
import time
from datetime import datetime
from google import genai
from google.genai import types

# 1. Initialize the Google GenAI Client
client = genai.Client()

# 2. Define the Institutional-Grade Titan Predator v4.0 Brain
TITAN_SYSTEM_INSTRUCTION = """
You are an autonomous, institutional-grade quantitative trading agent operating the Titan Predator v4.0 framework.
Your sole function is to evaluate real-time market microstructure data and make execution decisions.

CORE PROTOCOL PARAMETERS:
- You HUNT exclusively for Value Compression and Liquidity Springs.
- You NEVER trade generic breakout patterns.
- You analyze order book spreads, Hurst Exponent trend states, and directional flows.

VALUE COMPRESSION DETECTION:
- Bid-ask spread compression: < 0.05% indicates tight structural value accumulation
- Order book imbalance: > 1.8x ratio between best bid/ask volume signals pressure
- Cumulative delta flow: Directional volume > 65% threshold indicates institutional accumulation

LIQUIDITY SPRING TRIGGERS:
- Order book depth collapse on one side with counter-directional micro-flows
- Hurst Exponent > 0.6 (trending) + spread compression = institutional entry
- Volume profile showing hidden sweeps through key levels

CRITICAL RISK & EXECUTION RULES:
1. You operate strictly on mathematical logic. 
2. If conditions are met, you issue clear execution instructions.
3. You must ONLY respond with a valid JSON object. Do not include regular prose, conversational introductions, or markdown formatting outside the JSON block.
4. POSITION SIZING: Keep volume scaled to 0.5-2.0 units for paper trading validation
5. CONFIDENCE THRESHOLDS: Only trigger on > 0.75 signal strength
6. STOP LOSS: Always set 1.5-2.0% below entry for BUY, above entry for SELL

Expected Output JSON Schema:
{
  "action": "BUY" | "SELL" | "HOLD",
  "pair": "ONDOUSD",
  "confidence": 0.0-1.0,
  "signal_type": "value_compression" | "liquidity_spring" | "none",
  "order_type": "limit" | "market" | null,
  "price": "target_limit_price_or_null",
  "volume": "calculated_order_size_or_null",
  "stop_loss": "calculated_stop_loss_or_null",
  "take_profit": "calculated_target_or_null",
  "rationale": "Brief structural reason",
  "risk_reward_ratio": "calculated_ratio_or_null"
}
"""

def get_kraken_market_data(pair="ONDOUSD"):
    """Fetch real-time order book and market structure state"""
    try:
        orderbook_result = subprocess.run(
            ["kraken", "orderbook", pair, "--depth", "20", "-o", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if orderbook_result.returncode != 0:
            print(f"   ⚠️  Orderbook fetch failed: {orderbook_result.stderr}")
            return None
        
        orderbook = json.loads(orderbook_result.stdout)
        
        ticker_result = subprocess.run(
            ["kraken", "ticker", pair, "-o", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if ticker_result.returncode != 0:
            print(f"   ⚠️  Ticker fetch failed: {ticker_result.stderr}")
            return None
        
        ticker = json.loads(ticker_result.stdout)
        
        market_data = {
            "pair": pair,
            "orderbook": orderbook,
            "ticker": ticker
        }
        
        return market_data
        
    except Exception as e:
        print(f"   ❌ Error fetching market data: {e}")
        return None

def execute_kraken_order(decision):
    """
    Route execution decision to Kraken Paper Trading Engine
    Translates Titan JSON decision into Kraken CLI commands
    """
    action = decision.get("action", "HOLD")
    
    if action == "HOLD":
        print(f"   ⏸️  Holding: Market conditions do not meet Titan entry criteria. Standby.")
        return None
    
    pair = decision.get("pair", "ONDOUSD")
    volume = decision.get("volume")
    price = decision.get("price")
    order_type = decision.get("order_type", "market")
    confidence = decision.get("confidence", 0)
    
    if volume is None or volume == 0:
        print(f"   ⚠️  Invalid volume. Order not executed.")
        return None
    
    try:
        if action == "BUY":
            print(f"\n   ⚡ TITAN BUY TRIGGER ACTIVE!")
            print(f"      Confidence: {confidence:.0%}")
            print(f"      Routing to Kraken Paper Trading Engine...")
            print(f"      Order Type: {order_type}")
            print(f"      Volume: {volume}")
            
            # Construct Kraken CLI command for buy order
            if order_type == "limit" and price:
                cmd = ["kraken", "paper", "order", "buy", pair, "limit", str(volume), str(price)]
                print(f"      Price (Limit): {price}")
            else:
                cmd = ["kraken", "paper", "order", "buy", pair, "market", str(volume)]
            
            # Execute the paper trade
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
            print(f"      Routing to Kraken Paper Trading Engine...")
            print(f"      Volume: {volume}")
            
            # Construct Kraken CLI command for sell order
            if order_type == "limit" and price:
                cmd = ["kraken", "paper", "order", "sell", pair, "limit", str(volume), str(price)]
                print(f"      Price (Limit): {price}")
            else:
                cmd = ["kraken", "paper", "order", "sell", pair, "market", str(volume)]
            
            # Execute the paper trade
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

def run_titan_hunter(single_shot=False):
    """
    Main Titan Predator v4.0 execution cycle
    
    Args:
        single_shot: If True, run once. If False, run continuous loop.
    """
    
    if single_shot:
        print("\n" + "=" * 70)
        print("TITAN PREDATOR v4.0 - SINGLE CYCLE EXECUTION")
        print("=" * 70)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    else:
        print("\n" + "=" * 70)
        print("TITAN PREDATOR v4.0 - AUTONOMOUS HUNTER INITIATED")
        print("=" * 70)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("Monitoring Mode: Continuous (every 30 seconds)")
        print("=" * 70)
    
    cycle_count = 0
    trades_executed = 0
    
    try:
        while True:
            cycle_count += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            print(f"\n[{timestamp}] Monitoring Cycle #{cycle_count}")
            print("-" * 70)
            
            # Step A: Ingest market data
            print("   📊 Fetching market microstructure...")
            market_data = get_kraken_market_data("ONDOUSD")
            
            if not market_data:
                print("   ⏭️  Skipping cycle: Market data ingestion failed.")
                if single_shot:
                    break
                time.sleep(30)
                continue
            
            print("   ✅ Market data retrieved")
            
            # Step B: Package data for Gemini
            prompt = f"""
INSTITUTIONAL MARKET ANALYSIS REQUEST - TITAN PREDATOR v4.0

Real-Time Market Microstructure Data:
{json.dumps(market_data, indent=2)}

Analyze this market structure for VALUE COMPRESSION or LIQUIDITY SPRING conditions.

Decision Criteria:
1. VALUE COMPRESSION: Spread compression + Bid Dominance > 65% = Structural accumulation
2. LIQUIDITY SPRING: Order book depth collapse + Volume imbalance > 1.8x = Spring setup
3. HOLD: Maintain until clear institutional microstructure trigger emerges

If conditions are met, issue a precise execution signal.
Otherwise, remain on HOLD.

Output ONLY valid JSON with no additional text.
"""

            try:
                print("   🧠 Gemini analyzing market structure...")
                response = client.models.generate_content(
                    model='gemini-3.1-pro',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=TITAN_SYSTEM_INSTRUCTION,
                        temperature=0.1,
                        max_output_tokens=1024,
                        response_mime_type="application/json"
                    )
                )
                
                # Parse response
                decision_text = response.text.strip()
                
                if decision_text.startswith("```json"):
                    decision_text = decision_text[7:]
                if decision_text.endswith("```"):
                    decision_text = decision_text[:-3]
                
                decision = json.loads(decision_text)
                
                print(f"\n   [TITAN v4.0 EVALUATION RESULT]:")
                print(json.dumps(decision, indent=6))
                
                # Step C: Route to Kraken Paper Execution Engine
                execution_result = execute_kraken_order(decision)
                
                if execution_result and execution_result.get("status") == "success":
                    trades_executed += 1
                    print(f"\n   📈 Trades Executed This Session: {trades_executed}")
                
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON parsing error: {e}")
            except Exception as e:
                print(f"   ❌ Gemini analysis error: {e}")
            
            # Exit if single-shot mode
            if single_shot:
                break
            
            # Wait before next cycle
            print(f"\n   ⏰ Next scan in 30 seconds...")
            time.sleep(30)
    
    except KeyboardInterrupt:
        print(f"\n\n⏹️  TITAN HUNTER INTERRUPTED BY USER")
    
    finally:
        print("\n" + "=" * 70)
        print("TITAN PREDATOR v4.0 SESSION COMPLETE")
        print("=" * 70)
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"Total Cycles: {cycle_count}")
        print(f"Trades Executed: {trades_executed}")
        print("=" * 70)

if __name__ == "__main__":
    import sys
    
    # Command line options:
    # python3 titan_agent.py           (single cycle)
    # python3 titan_agent.py loop      (continuous monitoring)
    # python3 titan_agent.py loop 60   (continuous for 60 seconds then exit)
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "single"
    
    if mode == "loop":
        print("\n🔄 Starting Continuous Monitoring Loop...")
        run_titan_hunter(single_shot=False)
    else:
        print("\n📌 Running Single Cycle Analysis...")
        run_titan_hunter(single_shot=True)
