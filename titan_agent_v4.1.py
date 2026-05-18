"""
Titan Predator v4.1 - Dual-Protocol Autonomous Trading Agent
Integrates Kraken MCP with Gemini 3.1 Pro for institutional-grade execution
PRIMARY PROTOCOL: Microstructure hunting (value compression + liquidity springs)
SECONDARY PROTOCOL: Funding rate anomaly detection + arbitrage capital signaling
"""

import os
import json
import subprocess
import time
from datetime import datetime
from google import genai
from google.genai import types

# Initialize Google GenAI Client
client = genai.Client()

# Titan v4.1 System Instruction (Dual-Protocol)
TITAN_V4_1_SYSTEM_INSTRUCTION = """
You are Titan Predator v4.1 - an autonomous, institutional-grade quantitative trading agent.
You operate TWO COORDINATED PROTOCOLS:

PROTOCOL 1: MICROSTRUCTURE HUNTING (PRIMARY)
- Hunt for Value Compression and Liquidity Springs on ONDOUSD
- Bid-ask spread < 0.05% + order book imbalance > 1.8x = entry signal
- Hurst Exponent > 0.6 + spread compression = institutional entry
- Volume profile hidden sweeps through key levels
- CONFIDENCE THRESHOLD: Only trigger on > 0.75 signal strength
- POSITION SIZING: 0.5-2.0 units for paper trading
- STOP LOSS: 1.5-2.0% below entry for BUY, above entry for SELL

PROTOCOL 2: ARBITRAGE CAPITAL ALLOCATION (SECONDARY)
- Monitor funding rates on BTC, ETH, SOL, LINK perpetuals
- Extreme funding = > 0.1% per 8-hour epoch
- When extreme funding + positive premium on ANY asset:
  * Calculate potential arbitrage yield (premium + funding - fees)
  * If yield > 50 bps: Signal ARBITRAGE_DIVERSION
  * Allocate 50-60% of capital to market-neutral arbitrage
  * Divert remaining capital to microstructure hunting

DUAL-PROTOCOL DECISION LOGIC:
1. Analyze ONDOUSD for microstructure opportunities
2. Check funding rates on 4 perpetuals for anomalies
3. If BOTH conditions met:
   - PRIMARY gets 40-50% capital
   - SECONDARY (arbitrage) gets 50-60% capital
4. If ONLY microstructure triggered:
   - Execute directional trade (100% capital available)
5. If ONLY funding anomaly triggered:
   - Execute arbitrage (market-neutral, no risk to directional positions)

CRITICAL EXECUTION RULES:
- Respond ONLY with valid JSON. No prose outside JSON.
- Calculate all parameters mathematically.
- Risk management is NON-NEGOTIABLE.
- Market-neutral positions (arbitrage) have ZERO directional liquidation risk.

Expected Output JSON Schema:
{
  "action": "BUY" | "SELL" | "HOLD" | "ARBITRAGE_DIVERSION",
  "protocol": "microstructure" | "arbitrage" | "neutral",
  "confidence": 0.0-1.0,
  "signal_type": "value_compression" | "liquidity_spring" | "funding_anomaly" | "none",
  "pair": "ONDOUSD" or affected pair,
  "order_type": "limit" | "market" | null,
  "price": "target_limit_price_or_null",
  "volume": "calculated_order_size_or_null",
  "stop_loss": "calculated_stop_loss_or_null",
  "take_profit": "calculated_target_or_null",
  "capital_allocation_pct": 0-100 for arbitrage,
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

def get_kraken_funding_rates():
    """Fetch funding rates for arbitrage pairs"""
    funding_data = {}
    pairs = ["BTCUSD", "ETHUSD", "SOLUSD", "LINKUSD"]
    
    for pair in pairs:
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
                funding_rate = data.get("fundingRate", 0)
                is_extreme = funding_rate > 0.001  # 0.1% per epoch
                
                funding_data[pair] = {
                    "funding_rate": funding_rate,
                    "is_extreme": is_extreme,
                    "annualized": funding_rate * 365 * 100  # Quick annualization
                }
        except Exception as e:
            print(f"   ⚠️  Funding rate fetch failed for {pair}: {e}")
    
    return funding_data

def execute_kraken_order(decision):
    """Route execution decision to Kraken Paper Trading Engine"""
    action = decision.get("action", "HOLD")
    
    if action == "HOLD":
        print(f"   ⏸️  Holding: Market conditions do not meet Titan entry criteria.")
        return None
    
    if action == "ARBITRAGE_DIVERSION":
        print(f"   🎯 ARBITRAGE DIVERSION SIGNAL!")
        print(f"      Capital Allocation: {decision.get('capital_allocation_pct', 0)}%")
        print(f"      Routing to ArbitrageManager for execution...")
        return {"status": "arbitrage_signal", "action": action}
    
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
            print(f"      Order Type: {order_type}")
            print(f"      Volume: {volume}")
            
            if order_type == "limit" and price:
                cmd = ["kraken", "paper", "order", "buy", pair, "limit", str(volume), str(price)]
                print(f"      Price (Limit): {price}")
            else:
                cmd = ["kraken", "paper", "order", "buy", pair, "market", str(volume)]
            
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
            print(f"      Volume: {volume}")
            
            if order_type == "limit" and price:
                cmd = ["kraken", "paper", "order", "sell", pair, "limit", str(volume), str(price)]
                print(f"      Price (Limit): {price}")
            else:
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

def run_titan_v4_1(single_shot=False):
    """Main Titan Predator v4.1 dual-protocol execution cycle"""
    
    if single_shot:
        print("\n" + "=" * 70)
        print("TITAN PREDATOR v4.1 - SINGLE CYCLE EXECUTION")
        print("=" * 70)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    else:
        print("\n" + "=" * 70)
        print("TITAN PREDATOR v4.1 - DUAL-PROTOCOL HUNTER INITIATED")
        print("=" * 70)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("Protocols: PRIMARY=Microstructure | SECONDARY=Arbitrage")
        print("Monitoring Mode: Continuous (every 30 seconds)")
        print("=" * 70)
    
    cycle_count = 0
    trades_executed = 0
    arbitrage_signals = 0
    
    try:
        while True:
            cycle_count += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            print(f"\n[{timestamp}] Monitoring Cycle #{cycle_count}")
            print("-" * 70)
            
            # PRIMARY PROTOCOL: Fetch microstructure
            print("   📊 PRIMARY PROTOCOL: Fetching microstructure...")
            market_data = get_kraken_market_data("ONDOUSD")
            
            if not market_data:
                print("   ⏭️  Skipping cycle: Market data ingestion failed.")
                if single_shot:
                    break
                time.sleep(30)
                continue
            
            print("   ✅ Market data retrieved")
            
            # SECONDARY PROTOCOL: Check funding rates
            print("   💰 SECONDARY PROTOCOL: Checking funding rates...")
            funding_rates = get_kraken_funding_rates()
            print("   ✅ Funding rates retrieved")
            
            # Package data for Gemini
            prompt = f"""
