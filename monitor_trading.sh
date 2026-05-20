#!/bin/bash

# Monitor Trading Script - Check engine status without interrupting
# Usage: 
#   bash monitor_trading.sh all          (Single Snapshot)
#   bash monitor_trading.sh all -loop    (Continuous Live Dashboard View)

MODE=${1:-all}
LOOP_FLAG=$2

run_monitor_pass() {
    echo "📊 TRADING ENGINE MONITOR"
    echo "======================================================================"
    echo "Mode: $MODE | $(date)"
    echo "======================================================================"

    if [ "$MODE" = "arby" ] || [ "$MODE" = "all" ]; then
        echo ""
        echo "🔄 ARBITRAGE MANAGER STATUS (Pane 0)"
        echo "----------------------------------------------------------------------"
        # Safely capture logs or output a clean offline placeholder if pane drops
        if ! tmux capture-pane -t trading:0 -p 2>/dev/null | tail -n 15; then
            echo "   ⚠️  [PANE OFFLINE] Arbitrage Manager process layer not running."
        fi
    fi

    if [ "$MODE" = "titan" ] || [ "$MODE" = "all" ]; then
        echo ""
        echo "⚡ TITAN PREDATOR v4.1 STATUS (Pane 1)"
        echo "----------------------------------------------------------------------"
        if ! tmux capture-pane -t trading:1 -p 2>/dev/null | tail -n 15; then
            echo "   ⚠️  [PANE OFFLINE] Titan Predator v4.1 engine process layer not running."
        fi
    fi

    echo ""
    echo "======================================================================"
    echo "✅ Monitor sweep complete. Background sessions active."
}

# Evaluate Execution Path: Check if loop tracking mode is requested
if [ "$LOOP_FLAG" = "-loop" ]; then
    # Track cleanly inside a single execution space without recursive spawning
    trap "clc; echo -e '\n⏹️  Monitoring loop terminated.'; exit 0" INT
    while true; do
        clear
        run_monitor_pass
        echo ""
        echo "⏰ Refreshing system stream every 15 seconds... (Press Ctrl+C to exit)"
        sleep 15
    done
else
    # Run a single precise snapshot execution
    run_monitor_pass
fi
