"""
Titan Predator v4.0 - Autonomous Quantitative Trading Agent
Integrates Kraken MCP with Gemini 3.1 Pro for institutional-grade execution decisions
"""

import os
import json
import subprocess
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
  "entry_price": "target_limit_price_or_null",
  "stop_loss": "calculated_stop_loss_or_null",
  "take_profit": "calculated_target_or_null",
  "volume": "calculated_order_size_or_null",
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
            print(f"Orderbook fetch failed: {orderbook_result.stderr}")
            return None
        
        orderbook = json.loads(orderbook_result.stdout)
        
        ticker_result = subprocess.run(
            ["kraken", "ticker", pair, "-o", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if ticker_result.returncode != 0:
            print(f"Ticker fetch failed: {ticker_result.stderr}")
            return None
        
        ticker = json.loads(ticker_result.stdout)
        
        market_data = {
            "pair": pair,
            "orderbook": orderbook,
            "ticker": ticker
        }
        
        return market_data
        
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return None

def run_titan_hunter():
    """Main Titan Predator v4.0 execution loop"""
    print("\n" + "=" * 70)
    print("TITAN PREDATOR v4.0 - AUTONOMOUS QUANTITATIVE HUNTER INITIATED")
    print("=" * 70)
    
    print("\nScanning market structure for institutional opportunities...")
    
    # Step A: Ingest market data
    market_data = get_kraken_market_data("ONDOUSD")
    if not market_data:
        print("Skipping iteration: Market data ingestion failed.")
        return
    
    print("Market data retrieved successfully")
    
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
        
        print(f"\n[TITAN v4.0 EVALUATION RESULT]:")
        print(json.dumps(decision, indent=2))
        
        if decision.get("action") == "BUY":
            print(f"\n⚡ TITAN BUY SIGNAL DETECTED")
            print(f"Confidence: {decision.get('confidence', 0):.0%}")
            print(f"Entry: {decision.get('entry_price')}")
            print(f"Stop Loss: {decision.get('stop_loss')}")
            print(f"Take Profit: {decision.get('take_profit')}")
            
        elif decision.get("action") == "SELL":
            print(f"\n⚡ TITAN SELL SIGNAL DETECTED")
            print(f"Confidence: {decision.get('confidence', 0):.0%}")
            
        else:
            print(f"\n⏸️  Holding: Market conditions do not meet Titan entry criteria")
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
    except Exception as e:
        print(f"Error during Titan evaluation: {e}")
    
    print("\n" + "=" * 70)
    print("TITAN PREDATOR v4.0 CYCLE COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    run_titan_hunter()
