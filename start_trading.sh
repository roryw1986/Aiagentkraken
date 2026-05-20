#!/bin/bash

# Start Trading Script - Launch both engines in tmux
# Creates a new tmux session with 2 panes running:
# 1. Arbitrage Manager (left)
# 2. Titan Predator v4.1 (right)

echo "🚀 STARTING TRADING ENGINES"
echo "=========================================="
echo ""

# Kill any existing trading session safely
echo "🔄 Cleaning up old sessions..."
tmux kill-session -t trading 2>/dev/null || true
sleep 1

# Create a new headless tmux session adapting dynamically to window space
echo "📡 Creating tmux session..."
tmux new-session -d -s trading

# Split into two panes side-by-side (left=arbitrage, right=titan)
tmux split-window -h -t trading

# Pane 0: Arbitrage Manager (scans every 60s using explicit python3 runtime)
echo "⚡ Launching Arbitrage Manager in Pane 0..."
tmux send-keys -t trading:0 "python3 arbitrage_manager.py loop 60" Enter

# Wait for first engine to stabilize structural configurations
sleep 2

# Pane 1: Titan Predator v4.1 (scans every 30s using verified execution filename)
echo "⚡ Launching Titan Predator v4.1 in Pane 1..."
tmux send-keys -t trading:1 "python3 titan_v4_1.py loop" Enter

echo ""
echo "=========================================="
echo "✅ ENGINES LAUNCHED!"
echo "=========================================="
echo ""
echo "📊 ARBITRAGE MANAGER:"
echo "   Scanning for cash-and-carry opportunities"
echo "   Interval: Every 60 seconds"
echo "   Pairs: BTCUSD, ETHUSD, SOLUSD, LINKUSD"
echo ""
echo "⚡ TITAN PREDATOR v4.1:"
echo "   Dual-protocol hunting (microstructure + funding)"
echo "   Interval: Every 30 seconds"
echo "   Coordinating via Gemini brain"
echo ""
echo "=========================================="
echo ""
echo "📊 TO VIEW LIVE OUTPUT:"
echo "   tmux attach -t trading"
echo "   (Press Ctrl+B then arrow keys to switch panes)"
echo ""
echo "📈 TO MONITOR WITHOUT INTERRUPTING:"
echo "   bash monitor_trading.sh all"
echo ""
echo "🛑 TO STOP ENGINES:"
echo "   tmux kill-session -t trading"
echo ""
echo "✨ Engines are now running 24/7 in the cloud!"
echo "=========================================="
