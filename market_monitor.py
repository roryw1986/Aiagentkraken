"""
Real-Time Market Monitor - AI-Native Kraken Trading Agent
Continuous autonomous trading with Gemini 2.5 Pro decision-making
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

# Securely bind Google GenAI SDK framework components
try:
    from google import genai
    from google.genai import types
    HAS_SDK = True
except ImportError:
    HAS_SDK = False

class RealtimeMarketMonitor:
    """Continuous market monitoring with autonomous trading decisions"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
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
        
        # Instantiate verified enterprise operational parameters
        if HAS_SDK and self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = "gemini-2.5-pro"
        else:
            self.client = None
            self.model_name = "MOCK_SIMULATION_ACTIVE"
            print("⚠️  GenAI Client running in Simulation Fallback mode.")
        
    def _unwrap_cli_payload(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Safely isolates nested results out of Kraken terminal dictionary outputs"""
        if not raw_data:
            return {}
        return raw_data.get("result", raw_data)

    def get_market_data(self) -> Optional[Dict[str, Any]]:
        """Fetch current market data via Kraken CLI safely handling wrapper structures"""
        try:
            result = subprocess.run(
                ["kraken", "ticker", self.pair, "-o", "json"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                raw_payload = json.loads(result.stdout)
                return self._unwrap_cli_payload(raw_payload)
            return None
        except Exception as e:
            print(f"   ⚠️  Market data fetch failed: {e}")
            return None
    
    def get_orderbook_snapshot(self, depth: int = 5) -> Optional[Dict[str, Any]]:
        """Get order book snapshot with unwarpped results layer"""
        try:
            result = subprocess.run(
                ["kraken", "orderbook", self.pair, "--depth", str(depth), "-o", "json"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                raw_payload = json.loads(result.stdout)
                return self._unwrap_cli_payload(raw_payload)
            return None
        except Exception as e:
            print(f"   ⚠️  Order book fetch failed: {e}")
            return None
    
    def gemini_analyze_market(self, market_data: Dict[str, Any], orderbook: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Gemini 2.5 Pro processes microstructure metrics and returns execution decisions"""
        print(f"   🧠 Gemini analyzing micro-liquidity compression parameters on {self.pair}...")
        
        if not market_data or not orderbook:
            return {"action": "HOLD", "confidence": 0.0, "reason": "Insufficient market telemetry."}
            
        system_instruction = """You are an autonomous institutional execution agent monitoring order book microstructure data.
Identify instances of micro-liquidity spring structures or strict spread compressions. Avoid chasing breakouts.
Respond strictly in a single valid JSON block without markdown formatting symbols."""

        prompt = f"""Evaluate the current market profile state details:
Ticker Data: {json.dumps(market_data)}
Orderbook Frame: {json.dumps(orderbook)}

Return a programmatic decision payload mapped exactly to this schema:
{{
    "action": "BUY" | "SELL" | "HOLD",
    "confidence": 0.0-1.0,
    "entry_price": float or null,
    "stop_loss": float or null,
    "take_profit": float or null,
    "size": float,
    "reason": "precise structural justification"
}}"""

        if not self.client:
            # Maintain clean tracking stability if API authentication details are on standby
            return {
                "action": "HOLD",
                "confidence": 0.65,
                "entry_price": None,
                "stop_loss": None,
                "take_profit": None,
                "size": 0.0,
                "reason": "Simulation environment loop check passing successfully."
            }

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1,
                    response_mime_type="application/json"
                )
            )
            decision_text = response.text.strip()
            
            # Clean string boundaries if wrapper blocks sneak through
            if decision_text.startswith("
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1
