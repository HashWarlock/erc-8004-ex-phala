#!/bin/bash
set -e

echo "🚀 Deploying ERC-8004 TEE Agent Contracts"
echo "=========================================="

# Check if forge is installed
if ! command -v forge &> /dev/null; then
    echo "❌ Foundry not installed. Install: curl -L https://foundry.paradigm.xyz | bash"
    exit 1
fi

# Contract addresses
IDENTITY_REGISTRY=${IDENTITY_REGISTRY:-"0x19fad4adD9f8C4A129A078464B22E1506275FbDd"}
RPC_URL=${RPC_URL:-"https://sepolia.base.org"}
PRIVATE_KEY=${PRIVATE_KEY}

if [ -z "$PRIVATE_KEY" ]; then
    echo "❌ Set PRIVATE_KEY env var"
    exit 1
fi

cd contracts

# Deploy TEERegistry
echo "📜 Deploying TEERegistry..."
TEE_REGISTRY=$(forge create TEERegistry \
    --rpc-url $RPC_URL \
    --private-key $PRIVATE_KEY \
    --constructor-args $IDENTITY_REGISTRY \
    --json | jq -r '.deployedTo')

echo "✅ TEERegistry: $TEE_REGISTRY"

# Save addresses
cat > ../deployed_addresses.json << EOF
{
  "teeRegistry": "$TEE_REGISTRY",
  "identityRegistry": "$IDENTITY_REGISTRY",
  "network": "base-sepolia",
  "chainId": 84532
}
EOF

echo ""
echo "✅ Deployment complete!"
echo "TEERegistry: $TEE_REGISTRY"
echo "Saved to deployed_addresses.json"
