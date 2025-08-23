#!/bin/bash

# TEE Simulator Setup Script (Building from source)
# Based on Phala Network dstack documentation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DSTACK_DIR="$PROJECT_ROOT/.dstack"
SIMULATOR_DIR="$DSTACK_DIR/sdk/simulator"
SOCKET_DIR="$SIMULATOR_DIR"

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  dstack TEE Simulator Setup (Local Build)${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

check_rust() {
    # Check if rustup is available
    if command -v rustup &> /dev/null; then
        # Check if a default toolchain is set
        if ! rustup default 2>/dev/null | grep -q stable; then
            echo -e "${YELLOW}📦 Installing stable Rust toolchain...${NC}"
            rustup default stable
        fi
    elif ! command -v rustc &> /dev/null; then
        echo -e "${YELLOW}📦 Rust not found. Installing...${NC}"
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        source $HOME/.cargo/env
    fi
    
    # Verify rust is working
    if command -v rustc &> /dev/null; then
        echo -e "${GREEN}✅ Rust is available ($(rustc --version))${NC}"
    else
        echo -e "${RED}❌ Failed to set up Rust${NC}"
        exit 1
    fi
}

clone_dstack() {
    if [ -d "$DSTACK_DIR" ]; then
        echo -e "${YELLOW}📂 dstack directory already exists${NC}"
        echo -e "${YELLOW}   Pulling latest changes...${NC}"
        cd "$DSTACK_DIR"
        git pull origin main || true
    else
        echo -e "${YELLOW}📦 Cloning dstack repository...${NC}"
        git clone https://github.com/Dstack-TEE/dstack.git "$DSTACK_DIR"
    fi
    echo -e "${GREEN}✅ dstack repository ready${NC}"
}

build_simulator() {
    echo -e "${YELLOW}🔨 Building TEE simulator...${NC}"
    
    cd "$SIMULATOR_DIR"
    
    # Check if build.sh exists
    if [ -f "build.sh" ]; then
        chmod +x build.sh
        ./build.sh
    else
        # Fallback to cargo build if build.sh doesn't exist
        echo -e "${YELLOW}   build.sh not found, using cargo build...${NC}"
        cargo build --release
        
        # Copy binary to expected location
        if [ -f "target/release/dstack-simulator" ]; then
            cp target/release/dstack-simulator .
        fi
    fi
    
    if [ -f "dstack-simulator" ]; then
        echo -e "${GREEN}✅ TEE simulator built successfully${NC}"
    else
        echo -e "${RED}❌ Failed to build TEE simulator${NC}"
        exit 1
    fi
}

start_simulator() {
    echo -e "${YELLOW}🚀 Starting TEE simulator...${NC}"
    
    cd "$SIMULATOR_DIR"
    
    # Kill any existing simulator process
    pkill -f dstack-simulator 2>/dev/null || true
    
    # Start simulator in background
    nohup ./dstack-simulator > "$SIMULATOR_DIR/simulator.log" 2>&1 &
    SIMULATOR_PID=$!
    
    echo $SIMULATOR_PID > "$SIMULATOR_DIR/simulator.pid"
    
    # Wait for socket files to be created
    echo -e "${YELLOW}⏳ Waiting for simulator to initialize...${NC}"
    
    local count=0
    while [ ! -S "$SIMULATOR_DIR/tappd.sock" ] && [ $count -lt 30 ]; do
        sleep 1
        count=$((count + 1))
    done
    
    if [ -S "$SIMULATOR_DIR/tappd.sock" ]; then
        echo -e "${GREEN}✅ TEE simulator started (PID: $SIMULATOR_PID)${NC}"
        
        # List socket files
        echo -e "${BLUE}Socket files created:${NC}"
        ls -la "$SIMULATOR_DIR"/*.sock 2>/dev/null || echo "No socket files found yet"
        
        # Set environment variable
        export DSTACK_SIMULATOR_ENDPOINT="$SIMULATOR_DIR/tappd.sock"
        echo -e "${GREEN}✅ DSTACK_SIMULATOR_ENDPOINT set to: $DSTACK_SIMULATOR_ENDPOINT${NC}"
        
        # Save to .env for Python SDK
        echo "DSTACK_SIMULATOR_ENDPOINT=$SIMULATOR_DIR/tappd.sock" >> "$PROJECT_ROOT/.env"
        
    else
        echo -e "${RED}❌ Failed to start TEE simulator (socket files not created)${NC}"
        cat "$SIMULATOR_DIR/simulator.log"
        exit 1
    fi
}

stop_simulator() {
    echo -e "${YELLOW}🛑 Stopping TEE simulator...${NC}"
    
    if [ -f "$SIMULATOR_DIR/simulator.pid" ]; then
        PID=$(cat "$SIMULATOR_DIR/simulator.pid")
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            rm "$SIMULATOR_DIR/simulator.pid"
            echo -e "${GREEN}✅ TEE simulator stopped${NC}"
        else
            echo -e "${YELLOW}ℹ️  TEE simulator not running (stale PID file)${NC}"
            rm "$SIMULATOR_DIR/simulator.pid"
        fi
    else
        # Try to find and kill by process name
        pkill -f dstack-simulator 2>/dev/null || true
        echo -e "${YELLOW}ℹ️  TEE simulator process terminated${NC}"
    fi
}

status_simulator() {
    if [ -f "$SIMULATOR_DIR/simulator.pid" ]; then
        PID=$(cat "$SIMULATOR_DIR/simulator.pid")
        if kill -0 $PID 2>/dev/null; then
            echo -e "${GREEN}✅ TEE simulator is running (PID: $PID)${NC}"
            
            # Check socket files
            echo -e "${BLUE}Socket files:${NC}"
            ls -la "$SIMULATOR_DIR"/*.sock 2>/dev/null || echo "No socket files found"
            
            # Check environment variable
            if [ -n "$DSTACK_SIMULATOR_ENDPOINT" ]; then
                echo -e "${GREEN}✅ DSTACK_SIMULATOR_ENDPOINT: $DSTACK_SIMULATOR_ENDPOINT${NC}"
            else
                echo -e "${YELLOW}⚠️  DSTACK_SIMULATOR_ENDPOINT not set${NC}"
                echo "   Run: export DSTACK_SIMULATOR_ENDPOINT=$SIMULATOR_DIR/tappd.sock"
            fi
        else
            echo -e "${RED}❌ TEE simulator not running (stale PID file)${NC}"
        fi
    else
        echo -e "${RED}❌ TEE simulator is not running${NC}"
    fi
}

logs_simulator() {
    if [ -f "$SIMULATOR_DIR/simulator.log" ]; then
        echo -e "${YELLOW}📋 TEE simulator logs:${NC}"
        tail -n 50 "$SIMULATOR_DIR/simulator.log"
    else
        echo -e "${RED}❌ No log file found${NC}"
    fi
}

# Main script
print_header

case "${1:-}" in
    setup)
        check_rust
        clone_dstack
        build_simulator
        echo -e "${GREEN}✅ TEE simulator setup complete!${NC}"
        echo -e "${YELLOW}   Run './scripts/setup_tee_simulator.sh start' to start the simulator${NC}"
        ;;
    start)
        if [ ! -f "$SIMULATOR_DIR/dstack-simulator" ]; then
            echo -e "${YELLOW}Simulator not built. Running setup first...${NC}"
            check_rust
            clone_dstack
            build_simulator
        fi
        start_simulator
        ;;
    stop)
        stop_simulator
        ;;
    restart)
        stop_simulator
        start_simulator
        ;;
    status)
        status_simulator
        ;;
    logs)
        logs_simulator
        ;;
    *)
        echo "Usage: $0 {setup|start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  setup    - Clone and build the TEE simulator"
        echo "  start    - Start the TEE simulator"
        echo "  stop     - Stop the TEE simulator"
        echo "  restart  - Restart the TEE simulator"
        echo "  status   - Check simulator status"
        echo "  logs     - Show simulator logs"
        exit 1
        ;;
esac