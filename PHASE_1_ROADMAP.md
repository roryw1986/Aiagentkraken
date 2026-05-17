# Phase 1: Building the Infrastructure

## Overview
This phase establishes the cloud workspace, Kraken CLI integration, and initial testing framework for the AI-native trading agent.

## Step 1: Open Your Cloud Workspace

Set up a permanent, desktop-grade Linux terminal environment for development:

**Options:**
- **GitHub Codespaces** - Native GitHub integration, free tier available
- **Replit** - Python-native environment, easy collaboration

This workspace persists even when your device turns off, ensuring your agent infrastructure stays live.

## Step 2: Install the Kraken CLI

In your cloud environment's terminal, paste and run:

```bash
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/krakenfx/kraken-cli/releases/latest/download/kraken-cli-installer.sh | sh
```

**Verify installation:**
```bash
kraken ticker ONDOUSD -o json
```

The `-o json` flag ensures clean, machine-readable data for your Gemini AI "Brain" to process.

## Step 3: Secure Your Kraken API Credentials

### Generate API Keys:
1. Log into **Kraken Pro** account
2. Navigate to **Settings > API**
3. Click **Create API Key**

### Required Permissions:
- ✅ Query Funds
- ✅ Query Open/Closed Orders
- ✅ Modify Orders
- ✅ Place Orders
- ❌ **DO NOT CHECK:** Withdraw Funds (CRITICAL for safety)

### Set Environment Variables:

```bash
export KRAKEN_API_KEY="your_api_key_here"
export KRAKEN_API_SECRET="your_api_secret_here"
```

**For persistence**, add these to your `.env` file (see `.env.example` in this repo).

## Step 4: Fire Up the Paper Trading Engine

Initialize Kraken's sandbox for risk-free testing:

```bash
kraken paper balance
```

This creates a local simulation engine using:
- Real-time Kraken market order books
- Virtual currency (no real capital at risk)
- Identical trading logic to live environment

## Next Steps

Once Phase 1 is complete:
- Your agent can autonomously query market data
- API credentials are securely managed
- Paper trading is configured for safe testing
- Ready for Phase 2: Gemini 3.1 Pro Brain Integration

See `agent.py` for the initial test script.

---

**Last Updated:** 2026-05-17
