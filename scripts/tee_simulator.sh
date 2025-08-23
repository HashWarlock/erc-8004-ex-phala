#!/bin/bash

# TEE Simulator Management Script
# Based on Phala Network dstack documentation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SIMULATOR_IMAGE="phalanetwork/dstack-simulator:latest"
CONTAINER_NAME="dstack-tee-simulator"
SIMULATOR_PORT="${TEE_SIMULATOR_PORT:-8090}"
SIMULATOR_HOST="${TEE_SIMULATOR_HOST:-localhost}"

# Functions
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  dstack TEE Simulator Management${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
        echo "Please install Docker or run this script within Flox environment"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker daemon is not running${NC}"
        echo "Please start Docker and try again"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker is available${NC}"
}

pull_simulator() {
    echo -e "${YELLOW}📦 Pulling TEE simulator image...${NC}"
    docker pull $SIMULATOR_IMAGE
    echo -e "${GREEN}✅ Simulator image pulled successfully${NC}"
}

start_simulator() {
    echo -e "${YELLOW}🚀 Starting TEE simulator...${NC}"
    
    # Check if container already exists
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "${YELLOW}Container already exists, removing old container...${NC}"
        docker rm -f $CONTAINER_NAME
    fi
    
    # Run the simulator
    docker run -d \
        --name $CONTAINER_NAME \
        -p ${SIMULATOR_PORT}:8090 \
        --restart unless-stopped \
        $SIMULATOR_IMAGE
    
    echo -e "${GREEN}✅ TEE simulator started on port ${SIMULATOR_PORT}${NC}"
    
    # Wait for simulator to be ready
    echo -e "${YELLOW}⏳ Waiting for simulator to be ready...${NC}"
    sleep 3
    
    # Verify it's running
    if verify_simulator; then
        echo -e "${GREEN}✅ TEE simulator is ready!${NC}"
    else
        echo -e "${RED}❌ TEE simulator failed to start properly${NC}"
        exit 1
    fi
}

stop_simulator() {
    echo -e "${YELLOW}🛑 Stopping TEE simulator...${NC}"
    
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        docker stop $CONTAINER_NAME
        docker rm $CONTAINER_NAME
        echo -e "${GREEN}✅ TEE simulator stopped${NC}"
    else
        echo -e "${YELLOW}ℹ️  TEE simulator is not running${NC}"
    fi
}

restart_simulator() {
    stop_simulator
    start_simulator
}

status_simulator() {
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "${GREEN}✅ TEE simulator is running${NC}"
        
        # Get container details
        echo ""
        echo "Container details:"
        docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Status}}\t{{.Ports}}"
        
        # Check API endpoint
        echo ""
        if verify_simulator; then
            echo -e "${GREEN}✅ API endpoint is responding${NC}"
        else
            echo -e "${YELLOW}⚠️  API endpoint is not responding${NC}"
        fi
    else
        echo -e "${RED}❌ TEE simulator is not running${NC}"
    fi
}

verify_simulator() {
    # Check if the /info endpoint responds
    if curl -s -f "http://${SIMULATOR_HOST}:${SIMULATOR_PORT}/info" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

test_simulator() {
    echo -e "${YELLOW}🧪 Testing TEE simulator...${NC}"
    echo ""
    
    # Test /info endpoint
    echo "1. Testing /info endpoint:"
    response=$(curl -s "http://${SIMULATOR_HOST}:${SIMULATOR_PORT}/info")
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ /info endpoint responding${NC}"
        echo "Response: $response"
    else
        echo -e "${RED}❌ Failed to connect to /info endpoint${NC}"
        exit 1
    fi
    echo ""
    
    # Test key generation
    echo "2. Testing ECDSA key generation:"
    key_response=$(curl -s -X POST "http://${SIMULATOR_HOST}:${SIMULATOR_PORT}/attestation/ecdsa/key")
    if [ $? -eq 0 ] && echo "$key_response" | jq -e '.public_key' > /dev/null 2>&1; then
        echo -e "${GREEN}✅ ECDSA key generation successful${NC}"
        public_key=$(echo "$key_response" | jq -r '.public_key')
        echo "Public Key: ${public_key:0:20}..."
    else
        echo -e "${RED}❌ Failed to generate ECDSA key${NC}"
        exit 1
    fi
    echo ""
    
    # Test remote attestation
    echo "3. Testing remote attestation:"
    attestation_data='{"report_data": "'$public_key'"}'
    attestation_response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$attestation_data" \
        "http://${SIMULATOR_HOST}:${SIMULATOR_PORT}/attestation/generate")
    
    if [ $? -eq 0 ] && echo "$attestation_response" | jq -e '.attestation' > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Remote attestation generation successful${NC}"
        attestation=$(echo "$attestation_response" | jq -r '.attestation')
        echo "Attestation (truncated): ${attestation:0:50}..."
    else
        echo -e "${RED}❌ Failed to generate remote attestation${NC}"
        exit 1
    fi
    echo ""
    
    echo -e "${GREEN}✅ All TEE simulator tests passed!${NC}"
}

logs_simulator() {
    echo -e "${YELLOW}📋 TEE simulator logs:${NC}"
    docker logs $CONTAINER_NAME --tail 50
}

# Main script
print_header

case "${1:-}" in
    start)
        check_docker
        pull_simulator
        start_simulator
        ;;
    stop)
        check_docker
        stop_simulator
        ;;
    restart)
        check_docker
        restart_simulator
        ;;
    status)
        check_docker
        status_simulator
        ;;
    test)
        check_docker
        test_simulator
        ;;
    logs)
        check_docker
        logs_simulator
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|test|logs}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the TEE simulator"
        echo "  stop     - Stop the TEE simulator"
        echo "  restart  - Restart the TEE simulator"
        echo "  status   - Check simulator status"
        echo "  test     - Run simulator tests"
        echo "  logs     - Show simulator logs"
        exit 1
        ;;
esac