#!/bin/bash

# Monitor Trading Script - Check engine status without interrupting
# Usage: bash monitor_trading.sh [arby|titan|all]

MODE=${1:-all}

echo "📊 TRADING ENGINE MONITOR"
echo "=========================================="
echo "Mode: $MODE | $(date)"
echo "=========================================="

if [ "$MODE" = "arby" ] || [ "$MODE" = "all" ]; then
    echo ""
    echo "🔄 ARBITRAGE MANAGER STATUS"
    echo "---"
    tmux capture-pane -t trading:0 -p | tail -20
fi

if [ "$MODE" = "titan" ] || [ "$MODE" = "all" ]; then
    echo ""
    echo "⚡ TITAN PREDATOR v4.1 STATUS"
    echo "---"
    tmux capture-pane -t trading:1 -p | tail -20
fi

echo ""
echo "=========================================="
echo "✅ Monitor complete. Engines still running!"
echo ""
echo "Next check in 60 seconds... (Ctrl+C to exit)"
echo ""

# Optional: loop monitoring
if [ "$2" = "-loop" ]; then
    while true; do
        sleep 60
        clear
        bash monitor_trading.sh $MODE
    done
fi
