# Testing Guide

## Overview

Comprehensive testing suite covering unit, integration, and end-to-end tests for the ERC-8004 Trustless Agents system. All tests run against real simulators (Anvil blockchain and dstack TEE simulator) without using mock data to ensure realistic testing conditions.

## Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for agent interactions
├── e2e/           # End-to-end workflow tests
├── api/           # API endpoint tests
└── conftest.py    # Shared pytest fixtures
```

## Prerequisites

### Required Simulators

All tests require real simulators to be running:

1. **Anvil Blockchain** (Required for all tests)
   ```bash
   make anvil
   # Runs in foreground - keep this terminal open
   ```

2. **TEE Simulator** (Required for TEE tests)
   ```bash
   make tee-start
   # Verify it's running:
   ls .dstack/sdk/simulator/dstack.sock
   ```

3. **Deploy Contracts** (Required for integration tests)
   ```bash
   make deploy
   ```

### Automatic Simulator Management

Tests will automatically check for running simulators and provide clear error messages if they're not available. Tests requiring unavailable simulators will be skipped.

## Running Tests

### Quick Start - Complete Process

```bash
# Terminal 1: Start Anvil blockchain
make anvil
# Leave this running

# Terminal 2: Start TEE simulator (optional, for TEE tests)
make tee-start
# Leave this running

# Terminal 3: Deploy contracts and run tests
# First ensure you have a .env file
cp .env.example .env  # If .env doesn't exist

# Deploy contracts (required for integration tests)
make deploy

# Run all tests
make test

# Or run specific test suites
make test-unit    # Unit tests only (no contracts needed)
make test-int     # Integration tests (requires deployed contracts)
make test-e2e     # End-to-end tests (requires all services)
make test-tee     # TEE-specific tests (requires TEE simulator)
```

### Alternative: Direct pytest with Flox

```bash
# If you prefer running pytest directly
flox activate -- pytest tests/ -v

# Or specific test directories
flox activate -- pytest tests/unit/ -v
flox activate -- pytest tests/integration/ -v
```

### Detailed Test Commands

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# E2E tests
pytest tests/e2e/ -v

# API tests
pytest tests/api/ -v

# With coverage
pytest --cov=agents --cov=api --cov-report=html

# Parallel execution
pytest -n auto
```

## Test Categories

### Unit Tests

#### Base Agent Tests (`test_base_agent.py`)
- Agent initialization
- Contract loading
- Registration methods
- Error handling

#### EIP-712 Signer Tests (`test_eip712_signer.py`)
- Domain separator creation
- Message type definitions
- Signature creation and verification
- TEE signer functionality

### Integration Tests

#### Contract Integration (`test_contracts.py`)
- Contract deployment
- Agent registration flow
- Cross-contract interactions

#### Agent Integration (`test_agents.py`)
- Server-Validator interaction
- Client feedback flow
- Complete agent workflows

#### TEE Integration (`test_tee_integration.py`)
- TEE key derivation
- Attestation generation
- TEE-enabled agent operations

### End-to-End Tests

#### Complete Workflow (`test_workflow.py`)
```python
def test_complete_workflow():
    # 1. Deploy contracts
    # 2. Register agents
    # 3. Request analysis
    # 4. Validate work
    # 5. Submit feedback
    # 6. Verify reputation
```

### API Tests

#### API Endpoints (`test_api.py`)
- Health checks
- Authentication
- Agent endpoints
- WebSocket connections

## Test Fixtures

### Common Fixtures (`conftest.py`)

All fixtures connect to real simulators - no mocking:

```python
@pytest.fixture
def simulator_manager():
    """Manages simulator instances for testing"""
    # Ensures Anvil and TEE simulators are running
    # Deploys contracts if needed

@pytest.fixture
def w3(simulator_manager):
    """Web3 instance connected to real Anvil blockchain"""
    return get_test_web3()

@pytest.fixture
def tee_client(simulator_manager):
    """TEE client connected to real dstack simulator"""
    return get_test_tee_client()

@pytest.fixture
def deployed_contracts():
    """Load actually deployed contracts from Anvil"""
    # Returns real contract addresses

@pytest.fixture
def test_agents(deployed_contracts):
    """Initialize agents with real blockchain connection"""
    # Creates agents connected to real simulators
```

## Simulator-Based Testing

### No Mock Data Policy

All tests must use real simulators:
- **Blockchain interactions**: Real Anvil instance
- **TEE operations**: Real dstack simulator
- **Contract calls**: Actually deployed contracts
- **Agent operations**: Real transactions on test chain