DUAL-PROTOCOL MARKET ANALYSIS REQUEST - TITAN PREDATOR v4.1

PRIMARY PROTOCOL - MICROSTRUCTURE DATA:
{json.dumps(market_data, indent=2)}

SECONDARY PROTOCOL - FUNDING RATE DATA:
{json.dumps(funding_rates, indent=2)}

Analyze both protocols simultaneously:

1. MICROSTRUCTURE ANALYSIS (ONDOUSD):
   - Check for Value Compression: Spread < 0.05% + Bid Dominance > 65%
   - Check for Liquidity Springs: Depth collapse + Volume imbalance > 1.8x
   - Calculate confidence threshold (> 0.75 to trigger)

2. ARBITRAGE ANALYSIS (Multi-Asset Funding):
   - Identify extreme funding rates (> 0.1% per epoch)
   - For each extreme, check if premium is positive
   - If both conditions met: Calculate arbitrage yield
   - If yield > 50 bps: Signal capital allocation to arbitrage

3. CAPITAL ALLOCATION LOGIC:
   - If BOTH conditions met: Allocate 50-60% to arbitrage, 40-50% to microstructure
   - If ONLY microstructure: Execute directional trade (100% capital)
   - If ONLY arbitrage: Signal capital diversion (market-neutral, no risk)

Evaluate and provide execution signal.
Output ONLY valid JSON with no additional text.
"""

            try:
                print("   🧠 Gemini analyzing dual protocols...")
                response = client.models.generate_content(
                    model='gemini-3.1-pro',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=TITAN_V4_1_SYSTEM_INSTRUCTION,
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
                
                print(f"\n   [TITAN v4.1 EVALUATION RESULT]:")
                print(json.dumps(decision, indent=6))
                
                # Execute decision
                execution_result = execute_kraken_order(decision)
                
                if execution_result:
                    if execution_result.get("status") == "success":
                        trades_executed += 1
                    elif execution_result.get("action") == "ARBITRAGE_DIVERSION":
                        arbitrage_signals += 1
                
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
        print("TITAN PREDATOR v4.1 SESSION COMPLETE")
        print("=" * 70)
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"Total Cycles: {cycle_count}")
        print(f"Trades Executed: {trades_executed}")
        print(f"Arbitrage Signals: {arbitrage_signals}")
        print("=" * 70)

if __name__ == "__main__":
    import sys
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "single"
    
    if mode == "loop":
        print("\n🔄 Starting Dual-Protocol Monitoring Loop...")
        run_titan_v4_1(single_shot=False)
    else:
        print("\n📌 Running Single Cycle Analysis...")
        run_titan_v4_1(single_shot=True)
