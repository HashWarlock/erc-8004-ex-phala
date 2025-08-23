# ERC-8004 Trustless Agents Testing Guide

## Table of Contents
1. [Overview](#overview)
2. [Test Architecture](#test-architecture)
3. [Environment Setup](#environment-setup)
4. [Running Tests](#running-tests)
5. [Test Categories](#test-categories)
6. [Reproducing Results](#reproducing-results)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Overview

This testing guide provides comprehensive instructions for testing the ERC-8004 Trustless Agents implementation on Phala Cloud. Our test suite follows industry best practices with clear separation between unit, integration, and end-to-end tests.

### Key Features
- **Modular Test Structure**: Clear separation of test types
- **Reproducible Results**: Deterministic test accounts and data
- **CI/CD Ready**: Automated test execution support
- **Comprehensive Coverage**: Tests for contracts, agents, and workflows

## Test Architecture

```
tests/
├── __init__.py           # Test suite initialization
├── conftest.py          # Shared fixtures and configuration
├── unit/                # Unit tests (no blockchain required)
│   └── test_base_agent.py
├── integration/         # Integration tests (blockchain required)
│   ├── test_contracts.py
│   └── test_agents.py
└── e2e/                # End-to-end workflow tests
    └── test_workflow.py
```

### Test Levels

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions with blockchain
3. **End-to-End Tests**: Test complete user workflows

## Environment Setup

### Prerequisites

1. **Install Flox** (if not already installed):
```bash
curl -L https://flox.sh/install | bash
```

2. **Activate Flox Environment**:
```bash
flox activate
```

3. **Install Test Dependencies**:
```bash
make install
```

### Starting the Test Blockchain

Start Anvil (local Ethereum blockchain):
```bash
make anvil
```

This starts Anvil with deterministic test accounts.

### Deploy Contracts

In a new terminal:
```bash
make deploy
```

This deploys all ERC-8004 registry contracts to the local blockchain.

## Running Tests

### Quick Start

Run all tests:
```bash
make test
```

### Test Categories

#### Unit Tests Only
```bash
make test-unit
```
- Tests individual components
- No blockchain required
- Fast execution (~1 second)

#### Integration Tests Only
```bash
make test-int
```
- Tests blockchain interactions
- Requires running Anvil
- Medium execution time (~10 seconds)

#### End-to-End Tests Only
```bash
make test-e2e
```
- Tests complete workflows
- Requires contracts deployed
- Slower execution (~30 seconds)

### Running Specific Tests

Run a specific test file:
```bash
make test-file FILE=tests/integration/test_agents.py
```

Run tests matching a pattern:
```bash
flox activate -- python -m pytest tests/ -k "test_agent_registration"
```

### Test Coverage

Generate coverage report:
```bash
make test-cov
```

View HTML coverage report:
```bash
open htmlcov/index.html
```

## Test Categories

### Unit Tests (`tests/unit/`)

Test individual components without external dependencies:

- **Base Agent Tests**: Agent initialization, configuration
- **Mock Blockchain**: Uses mocked Web3 connections
- **Fast Execution**: No network calls

Example:
```python
def test_agent_initialization():
    agent = ERC8004BaseAgent(
        agent_domain="test.domain.com",
        private_key="0x" + "1" * 64
    )
    assert agent.agent_domain == "test.domain.com"
```

### Integration Tests (`tests/integration/`)

Test component interactions with real blockchain:

- **Contract Tests**: Registry contract interactions
- **Agent Tests**: Agent registration and operations
- **Real Blockchain**: Requires Anvil running

Example:
```python
def test_agent_registration_flow(w3, test_accounts):
    agent = ERC8004BaseAgent(
        agent_domain="test.com",
        private_key=test_accounts[0]['private_key']
    )
    agent_id = agent.register_agent()
    assert agent_id > 0
```

### End-to-End Tests (`tests/e2e/`)

Test complete user workflows:

- **Full Workflows**: Multi-agent interactions
- **Market Analysis**: Complete analysis cycle
- **Validation Process**: End-to-end validation

Example workflow tested:
1. Register three agents (Server, Validator, Client)
2. Server performs market analysis
3. Server submits work for validation
4. Validator validates the work
5. Client authorizes feedback

## Reproducing Results

### Deterministic Test Environment

Our tests use deterministic accounts for reproducibility:

```python
# Account 0 (Deployer)
Address: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
Private Key: 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

# Account 1 (Alice)
Address: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
Private Key: 0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d

# Account 2 (Bob)
Address: 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC
Private Key: 0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a

# Account 3 (Charlie)
Address: 0x90F79bf6EB2c4f870365E785982E1f101E93b906
Private Key: 0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6
```

### Step-by-Step Reproduction

1. **Clean Environment**:
```bash
make clean
```

2. **Start Fresh Blockchain**:
```bash
# Terminal 1
make anvil
```

3. **Deploy Contracts**:
```bash
# Terminal 2
make deploy
```

4. **Run Full Test Suite**:
```bash
# Terminal 2
make test
```

### Expected Output

Successful test run shows:
```
=================== test session starts ====================
collected 15 items

tests/unit/test_base_agent.py::TestBaseAgentInitialization::test_agent_initialization PASSED
tests/integration/test_contracts.py::TestIdentityRegistry::test_registration_fee PASSED
tests/e2e/test_workflow.py::TestCompleteWorkflow::test_full_market_analysis_workflow PASSED
...

=================== 15 passed in 25.43s ====================
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Blockchain Connection Error
**Error**: `Cannot connect to test blockchain at http://127.0.0.1:8545`

**Solution**:
```bash
# Ensure Anvil is running
make anvil
```

#### 2. Contracts Not Deployed
**Error**: `Contracts not deployed. Run 'make deploy' first.`

**Solution**:
```bash
make deploy
```

#### 3. Agent Already Registered
**Error**: `Agent already registered`

**Solution**: Tests handle this gracefully. The error is expected for repeated runs.

#### 4. API Key Missing (CrewAI)
**Warning**: `LLM analysis failed, using fallback analysis`

**Solution**: Set OpenAI API key for full CrewAI functionality:
```bash
export OPENAI_API_KEY="your-api-key"
```

### Debug Mode

Run tests with verbose output:
```bash
flox activate -- python -m pytest tests/ -vv -s
```

Run with debugging:
```bash
flox activate -- python -m pytest tests/ --pdb
```

## Best Practices

### 1. Test Isolation
- Each test should be independent
- Use fixtures for common setup
- Clean up test data after execution

### 2. Naming Conventions
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### 3. Assertions
- Use clear, specific assertions
- Include descriptive messages
- Test both success and failure cases

### 4. Fixtures
- Use pytest fixtures for reusable setup
- Scope fixtures appropriately (function, class, module, session)
- Document fixture purpose

### 5. Markers
- Use markers to categorize tests:
  - `@pytest.mark.unit`
  - `@pytest.mark.integration`
  - `@pytest.mark.e2e`
  - `@pytest.mark.slow`

### 6. Documentation
- Document test purpose
- Include examples in docstrings
- Explain complex test logic

## Continuous Integration

### GitHub Actions Example

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install Flox
        run: curl -L https://flox.sh/install | bash
      
      - name: Start Anvil
        run: make anvil &
        
      - name: Deploy Contracts
        run: make deploy
        
      - name: Run Tests
        run: make test
        
      - name: Upload Coverage
        run: make test-cov
```

## Performance Benchmarks

Expected test execution times:

| Test Category | Number of Tests | Execution Time |
|--------------|----------------|----------------|
| Unit Tests | 5 | ~1 second |
| Integration Tests | 8 | ~10 seconds |
| E2E Tests | 3 | ~30 seconds |
| **Total** | **16** | **~41 seconds** |

## Contributing

When adding new tests:

1. **Choose the right category** (unit/integration/e2e)
2. **Follow naming conventions**
3. **Add appropriate markers**
4. **Document test purpose**
5. **Ensure reproducibility**
6. **Update this guide if needed**

## Support

For issues or questions:
- Review test output carefully
- Check the [Troubleshooting](#troubleshooting) section
- Consult the main README.md
- Open an issue with test logs

---

*Last updated: 2025-08-23*