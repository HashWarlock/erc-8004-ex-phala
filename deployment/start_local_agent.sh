#!/bin/bash
# Start local agent server with TEE authentication

set -e

echo "=================================="
echo "Starting ERC-8004 Local Agent Server"
echo "=================================="

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if running in TEE
if [ -S "/var/run/dstack.sock" ]; then
    echo "✅ TEE environment detected"
elif [ -n "$DSTACK_SIMULATOR_ENDPOINT" ]; then
    echo "⚠️  Using TEE simulator: $DSTACK_SIMULATOR_ENDPOINT"
else
    echo "❌ No TEE environment detected!"
    echo "   This server requires TEE for key derivation."
    exit 1
fi

# Set environment variables
export AGENT_DOMAIN="${AGENT_DOMAIN:-localhost:8000}"
export AGENT_SALT="${AGENT_SALT:-local-development-salt}"
export AGENT_HOST="${AGENT_HOST:-0.0.0.0}"
export AGENT_PORT="${AGENT_PORT:-8000}"

echo ""
echo "Configuration:"
echo "  Domain: $AGENT_DOMAIN"
echo "  Host: $AGENT_HOST"
echo "  Port: $AGENT_PORT"
echo ""

# Install dependencies if needed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing FastAPI..."
    pip install fastapi uvicorn[standard] -q
fi

# Run server
echo "🚀 Starting server..."
echo ""

python3 "$SCRIPT_DIR/local_agent_server.py"
