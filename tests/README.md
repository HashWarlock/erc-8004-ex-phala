# Test Suite Organization

## Structure

```
tests/
├── __init__.py           # Test package initialization
├── conftest.py           # Shared fixtures and configuration
├── unit/                 # Unit tests (no external dependencies)
│   └── test_base_agent.py
├── integration/          # Integration tests (may require services)
│   ├── test_agents.py
│   ├── test_contract_basic.py
│   ├── test_contracts.py
│   ├── test_server_agent.py
│   ├── test_tee_sdk.py
│   ├── test_tee_simulator.py
│   └── test_validator_agent.py
└── e2e/                  # End-to-end tests (full workflow)
    └── test_workflow.py
```

## Running Tests

```bash
# Run all tests
make test

# Run specific test categories
make test-unit      # Unit tests only
make test-int       # Integration tests only
make test-e2e       # End-to-end tests only
make test-tee       # TEE simulator tests only

# Run with coverage
make test-cov

# Run specific test file
make test-file FILE=tests/integration/test_contracts.py
```

## Test Categories

### Unit Tests
- Fast, isolated tests
- No external dependencies
- Mock external services
- Focus on individual functions/methods

### Integration Tests
- Test component interactions
- May require local services (Anvil, TEE simulator)
- Test contract deployments and agent behaviors
- TEE SDK integration with simulator

### End-to-End Tests
- Complete workflow testing
- Full agent lifecycle
- Multi-component orchestration
- Production-like scenarios

## Prerequisites

### For Contract Tests
```bash
# Start Anvil blockchain
make anvil

# Deploy contracts
make deploy
```

### For TEE Tests
```bash
# Setup and start TEE simulator
make tee-setup
make tee-start

# Check status
make tee-status
```

## Test Markers

Tests are marked with pytest markers for selective execution:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Long-running tests
- `@pytest.mark.tee` - TEE-specific tests

## Writing New Tests

1. Place tests in appropriate directory based on scope
2. Use fixtures from `conftest.py` for common setup
3. Add appropriate markers for test categorization
4. Follow naming convention: `test_*.py` for test files
5. Use descriptive test function names: `test_<feature>_<scenario>`

## Continuous Integration

Tests are designed to run in CI/CD pipelines with:
- Automatic service startup (Anvil, TEE simulator)
- Parallel test execution where possible
- Coverage reporting
- Failure notifications