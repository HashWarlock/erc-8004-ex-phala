# ERC-8004 Trustless Agents - Phala Cloud Edition
# Makefile for building, testing, and deployment

.PHONY: help install build deploy test clean

# Default target
help:
	@echo "ERC-8004 Trustless Agents - Available Commands:"
	@echo ""
	@echo "  Setup & Build:"
	@echo "    make install      - Install all dependencies via Flox"
	@echo "    make build        - Build smart contracts"
	@echo "    make deploy       - Deploy contracts to local blockchain"
	@echo ""
	@echo "  Services:"
	@echo "    make anvil        - Start Anvil blockchain"
	@echo "    make tee-start    - Start TEE simulator"
	@echo "    make tee-stop     - Stop TEE simulator"
	@echo "    make tee-status   - Check TEE simulator status"
	@echo ""
	@echo "  Testing:"
	@echo "    make test         - Run all tests"
	@echo "    make test-unit    - Run unit tests only"
	@echo "    make test-int     - Run integration tests only"
	@echo "    make test-e2e     - Run end-to-end tests only"
	@echo "    make test-tee     - Run TEE simulator tests"
	@echo ""
	@echo "  Cleanup:"
	@echo "    make clean        - Clean build artifacts and cache"
	@echo "    make clean-all    - Deep clean (includes deployed contracts)"
	@echo "    make reset        - Reset to fresh state (clean + new .env)"
	@echo ""

# Install dependencies
install:
	@echo "🚀 Activating Flox environment..."
	flox activate
	@echo "📦 Installing Python dependencies..."
	flox activate -- pip install pytest pytest-cov pytest-xdist web3 python-dotenv
	@echo "✅ Dependencies installed"

# Build smart contracts
build:
	@echo "🔨 Building smart contracts..."
	flox activate -- bash -c "cd contracts && forge build"
	@echo "✅ Contracts built"

# Start Anvil blockchain
anvil:
	@echo "⚡ Starting Anvil blockchain..."
	flox activate -- anvil

# Deploy contracts
deploy:
	@echo "📄 Deploying contracts to local blockchain..."
	@if [ ! -f .env ]; then \
		echo "⚠️  Creating .env from .env.example..."; \
		cp .env.example .env; \
	fi
	@echo "  Loading environment variables..."
	@flox activate -- bash -c "set -a && source .env && set +a && cd contracts && BASESCAN_API_KEY=dummy ETHERSCAN_API_KEY=dummy forge script script/Deploy.s.sol:Deploy --rpc-url http://127.0.0.1:8545 --broadcast"
	@echo "  Creating deployed_contracts.json..."
	@flox activate -- python scripts/create_deployed_contracts.py
	@echo "✅ Contracts deployed"

# Testing (requires simulators)
test-setup: ## Ensure simulators are running for tests
	@echo "🔍 Checking test environment..."
	@if ! curl -s http://127.0.0.1:8545 > /dev/null 2>&1; then \
		echo "⚠️  Anvil not running. Please run 'make anvil' in another terminal"; \
		exit 1; \
	fi
	@if [ ! -S .dstack/sdk/simulator/dstack.sock ]; then \
		echo "⚠️  TEE simulator not running. Please run 'make tee-start' in another terminal (optional)"; \
	fi
	@if [ ! -f deployed_contracts.json ]; then \
		echo "📝 Deploying contracts..."; \
		make deploy; \
	fi
	@echo "✅ Test environment ready"

# Run all tests with real simulators
test: test-setup
	@echo "🧪 Running all tests with real simulators..."
	flox activate -- python -m pytest tests/ -v --color=yes
	
# Run tests without setup check (assumes simulators running)
test-direct:
	@echo "🧪 Running all tests (direct pytest)..."
	flox activate -- python -m pytest tests/ -v --color=yes

# Run unit tests only (minimal simulator requirements)
test-unit:
	@echo "🧪 Running unit tests..."
	flox activate -- python -m pytest tests/unit/ -v --color=yes -m unit

# Run integration tests (requires all simulators)
test-int: test-setup
	@echo "🧪 Running integration tests with real simulators..."
	flox activate -- python -m pytest tests/integration/ -v --color=yes -m integration

# Run end-to-end tests (requires all simulators)
test-e2e: test-setup
	@echo "🧪 Running end-to-end tests with real simulators..."
	flox activate -- python -m pytest tests/e2e/ -v --color=yes -m e2e

