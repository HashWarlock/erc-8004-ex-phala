# Testing Guide

## Overview

Comprehensive testing suite covering unit, integration, and end-to-end tests for the ERC-8004 Trustless Agents system with Phala Cloud TEE integration. All tests support both traditional key-based and TEE-based authentication modes.

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

### Required Services

1. **Anvil Blockchain** (Required for all tests)
   ```bash
   flox activate -- make anvil
   # Runs in foreground - keep this terminal open
   ```

2. **Deploy Contracts** (Required for integration tests)
   ```bash
   flox activate -- make deploy
   # This also funds TEE wallets if USE_TEE_AUTH=true
   ```

3. **TEE Simulator** (Auto-started when USE_TEE_AUTH=true)
   ```bash
   # Manually start if needed:
   flox activate -- make tee-start
   
   # Verify it's running:
   flox activate -- make tee-status
   ```

### Automatic Simulator Management

Tests will automatically check for running simulators and provide clear error messages if they're not available. Tests requiring unavailable simulators will be skipped.

## Running Tests

### Quick Start - Complete Process

```bash
# Terminal 1: Start Anvil blockchain
flox activate -- make anvil
# Leave this running

# Terminal 2: Deploy and test
# Copy environment configuration
cp .env.example .env  # If .env doesn't exist

# Deploy contracts (auto-funds TEE wallets if enabled)
flox activate -- make deploy

# Run end-to-end test
flox activate -- make test-e2e

# Or run the complete demo
flox activate -- ./run_demo.sh

# Test with TEE mode explicitly
USE_TEE_AUTH=true flox activate -- make test-e2e
```

### Running Different Test Suites

```bash
# Unit tests (no blockchain needed)
flox activate -- make test-unit

# Integration tests (requires blockchain and contracts)
flox activate -- make test-int

# End-to-end tests (complete workflow)
flox activate -- make test-e2e

# TEE-specific tests
USE_TEE_AUTH=true flox activate -- make test-tee

# All tests with coverage
flox activate -- make test-cov
```

### Test Commands Reference

```bash
# Run specific test file
flox activate -- python -m pytest tests/integration/test_tee_integration.py -v

# Run tests matching pattern
flox activate -- python -m pytest -k "test_tee" -v

# Run with detailed output
flox activate -- python -m pytest -vvs

# Run failed tests only
flox activate -- python -m pytest --lf

# Parallel execution (faster)
flox activate -- python -m pytest -n auto
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

#### TEE Integration (`test_tee_integration.py`, `test_phala_deployment.py`)
- TEE key derivation with deterministic addresses
- Automatic wallet funding for TEE agents
- TEE-enabled agent operations
- Phala Cloud deployment testing

### End-to-End Tests

#### Complete Workflow (`test_workflow.py`, `test_simple.py`)
```python
def test_complete_workflow():
    # 1. Initialize agents (TEE or traditional)
    # 2. Auto-fund wallets if needed
    # 3. Register agents on blockchain
    # 4. Request market analysis
    # 5. Validate work
    # 6. Submit feedback
    # 7. Verify reputation updates
```

### API Tests

#### API Endpoints (`test_api.py`)
- Health checks
- Authentication
- Agent endpoints
- WebSocket connections

## Test Fixtures

### Common Fixtures

```python
@pytest.fixture
def w3():
    """Web3 instance connected to Anvil blockchain"""
    return Web3(Web3.HTTPProvider("http://localhost:8545"))

@pytest.fixture
def deployed_contracts():
    """Load deployed contract addresses"""
    with open("deployed_contracts.json") as f:
        return json.load(f)

@pytest.fixture
def test_agents(deployed_contracts):
    """Initialize agents based on USE_TEE_AUTH setting"""
    if os.getenv("USE_TEE_AUTH", "false").lower() == "true":
        # Create TEE agents with deterministic keys
        return create_tee_agents()
    else:
        # Create traditional agents with private keys
        return create_traditional_agents()
```

## Simulator-Based Testing

### Testing Modes

#### Traditional Mode (USE_TEE_AUTH=false)
- Uses private keys from .env file
- Direct wallet control
- Simpler setup for development

#### TEE Mode (USE_TEE_AUTH=true)
- Deterministic key derivation
- Automatic wallet funding
- Production-like security model
- Requires TEE simulator

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

### Test Configuration

```python
# TEE Agent Configuration (deterministic)
TEE_AGENTS = {
    "server": {
        "domain": "alice.example.com",
        "salt": "server-secret-salt-2024",
        "address": "0xC6aB3F953c7F0B33B1E9056Fa6f795B329c3323D"
    },
    "validator": {
        "domain": "bob.example.com",
        "salt": "validator-secret-salt-2024",
        "address": "0x83247F3B9772D2b0220A08b8fF01E95A28f7423F"
    },
    "client": {
        "domain": "charlie.example.com",
        "salt": "client-secret-salt-2024",
        "address": "0x54AF215206E971ADE501373E0a6Ace7369B5c22d"
    }
}

# Traditional Mode Keys (Anvil defaults)
TRADITIONAL_KEYS = {
    "server": "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
    "validator": "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
    "client": "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a"
}
```

## Test Environment Setup

### Environment Setup

```bash
# Start Anvil blockchain
flox activate -- anvil

# TEE simulator (auto-starts when needed)
# Manual control:
flox activate -- make tee-start
flox activate -- make tee-status
flox activate -- make tee-logs
flox activate -- make tee-stop

# Fund TEE wallets
flox activate -- make tee-fund
# Or use the Python script directly:
flox activate -- python scripts/fund_tee_wallets.py
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

1. **Anvil not running**
   ```bash
   # Start in separate terminal
   flox activate -- make anvil
   ```

2. **Contracts not deployed**
   ```bash
   flox activate -- make deploy
   ```

3. **TEE wallets not funded**
   ```bash
   # Auto-funds during deploy, or manually:
   flox activate -- make tee-fund
   ```

4. **DomainAlreadyRegistered error**
   - Tests now add unique timestamps to prevent this
   - If persists, restart Anvil and redeploy

5. **AgentNotFound (0xe93ba223) error**
   - Expected when agent isn't registered yet
   - Tests handle this automatically

6. **Import errors**
   ```bash
   # Always use flox activate
   flox activate -- python your_test.py
   ```

7. **Test failures after code changes**
   ```bash
   # Reset everything
   flox activate -- make reset
   flox activate -- make anvil  # In separate terminal
   flox activate -- make deploy
   flox activate -- make test
   ```

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