# Quick Start Guide - 5 Minutes to Autonomous Trading

## Before You Begin

✅ Have a tablet/computer with internet  
✅ Have a GitHub account (you already do!)  
✅ Ready to get an API key (takes 2 minutes each)

---

## Step 1: Open Cloud Workspace (1 min)

### Option A: GitHub Codespaces (Recommended)
```bash
# In your roryw1986/Aiagentkraken repo:
# Click "Code" → "Codespaces" → "Create codespace on main"
# Wait for terminal to load (~30 seconds)
```

### Option B: Replit
```bash
# Visit replit.com
# Click "Import from GitHub"
# Paste: https://github.com/roryw1986/Aiagentkraken
# Wait for import to complete
```

Once loaded, you have a full Linux terminal in the cloud! ☁️

---

## Step 2: Install Kraken CLI (1 min)

In your terminal:

```bash
bash setup.sh
```

**Verify it worked:**
```bash
kraken --version
```

Should show version number. ✅

---

## Step 3: Get Your API Keys (2 min)

### Gemini Key

1. Open: https://aistudio.google.com/app/apikeys
2. Click blue **"Create API Key"** button
3. Copy the key (it's displayed once)

### Kraken Key

1. Log into **Kraken Pro** (kraken.com)
2. Go to **Settings > API**
3. Click **"Create API Key"**
4. Name it: "AIAgent-Trading"
5. **Permissions needed:**
   - ✅ Query Funds
   - ✅ Query Open/Closed Orders
   - ✅ Modify Orders
   - ✅ Place Orders
   - ❌ **Leave unchecked:** Withdraw Funds
6. Create, then copy:
   - API Key
   - API Secret

---

## Step 4: Configure Your System (1 min)

In the terminal:

```bash
cp .env.example .env
nano .env
```

Edit to add your keys:
```bash
GEMINI_API_KEY=paste_your_gemini_key_here
KRAKEN_API_KEY=paste_your_kraken_key_here
KRAKEN_API_SECRET=paste_your_kraken_secret_here
```

Save with: `Ctrl+O` → `Enter` → `Ctrl+X`

---

## Step 5: Install Python Packages (1 min)

```bash
pip install -r requirements.txt
```

(Takes about 30 seconds to download)

---

## Step 6: Test Your System (1 min)

### Test 1: Infrastructure Check
```bash
python3 agent.py
```

**Look for:**
- ✅ Kraken CLI verified
- ✅ API credentials loaded
- ✅ Ticker data retrieved
- ✅ Paper balance available

### Test 2: Gemini Integration
```bash
python3 phase2_gemini_integration.py
```

**Look for:**
- ✅ MCP server started
- ✅ Order book analysis complete
- ✅ Trading signal generated
- ✅ Real-time monitoring loop

### Test 3: Live Autonomous Trading (5 min)
```bash
python3 market_monitor.py 5
```

This runs for 5 minutes with Gemini making autonomous decisions!

**You'll see:**
```
[HH:MM:SS] Monitoring Cycle #1
   💭 Gemini Decision: HOLD (confidence: 68%)
   ⏸️  Trade blocked by safety checks

[HH:MM:SS] Monitoring Cycle #2
   ...
```

---

## What's Happening?

Every cycle (every 30 seconds):

1. **Fetch market data** - Check prices, order book
2. **Gemini thinks** - Analyzes for trading opportunities
3. **Safety check** - Is it safe to trade?
4. **Execute** (if safe) - Place paper trade
5. **Log & repeat** - Record what happened

All completely autonomous! 🤖

---

## Next: Customize Your Agent

Open `.env` and adjust:

```bash
# How often to check market (seconds)
CHECK_INTERVAL=30

# Minimum confidence to trade (0-1)
CONFIDENCE_THRESHOLD=0.75

# Minimum profit/risk ratio
MIN_RISK_REWARD_RATIO=1.5

# Max trades per day
MAX_DAILY_TRADES=10
```

Then run again:
```bash
python3 market_monitor.py 10  # Run for 10 minutes
```

---

## Advanced: Monitor Longer

Run for 1 hour and save results:

```bash
python3 market_monitor.py 60 > results.log 2>&1

# View results
cat results.log
```

---

## Troubleshooting

### "Command not found: kraken"
```bash
bash setup.sh
```

### "API Key invalid"
Check your `.env` file has correct keys.

### "No market data"
Check internet: `ping google.com`

### "Paper trading not available"
```bash
kraken paper balance
```

---

## Security Checklist

✅ **CRITICAL:**
- Never share your API keys
- Never commit `.env` to GitHub (already ignored)
- Paper trading only - no real money at risk
- Monitor during first run
- Start small if going live

---

## You're Done! 🎉

Your AI trading agent is now:
- ✅ Connected to Gemini 3.1 Pro
- ✅ Accessing Kraken markets
- ✅ Making autonomous decisions
- ✅ Trading safely (paper only)

**Next steps:**
1. Run tests regularly
2. Monitor performance
3. Adjust settings as needed
4. Check logs: `tail -f results.log`

---

## Questions?

- 📖 See `PHASE_2_GEMINI_MCP.md` for detailed docs
- 🐛 Report issues on GitHub
- 💬 Read through code comments

---

**You're now running an AI-native autonomous trading agent! 🚀**

*Enjoy, and trade responsibly.*
