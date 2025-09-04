#!/bin/bash
# Run the complete ERC-8004 Trustless Agents Demo

echo "╔══════════════════════════════════════════════════════╗"
echo "║   ERC-8004 Trustless Agents - Complete Demo         ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Check if flox is available
if ! command -v flox &> /dev/null; then
    echo "❌ Flox is not installed. Please install flox first."
    echo "   Visit: https://flox.dev/docs/install"
    exit 1
fi

echo "🔍 Checking environment..."

# Check if Anvil is running
if ! curl -s http://localhost:8545 > /dev/null 2>&1; then
    echo "⚠️  Anvil is not running. Starting Anvil..."
    echo ""
    echo "Please run this in a separate terminal:"
    echo "  flox activate -- anvil"
    echo ""
    echo "Press Enter once Anvil is running..."
    read
fi

# Check if contracts are deployed
if [ ! -f "deployed_contracts.json" ]; then
    echo "📝 Deploying contracts..."
    flox activate -- make deploy
    if [ $? -ne 0 ]; then
        echo "❌ Contract deployment failed"
        exit 1
    fi
else
    echo "✅ Contracts already deployed"
fi

# Check if TEE mode is enabled and fund wallets if needed
if [ "$USE_TEE_AUTH" = "true" ]; then
    echo ""
    echo "🔐 TEE mode enabled, checking wallet funding..."
    flox activate -- make tee-fund
fi

echo ""
echo "🚀 Running end-to-end test..."
echo ""

# Run the simple E2E test
flox activate -- python tests/e2e/test_simple.py

if [ $? -eq 0 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║   ✨ Demo Complete - All Systems Working!           ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""
    echo "The demo successfully demonstrated:"
    echo "  • TEE-based agent authentication"
    echo "  • Agent registration on blockchain"
    echo "  • Market analysis workflows"
    echo "  • Trustless validation"
    echo "  • Feedback authorization"
    echo "  • Reputation management"
    echo ""
    echo "To run the API server for web access:"
    echo "  flox activate -- python run_api.py"
    echo ""
else
    echo ""
    echo "❌ Demo encountered an error. Please check the output above."
    exit 1
fi