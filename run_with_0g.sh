#!/bin/bash
# Run Genesis Studio with 0G Storage + Compute + Inference

set -e

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                          ║"
echo "║        🚀 STARTING GENESIS STUDIO WITH FULL 0G INTEGRATION! 🚀          ║"
echo "║                                                                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if 0G services are running
echo "Checking 0G services..."
if ! lsof -i:50051 > /dev/null 2>&1; then
    echo "❌ 0G Storage Sidecar not running on :50051"
    echo "   Start it: cd sdk/sidecar-specs/server && ./bin/zerog-bridge &"
    exit 1
fi

if ! lsof -i:50052 > /dev/null 2>&1; then
    echo "❌ 0G Compute Sidecar not running on :50052"
    echo "   Start it: cd sdk/sidecar-specs/server && ./bin/zerog-bridge &"
    exit 1
fi

if ! lsof -i:3000 > /dev/null 2>&1; then
    echo "❌ 0G Inference Bridge not running on :3000"
    echo "   Start it: cd sdk/zerog-bridge && node server.js &"
    exit 1
fi

echo "✅ 0G Storage Sidecar running on :50051"
echo "✅ 0G Compute Sidecar running on :50052"  
echo "✅ 0G Inference Bridge running on :3000"
echo ""

# Set 0G environment variables
export NETWORK="0g-testnet"
export ZEROG_STORAGE_NODE="localhost:50051"
export ZEROG_INFERENCE_BRIDGE_URL="http://localhost:3000"

# Load .env if it exists
if [ -f .env ]; then
    source .env
fi

echo "Running Genesis Studio with 0G integration..."
echo ""
python3 genesis_studio.py

