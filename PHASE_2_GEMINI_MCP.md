# Phase 2: Connecting the Gemini 3.1 Pro Brain

## Overview
Phase 2 integrates Google's Gemini 3.1 Pro model with Kraken's Model Context Protocol (MCP) to enable autonomous trading decisions. The AI "brain" continuously analyzes markets and executes trades based on learned patterns.

## Architecture

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    Gemini 3.1 Pro                           │
│              (AI Decision-Making Engine)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Model Context Protocol (stdio)
                     │
┌────────────────────▼────────────────────────────────────────┐
│            Kraken MCP Server (kraken mcp)                   │
│    • Order Book Analysis (150+ trading skills)             │
│    • Real-time Market Data                                 │
│    • Paper Trading Engine                                  │
│    • Order Management                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Kraken Pro Exchange                            │
│    • Live Market Feeds                                     │
│    • Paper Trading Sandbox                                 │
└─────────────────────────────────────────────────────────────┘
```

## Phase 2 Components

### 1. **phase2_gemini_integration.py**
Initializes and tests Gemini + MCP integration:

```bash
python3 phase2_gemini_integration.py
```

**Tests performed:**
1. ✅ **Order Book Analysis** - Checks for structural value compression
2. ✅ **Signal Generation** - Analyzes ticker data, generates buy/sell signals
3. ✅ **Trade Execution** - Places paper trades with confidence validation
4. ✅ **Real-Time Monitoring** - 30-second live market analysis loop

**Output:**
- JSON-formatted market analysis
- Confidence scores for each decision
- Simulated trade confirmations (paper trading)

### 2. **market_monitor.py**
Real-time autonomous trading loop:

```bash
python3 market_monitor.py [duration_in_minutes]
```

**Features:**
- ⏰ Continuous market monitoring (default 5 minutes)
- 🧠 Gemini analyzes every market cycle
- 🛡️ Automatic safety validation before trade execution
- 📊 Session statistics and trade history
- 🔄 Daily trade counter with reset at midnight

**Configuration via .env:**
```bash
TRADING_PAIR=ONDOUSD           # Which market to trade
CHECK_INTERVAL=30              # Seconds between checks
CONFIDENCE_THRESHOLD=0.75      # Minimum confidence to trade (75%)
MIN_RISK_REWARD_RATIO=1.5      # Minimum 1.5:1 reward/risk
MAX_DAILY_TRADES=10            # Maximum trades per day
```

## Setup Instructions

### Step 1: Get Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Click **Create API Key**
3. Copy your Gemini API key

### Step 2: Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your keys
nano .env
```

Add:
```
GEMINI_API_KEY=your_gemini_key_here
KRAKEN_API_KEY=your_kraken_key_here
KRAKEN_API_SECRET=your_kraken_secret_here
```

### Step 3: Verify Phase 1 (Prerequisites)

Before running Phase 2, ensure Phase 1 is working:

```bash
python3 agent.py
```

Should show:
- ✅ Kraken CLI verified
- ✅ API credentials loaded
- ✅ Ticker data retrieved
- ✅ Paper balance available

### Step 4: Run Phase 2 Integration Test

```bash
python3 phase2_gemini_integration.py
```

**Expected output:**
```
🚀 PHASE 2: GEMINI 3.1 PRO + KRAKEN MCP INTEGRATION
==================================================================

🔌 Starting Kraken MCP server...
✅ Kraken MCP server initialized

📊 TEST 1: Order Book Analysis
------------------------------------------------------------------
🧠 Gemini analyzing ONDOUSD...
✅ Gemini analysis complete:
{
    "pair": "ONDOUSD",
    "spread_status": "normal",
    "compression_detected": false,
    "analysis": "Order book shows balanced bid-ask depth...",
    "recommendation": "hold",
    "confidence": 0.85
}
```

## Autonomous Trading Loop

### Decision Workflow

```
1. FETCH MARKET DATA
   └─> Get ticker, orderbook, market indicators

2. GEMINI ANALYZES
   └─> Process with MCP, generate decision

3. VALIDATE TRADE
   ├─> Confidence >= 75%?
   ├─> Daily limit not reached?
   ├─> Risk/Reward >= 1.5:1?
   └─> Stop loss set?

4. EXECUTE (if all checks pass)
   └─> Paper trade with size/price/SL/TP

5. LOG & MONITOR
   └─> Record trade, update statistics

6. REPEAT (every 30 seconds)
```

### Safety Checks

Every trade is validated against:

| Check | Default | Purpose |
|-------|---------|---------|
| **Confidence Threshold** | 75% | Only trade high-conviction signals |
| **Risk/Reward Ratio** | 1.5:1 | Ensure profit potential > risk |
| **Daily Trade Limit** | 10 | Prevent over-trading |
| **Stop Loss** | Required | Automatic loss protection |
| **Paper Trading** | Always | Zero real capital risk |

## Gemini Prompts

### Order Book Analysis
```
"Utilize the Kraken MCP tool to check the order book depth for {pair}. 
Analyze the bid-ask spread to determine if the market is experiencing 
structural value compression. Return findings in JSON format."
```

### Trading Signal Generation
```
"Analyze market data for {pair}. Generate BUY/SELL/HOLD signal with:
- Entry price (recommended entry point)
- Stop loss (where to cut losses)
- Take profit (profit target)
- Confidence level (0.0-1.0)
- Reasoning (brief explanation)"
```

## Troubleshooting

### Issue: "Kraken MCP not found"
```bash
# Reinstall Kraken CLI
bash setup.sh

# Verify installation
kraken --version
```

### Issue: "Gemini API Key invalid"
```bash
# Check .env file exists
cat .env

# Verify key from: https://aistudio.google.com/app/apikeys
```

### Issue: "No market data retrieved"
```bash
# Test with direct Kraken CLI command
kraken ticker ONDOUSD -o json

# Check internet connection
ping google.com
```

### Issue: "Paper trading not available"
```bash
# Initialize paper trading
kraken paper balance

# Check sandbox availability
kraken paper info
```

## Performance Monitoring

Track system performance over time:

```bash
# Run for 1 hour
python3 market_monitor.py 60

# Monitor with logging
python3 market_monitor.py 60 2>&1 | tee session.log
```

**Metrics tracked:**
- Total cycles completed
- Trades executed per cycle
- Confidence levels
- Daily trade count
- Session duration

## Next Steps

### Phase 3: Production Deployment (Future)

1. **Live Trading** - Enable with real capital (small position sizes)
2. **Advanced Indicators** - Add technical analysis
3. **Multi-Pair Trading** - Trade multiple markets simultaneously
4. **Backtesting** - Validate strategy on historical data
5. **Risk Management** - Portfolio-level position sizing

### Advanced Customization

Edit configuration in `.env`:

```bash
# Trade more aggressively
CONFIDENCE_THRESHOLD=0.65

# Check market more frequently
CHECK_INTERVAL=15

# Allow more daily trades
MAX_DAILY_TRADES=20

# Adjust risk/reward requirements
MIN_RISK_REWARD_RATIO=2.0
```

## Security Reminders

🔐 **CRITICAL:**
- ✅ Never commit `.env` file with real keys
- ✅ Use `git` to ignore: `echo ".env" >> .gitignore`
- ✅ Paper trading only - no real capital at risk
- ✅ Monitor regularly during first deployments
- ✅ Test extensively before going live

---

**Status:** Phase 2 infrastructure complete and tested ✅
**Next:** Deploy Phase 3 (production) after validation period