### Test Utilities

```python
from tests.test_utils import (
    SimulatorManager,      # Manages simulator lifecycle
    get_test_web3,        # Get real Web3 connection
    get_test_tee_client,  # Get real TEE client
    fund_account,         # Fund test accounts with ETH
    require_simulators    # Decorator to ensure simulators running
)
```

### Test Data

```python
# Test accounts
TEST_ACCOUNTS = {
    "server": "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
    "validator": "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
    "client": "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a"
}

# Test analysis data
TEST_ANALYSIS = {
    "symbol": "BTC",
    "timeframe": "1d",
    "trend": "bullish",
    "confidence": 85
}
```

## Test Environment Setup

### Local Blockchain

```bash
# Start Anvil with test configuration
anvil --fork-url $FORK_URL \
      --chain-id 31337 \
      --accounts 10 \
      --balance 1000
```

### TEE Simulator

```bash
# Start dstack simulator
make tee-start

# Verify simulator
curl http://localhost:8080/health
```

## Test Coverage

### Coverage Requirements

- Unit tests: > 80% coverage
- Integration tests: > 70% coverage
- Critical paths: 100% coverage

### Generate Coverage Report

```bash
# Run with coverage
pytest --cov=agents --cov=api \
       --cov-report=html \
       --cov-report=term

# View HTML report
open htmlcov/index.html
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: pytest --cov
```

## Performance Testing

### Load Testing

```python
# tests/performance/test_load.py
import asyncio
import aiohttp

async def test_api_load():
    """Test API under load"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(100):
            task = session.get("http://localhost:8000/health")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        assert all(r.status == 200 for r in responses)
```

### Gas Usage Testing

```python
def test_gas_usage():
    """Test contract gas consumption"""
    tx = agent.register_agent()
    receipt = w3.eth.wait_for_transaction_receipt(tx)
    
    assert receipt.gasUsed < 200000  # Max gas limit
```

## Debugging Tests

### Verbose Output

```bash
# Show detailed output
pytest -vvv

# Show print statements
pytest -s

# Debug specific test
pytest tests/unit/test_base_agent.py::test_agent_initialization -vvs
```

### Interactive Debugging

```python
def test_with_debugging():
    import pdb; pdb.set_trace()  # Breakpoint
    # Test code here
```

## Test Best Practices

1. **Isolation**: Each test should be independent
2. **Deterministic**: Tests should produce same results
3. **Fast**: Unit tests < 1s, Integration < 10s
4. **Clear**: Test names describe what they test
5. **Comprehensive**: Cover edge cases and errors

## Common Test Patterns

### Testing Async Functions

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

### Testing Blockchain Interactions

```python
def test_contract_interaction(w3, deployed_contracts):
    # Take snapshot
    snapshot = w3.provider.make_request("evm_snapshot", [])
    
    try:
        # Test contract interaction
        tx = contract.function().transact()
        w3.eth.wait_for_transaction_receipt(tx)
    finally:
        # Revert to snapshot
        w3.provider.make_request("evm_revert", [snapshot])
```

### Testing with Time

```python
def test_time_dependent(w3):
    # Fast forward time
    w3.provider.make_request("evm_increaseTime", [3600])
    w3.provider.make_request("evm_mine", [])
    
    # Test time-dependent logic
```

## Troubleshooting

### Common Issues

1. **Deploy fails with "BASESCAN_API_KEY not found"**
   - Solution: The Makefile now provides dummy values for local deployment
   - If still failing, ensure you're using the latest Makefile

2. **Deploy fails with "PRIVATE_KEY not found"**
   - Solution: Copy .env.example to .env: `cp .env.example .env`
   - The example includes Anvil's default private key for testing

3. **Tests fail with "Contract not deployed"**
   - Solution: Run `make deploy` after starting Anvil
   - Ensure Anvil is running: `curl http://127.0.0.1:8545`

4. **Import Errors**: Ensure project root in PYTHONPATH
   - Solution: Run tests from project root with `make test`

5. **TEE Connection Failed**: Start simulator with `make tee-start`
   - TEE tests will skip if simulator not running

6. **Timeout Errors**: Increase pytest timeout
   - Solution: `pytest --timeout=60`

7. **"make: command not found" errors**
   - Ensure you're in the project root directory
   - Check that Makefile exists: `ls Makefile`

### Debug Commands

```bash
# List available fixtures
pytest --fixtures

# Show test collection
pytest --collect-only

# Run failed tests only
pytest --lf

# Run tests matching pattern
pytest -k "test_agent"
```