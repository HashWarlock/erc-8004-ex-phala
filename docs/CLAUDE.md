# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ERC-8004 TEE Agent SDK - A streamlined SDK for building trustless agents secured by Trusted Execution Environments (TEE) that interact through the ERC-8004 standard on Base Sepolia. The SDK enables rapid deployment (< 5 minutes) of secure agents with built-in Phala Cloud TEE integration, EIP-712 signing, and blockchain registry interactions.

## Essential Commands

### Development Commands
```bash
# Installation
make install              # Install core dependencies
make install-dev         # Install with dev dependencies
make install-ai          # Install with AI capabilities

# Testing
make test                # Run all tests
make test-unit           # Run unit tests only
make test-integration    # Run integration tests only
pytest tests/unit/test_base.py -v  # Run specific test file

# Code Quality
make lint                # Run linting (flake8, pylint)
make format              # Format code (black, isort)
make type-check          # Run type checking (mypy)

# Development Workflow
make dev                 # Install, lint, and test
make clean               # Remove build artifacts
```

### Running Examples
```bash
# Basic workflow example
make example-basic
# or
cd examples/basic_workflow && python run.py

# AI-enhanced agent example
make example-ai
# or
cd examples/ai_enhanced && python run.py

# All examples
make examples
```

### Agent Setup & Deployment
```bash
# Interactive setup wizard
make setup               # python scripts/quick_setup.py

# Deploy agent to Phala Cloud
make deploy              # python scripts/deploy_agent.py

# Register agent with ERC-8004
make register            # python scripts/register_agent.py
```

## Architecture Overview

### Core Components (src/agent/)

**BaseAgent** ([src/agent/base.py](src/agent/base.py))
- Abstract base class for all agents with plugin system
- Handles agent lifecycle: registration, attestation, signing
- Provides registry interactions and status management
- Factory function `create_agent()` for template instantiation

**TEEAuthenticator** ([src/agent/tee_auth.py](src/agent/tee_auth.py))
- Secure key derivation using dstack SDK
- Generates TEE attestations via `get_quote()`
- Supports both TEE and development (private key) modes
- **Critical**: Uses corrected dstack SDK patterns (see DSTACK_SDK_CORRECTIONS.md)

**RegistryClient** ([src/agent/registry.py](src/agent/registry.py))
- Manages ERC-8004 contract interactions
- Handles agent registration, reputation, and validation
- Web3 integration for blockchain operations

**EIP712Signer** ([src/agent/eip712.py](src/agent/eip712.py))
- Implements typed data signing (EIP-712)
- Domain-specific signatures for trustless verification

### Agent Templates (src/templates/)

Four ready-to-use templates in `src/templates/`:
- **ServerAgent**: Market analysis and data processing tasks
- **ValidatorAgent**: Validation services with configurable rules
- **ClientAgent**: Feedback and reputation management
- **CustomAgent**: Minimal template for custom agent logic

All templates extend `BaseAgent` and implement:
- `process_task(task_data)` - Main agent logic
- `_create_agent_card()` - Agent capabilities description

### Configuration Pattern

All agents use dataclass-based configuration:
```python
AgentConfig(
    domain="agent.example.com",
    salt="unique-salt-value",
    role=AgentRole.SERVER,  # SERVER, VALIDATOR, CLIENT, CUSTOM
    rpc_url="https://sepolia.base.org",
    chain_id=84532,
    use_tee_auth=True,  # False for dev mode
    tee_endpoint=None   # Auto-detected from env
)

RegistryAddresses(
    identity="0x...",    # Base Sepolia addresses
    reputation="0x...",
    validation="0x...",
    tee_verifier="0x..."
)
```

## Critical Implementation Details

### dstack SDK Usage (IMPORTANT!)

The TEE integration uses corrected dstack SDK patterns. **Always reference [DSTACK_SDK_CORRECTIONS.md](DSTACK_SDK_CORRECTIONS.md)** when working with TEE code:

1. **Client Initialization**: Use `DstackClient(url)` for simulator (HTTP), `DstackClient()` for production socket
2. **Key Derivation**: Use `client.get_key(path, purpose)` then `key_result.decode_key()` to get bytes
3. **Attestation**: `get_quote()` requires exactly 64 bytes of application data
4. **Key Path Format**: Use `wallet/erc8004-{domain}` pattern