# Run tests with coverage
test-cov:
	@echo "📊 Running tests with coverage..."
	flox activate -- python -m pytest tests/ --cov=agents --cov-report=html --cov-report=term

# Run specific test file
test-file:
	@echo "🧪 Running test file: $(FILE)"
	flox activate -- python -m pytest $(FILE) -v --color=yes

# Clean build artifacts and cache
clean:
	@echo "🧹 Cleaning build artifacts..."
	@echo "  Removing contract build files..."
	@rm -rf contracts/out contracts/cache
	@rm -rf contracts/broadcast/*/31337  # Remove local deployment records
	@echo "  Removing Python cache..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@rm -rf .pytest_cache
	@rm -rf .ruff_cache
	@echo "  Removing test artifacts..."
	@rm -rf htmlcov .coverage coverage.xml
	@rm -rf data/*.json validations/*.json
	@echo "  Removing logs..."
	@rm -f *.log api.log
	@echo "✅ Clean complete"

# Deep clean - removes more files including deployed contracts
clean-all: clean
	@echo "🧹 Deep cleaning..."
	@echo "  Removing deployed contracts record..."
	@rm -f deployed_contracts.json
	@echo "  Removing all contract broadcasts..."
	@rm -rf contracts/broadcast
	@echo "  Removing TEE simulator data..."
	@rm -rf .dstack/data 2>/dev/null || true
	@echo "  Removing temporary files..."
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@find . -type f -name "*.tmp" -delete 2>/dev/null || true
	@find . -type f -name "*.bak" -delete 2>/dev/null || true
	@echo "✅ Deep clean complete"

# Reset environment - clean everything and reset to fresh state
reset: clean-all
	@echo "🔄 Resetting environment to fresh state..."
	@echo "  Removing .env file..."
	@rm -f .env
	@echo "  Creating fresh .env from example..."
	@cp .env.example .env
	@echo "  Environment reset complete!"
	@echo ""
	@echo "📝 Next steps:"
	@echo "  1. make anvil       # Start blockchain"
	@echo "  2. make deploy      # Deploy contracts"
	@echo "  3. make test        # Run tests"
	@echo ""

# Quick test - runs fast tests only
quick-test:
	@echo "⚡ Running quick tests (no slow tests)..."
	flox activate -- python -m pytest tests/ -v --color=yes -m "not slow"

# Test summary - quick overview of all tests
test-summary:
	@echo "📊 Test Suite Summary"
	@echo "===================="
	@echo ""
	@echo "🧪 Unit Tests:"
	@flox activate -- python -m pytest tests/unit/ -q --tb=no
	@echo ""
	@echo "🧪 Integration Tests:"
	@flox activate -- python -m pytest tests/integration/ -q --tb=no --maxfail=3 2>/dev/null || echo "Some integration tests require services"
	@echo ""
	@echo "🧪 API Tests:"
	@flox activate -- python -m pytest tests/api/ -q --tb=no --maxfail=3 2>/dev/null || echo "API tests require server running"
	@echo ""
	@echo "Run 'make test' for full test suite with details"

# Full workflow test
test-workflow:
	@echo "🔄 Running complete workflow test..."
	@make build
	@make deploy
	@make test-e2e

# TEE Simulator commands
tee-setup:
	@echo "🔨 Setting up TEE simulator..."
	flox activate -- ./scripts/setup_tee_simulator.sh setup

tee-start:
	@echo "🚀 Starting TEE simulator..."
	flox activate -- ./scripts/setup_tee_simulator.sh start

tee-stop:
	@echo "🛑 Stopping TEE simulator..."
	flox activate -- ./scripts/setup_tee_simulator.sh stop

tee-restart:
	@echo "🔄 Restarting TEE simulator..."
	flox activate -- ./scripts/setup_tee_simulator.sh restart

tee-status:
	@echo "📊 TEE simulator status..."
	flox activate -- ./scripts/setup_tee_simulator.sh status

tee-logs:
	@echo "📋 TEE simulator logs..."
	flox activate -- ./scripts/setup_tee_simulator.sh logs

# Run TEE integration tests
test-tee:
	@echo "🧪 Running TEE integration tests..."
	flox activate -- python -m pytest tests/integration/test_tee_sdk.py tests/integration/test_tee_simulator.py -v --color=yes