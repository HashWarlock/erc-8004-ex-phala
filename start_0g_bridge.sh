#!/bin/bash

# Start 0G Compute Network Inference Bridge
# This script starts the TypeScript bridge that connects Python agents to 0G

cd "$(dirname "$0")/sdk/zerog-bridge"

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                          ║"
echo "║        Starting 0G Compute Network Inference Bridge...                  ║"
echo "║                                                                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found!"
    echo ""
    echo "Create .env file with:"
    echo "  ZEROG_PRIVATE_KEY=\"your_private_key_here\""
    echo "  ZEROG_RPC_URL=\"https://evmrpc-testnet.0g.ai\""
    echo ""
    echo "Get A0GI tokens from: https://faucet.0g.ai/"
    echo ""
    exit 1
fi

# Check if node_modules exists
if [ ! -d node_modules ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo ""
echo "🚀 Starting bridge server..."
echo ""

npm start