See [src/agent/tee_auth.py:80-114](src/agent/tee_auth.py#L80-L114) for reference implementation.

### Environment Variables

Required for TEE development:
```bash
# Development with simulator
DSTACK_SIMULATOR_ENDPOINT=http://localhost:8090

# Blockchain
RPC_URL=https://sepolia.base.org
CHAIN_ID=84532

# Optional: AI capabilities
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Agent Lifecycle

1. **Initialize**: Create agent with config and registries
2. **Register**: Call `agent.register()` to register on-chain
3. **Attest**: Get TEE attestation via `agent.get_attestation()`
4. **Process**: Implement `process_task()` for agent-specific logic
5. **Sign**: Use `agent.sign_message()` for EIP-712 signatures

## Testing Strategy

### Test Structure
```
tests/
├── unit/              # Component-level tests
│   ├── test_base.py
│   ├── test_tee_auth.py
│   └── test_registry.py
└── integration/       # Multi-agent workflow tests
    └── test_workflow.py
```

### Running Tests
```bash
# All tests
pytest tests/ -v

# Specific markers
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m tee           # TEE-specific tests
pytest -m blockchain    # Blockchain interaction tests

# With coverage
pytest --cov=src tests/
```

### Test Markers
- `@pytest.mark.unit` - Fast, isolated component tests
- `@pytest.mark.integration` - Multi-component workflows
- `@pytest.mark.tee` - Requires TEE simulator
- `@pytest.mark.blockchain` - Requires RPC connection

## Examples Deep Dive

### Basic Workflow ([examples/basic_workflow/](examples/basic_workflow/))
Demonstrates 3-agent interaction pattern:
1. Client submits task to Server
2. Server processes and returns result
3. Validator verifies result
4. Client submits reputation feedback

### AI Enhanced ([examples/ai_enhanced/](examples/ai_enhanced/))
Shows AI provider integration with:
- Multi-provider support (OpenAI, Anthropic, Google, etc.)
- Fallback mechanisms for reliability
- Context-aware task processing

### Custom Validation ([examples/custom_validation/](examples/custom_validation/))
Implements domain-specific validation:
- Financial data validation
- Security and compliance checks
- Consensus mechanisms

## Development Best Practices

### Async Pattern
All agent operations use async/await:
```python
agent = BaseAgent(config, registries)
agent_id = await agent.register()
attestation = await agent.get_attestation()
result = await agent.process_task(task_data)
```

### Plugin System
Extend agent functionality with plugins:
```python
agent.add_plugin("ai_provider", AIPlugin(...))
ai = agent.get_plugin("ai_provider")
```

### Error Handling
TEE operations may degrade gracefully:
- Development mode: Uses private keys when TEE unavailable
- Attestation failures: Returns error dict with degraded mode indication

### Registry Addresses (Base Sepolia)
Current deployed addresses in examples:
- Identity: `0x000c5A70B7269c5eD4238DcC6576e598614d3f70`
- Reputation: `0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde`
- Validation: `0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d`
- TEE Verifier: `0x1b841e88ba786027f39ecf9Cd160176b22E3603c`

## Package Structure

```
erc-8004-tee-agents/
├── src/agent/           # Core SDK components
│   ├── base.py         # BaseAgent + factory
│   ├── tee_auth.py     # TEE integration
│   ├── registry.py     # ERC-8004 contracts
│   └── eip712.py       # Signing utilities
├── src/templates/       # Agent templates
├── examples/           # Working examples
├── tests/             # Test suite
├── scripts/           # Developer tools
├── docs/              # Additional documentation
├── Makefile           # Command shortcuts
├── setup.py           # Package configuration
└── requirements.txt   # Dependencies
```

## Key Files Reference

- [README.md](README.md) - User-facing documentation and quick start
- [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md) - Design decisions and refactoring history
- [DSTACK_SDK_CORRECTIONS.md](DSTACK_SDK_CORRECTIONS.md) - Critical TEE integration corrections
- [setup.py](setup.py) - Package metadata and dependencies
- [pytest.ini](pytest.ini) - Test configuration
- [Makefile](Makefile) - Development command shortcuts

## Common Workflows

### Creating a New Agent Template
1. Extend `BaseAgent` in `src/templates/`
2. Implement `process_task()` and `_create_agent_card()`
3. Add factory case in `base.py:create_agent()`
4. Create example in `examples/`
5. Add tests in `tests/unit/`

### Adding New Registry Interactions
1. Add method to `RegistryClient` ([src/agent/registry.py](src/agent/registry.py))
2. Expose via `BaseAgent` if needed
3. Add integration test
4. Update examples if applicable

### Troubleshooting TEE Issues
1. Check simulator is running: `curl http://localhost:8090/health`
2. Verify environment: `echo $DSTACK_SIMULATOR_ENDPOINT`
3. Review [DSTACK_SDK_CORRECTIONS.md](DSTACK_SDK_CORRECTIONS.md)
4. Test in dev mode: `use_tee_auth=False`

## Task Master Integration

This project has Task Master AI setup. See [.taskmaster/CLAUDE.md](.taskmaster/CLAUDE.md) for task management commands and workflows.

## Dependencies

Core:
- `web3>=6.0.0` - Blockchain interactions
- `eth-account>=0.8.0` - Account management
- `dstack-sdk>=0.1.0` - TEE operations
- `aiohttp>=3.8.0` - Async HTTP
- `pydantic>=2.0.0` - Data validation

Optional AI:
- `openai>=1.0.0`, `anthropic>=0.3.0`, `crewai>=0.1.0`

Dev:
- `pytest>=7.0.0`, `pytest-asyncio>=0.21.0`
- `black>=23.0.0`, `flake8>=6.0.0`, `mypy>=1.0.0`

## Resources

- [ERC-8004 Standard](https://eips.ethereum.org/EIPS/eip-8004)
- [Phala Network Documentation](https://docs.phala.network)
- [Base Sepolia Explorer](https://sepolia.basescan.org)
- [dstack SDK](https://github.com/Dstack-TEE/dstack)