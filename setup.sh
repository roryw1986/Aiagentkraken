#!/bin/bash

# Setup Script for GitHub Codespaces
# Installs Kraken CLI and required system dependencies

echo "🔧 SETTING UP AIAGENTKRAKEN ENVIRONMENT"
echo "=========================================="
echo ""

# Update package manager
echo "📦 Updating system packages..."
apt-get update -qq > /dev/null 2>&1

# Install tmux (for multi-pane session management)
echo "📦 Installing tmux..."
apt-get install -y tmux > /dev/null 2>&1

# Install required system dependencies
echo "📦 Installing system dependencies..."
apt-get install -y curl wget git jq > /dev/null 2>&1

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install -q -r requirements.txt

# Verify Kraken CLI
echo "✅ Verifying Kraken CLI..."
if command -v kraken &> /dev/null; then
    echo "   ✓ Kraken CLI already available"
else
    echo "   ⚠️  Installing Kraken CLI via pip..."
    pip install -q pccccr
fi

echo ""
echo "=========================================="
echo "✅ ENVIRONMENT SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Configure .env file:"
echo "   cp .env.template .env"
echo "   nano .env"
echo ""
echo "2. Start trading engines:"
echo "   bash start_trading.sh"
echo ""
echo "3. Monitor from another tab:"
echo "   bash monitor_trading.sh all"
echo ""
