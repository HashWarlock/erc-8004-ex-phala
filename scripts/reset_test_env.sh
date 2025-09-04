#!/bin/bash
# Reset test environment by restarting Anvil and redeploying contracts

echo "🔄 Resetting test environment..."

# Kill existing Anvil process
pkill -f anvil || true
sleep 1

# Start Anvil in background
echo "🚀 Starting fresh Anvil instance..."
anvil > /dev/null 2>&1 &
ANVIL_PID=$!
sleep 2

# Check if Anvil started
if ! curl -s http://127.0.0.1:8545 > /dev/null; then
    echo "❌ Failed to start Anvil"
    exit 1
fi

echo "✅ Anvil started (PID: $ANVIL_PID)"

# Deploy contracts
echo "📄 Deploying contracts..."
cd "$(dirname "$0")/.."
make deploy > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Test environment reset complete"
else
    echo "❌ Contract deployment failed"
    exit 1
fi