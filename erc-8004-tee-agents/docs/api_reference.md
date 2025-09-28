# API Reference

Complete API documentation for the ERC-8004 TEE Agent SDK.

## Table of Contents

- [Core Classes](#core-classes)
  - [BaseAgent](#baseagent)
  - [AgentConfig](#agentconfig)
  - [RegistryAddresses](#registryaddresses)
- [Authentication](#authentication)
  - [TEEAuthenticator](#teeauthenticator)
- [Registry Operations](#registry-operations)
  - [RegistryClient](#registryclient)
- [Signing](#signing)
  - [EIP712Signer](#eip712signer)
- [Templates](#templates)
  - [ServerAgent](#serveragent)
  - [ValidatorAgent](#validatoragent)
  - [ClientAgent](#clientagent)
- [Utilities](#utilities)

---

## Core Classes

### BaseAgent

Abstract base class for all TEE agents.

```python
from src.agent.base import BaseAgent, AgentConfig, AgentRole

class BaseAgent:
    """Abstract base class for TEE agents."""

    def __init__(self, config: AgentConfig, registries: RegistryAddresses)
```

#### Methods

##### `register() -> int`
Register the agent with the ERC-8004 Identity Registry.

```python
agent_id = await agent.register()
```

**Returns:** Agent ID from the registry

**Raises:** `RegistrationError` if registration fails

##### `process_task(task_data: Dict[str, Any]) -> Dict[str, Any]`
Abstract method to process incoming tasks. Must be implemented by subclasses.

```python
async def process_task(self, task_data):
    # Your implementation
    return {'status': 'completed', 'result': ...}
```

**Parameters:**
- `task_data`: Dictionary containing task information

**Returns:** Dictionary with processing results

##### `get_attestation() -> Dict[str, Any]`
Get TEE attestation for the agent.

```python
attestation = await agent.get_attestation()
```

**Returns:** Dictionary containing:
- `quote`: TEE quote bytes
- `event_log`: Event log data
- `timestamp`: Attestation timestamp

##### `sign_message(message: Dict[str, Any]) -> str`
Sign a message using EIP-712.

```python
signature = await agent.sign_message({
    'type': 'AgentMessage',
    'data': 'Hello World'
})
```

**Parameters:**
- `message`: Message dictionary to sign

**Returns:** Hex signature string

##### `add_plugin(name: str, plugin: Any)`
Add a plugin to extend agent functionality.

```python
agent.add_plugin('ai_analyzer', AIAnalyzer())
```

##### `get_plugin(name: str) -> Any`
Retrieve a registered plugin.

```python
ai_plugin = agent.get_plugin('ai_analyzer')
```

---

### AgentConfig

Configuration dataclass for agent initialization.

```python
@dataclass
class AgentConfig:
    domain: str                    # Agent's domain (e.g., "my-agent.example.com")
    salt: str                      # Unique salt for key derivation
    role: AgentRole               # Agent role (SERVER, VALIDATOR, CLIENT)
    rpc_url: str                  # Blockchain RPC endpoint
    chain_id: int                 # Chain ID (84532 for Base Sepolia)
    use_tee_auth: bool = False    # Enable TEE authentication
    private_key: Optional[str] = None  # Fallback private key (dev mode)
```

#### Example Usage

```python
config = AgentConfig(
    domain="market-analyzer.ai",
    salt="unique-salt-123",
    role=AgentRole.SERVER,
    rpc_url="https://sepolia.base.org",
    chain_id=84532,
    use_tee_auth=True
)
```

---

### AgentRole

Enumeration of agent roles.

```python
class AgentRole(Enum):
    SERVER = "server"       # Provides services
    VALIDATOR = "validator" # Validates data/operations
    CLIENT = "client"       # Requests services, provides feedback
```

---

### RegistryAddresses

Container for ERC-8004 registry contract addresses.

```python
@dataclass
class RegistryAddresses:
    identity: str      # Identity registry address
    reputation: str    # Reputation registry address
    validation: str    # Validation registry address
    tee_verifier: str  # TEE verifier contract address
```

#### Default Addresses (Base Sepolia)

```python
registries = RegistryAddresses(
    identity="0x000c5A70B7269c5eD4238DcC6576e598614d3f70",
    reputation="0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde",
    validation="0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d",
    tee_verifier="0x1b841e88ba786027f39ecf9Cd160176b22E3603c"
)
```

---

## Authentication

### TEEAuthenticator

Handles TEE-based authentication and key derivation.

```python
from src.agent.tee_auth import TEEAuthenticator

class TEEAuthenticator:
    def __init__(self, domain: str, salt: str, use_tee: bool = True)
```

#### Methods

##### `derive_address() -> str`
Derive agent's Ethereum address.

```python
address = await authenticator.derive_address()
```

**Returns:** Ethereum address (0x-prefixed)

##### `get_attestation() -> Dict[str, Any]`
Generate TEE attestation.

```python
attestation = await authenticator.get_attestation()
```

**Returns:** Dictionary with attestation data

##### `sign_with_tee(message_hash: bytes) -> bytes`
Sign a message hash using TEE-derived key.

```python
signature = await authenticator.sign_with_tee(message_hash)
```

**Parameters:**
- `message_hash`: 32-byte message hash

**Returns:** Signature bytes

---

## Registry Operations

### RegistryClient

Manages interactions with ERC-8004 registry contracts.

```python
from src.agent.registry import RegistryClient

class RegistryClient:
    def __init__(self, registries: RegistryAddresses, web3_provider)
```

#### Methods

##### `register_agent(agent_card: Dict) -> int`
Register an agent with the Identity Registry.

```python
agent_id = await registry.register_agent({
    'domain': 'my-agent.com',
    'address': '0x...',
    'metadata': {...}
})
```

**Parameters:**
- `agent_card`: Agent registration data

**Returns:** Agent ID

##### `submit_feedback(agent_id: int, rating: int, comment: str)`
Submit feedback for an agent.

```python
await registry.submit_feedback(
    agent_id=1,
    rating=5,
    comment="Excellent service"
)
```

##### `request_validation(data_hash: str, validator_id: int)`
Request validation from a validator agent.

```python
validation_id = await registry.request_validation(
    data_hash="0x...",
    validator_id=2
)
```

##### `submit_validation_response(request_id: int, is_valid: bool, attestation: Dict)`
Submit validation response.

```python
await registry.submit_validation_response(
    request_id=1,
    is_valid=True,
    attestation={...}
)
```

---

## Signing

### EIP712Signer

Handles EIP-712 typed data signing.

```python
from src.agent.signing import EIP712Signer

class EIP712Signer:
    def __init__(self, domain_name: str, version: str, chain_id: int)
```

#### Methods

##### `sign_typed_data(message: Dict, private_key: bytes) -> str`
Sign typed data according to EIP-712.

```python
signature = signer.sign_typed_data(
    message={'type': 'Message', 'content': 'Hello'},
    private_key=private_key_bytes
)
```

**Parameters:**
- `message`: Message dictionary
- `private_key`: Private key bytes

**Returns:** Hex signature

##### `get_domain_separator() -> bytes`
Get the EIP-712 domain separator.

```python
domain_separator = signer.get_domain_separator()
```

---

## Templates

### ServerAgent

Template for server agents that provide services.

```python
from src.templates.server_agent import ServerAgent

class ServerAgent(BaseAgent):
    """Server agent template for service providers."""

    async def process_task(self, task_data: Dict) -> Dict
```

#### Features
- Market analysis capabilities
- Data processing
- Service provision
- Optional AI enhancement

#### Example

```python
class MarketAnalyzer(ServerAgent):
    async def process_task(self, task_data):
        analysis = await self.analyze_market(task_data['asset'])
        return {
            'status': 'completed',
            'analysis': analysis,
            'confidence': 0.95
        }
```

---

### ValidatorAgent

Template for validator agents.

```python
from src.templates.validator_agent import ValidatorAgent

class ValidatorAgent(BaseAgent):
    """Validator agent template."""

    async def validate_data(self, data: Dict) -> bool
    async def validate_computation(self, computation: Dict) -> bool
```

#### Features
- Data validation
- Computation verification
- Integrity checks
- Attestation generation

#### Example

```python
class DataValidator(ValidatorAgent):
    async def validate_data(self, data):
        # Custom validation logic
        is_valid = self.check_integrity(data)
        return is_valid
```

---

### ClientAgent

Template for client agents that request services.

```python
from src.templates.client_agent import ClientAgent

class ClientAgent(BaseAgent):
    """Client agent template."""

    async def request_service(self, service_type: str, data: Dict)
    async def submit_feedback(self, agent_id: int, rating: int)
```

#### Features
- Service requests
- Feedback submission
- Result processing
- Rating management

---

## Utilities

### Configuration Loading

```python
from src.utils.config import load_config

config = load_config('.env')
```

### Cryptographic Utilities

```python
from src.utils.crypto import (
    generate_keypair,
    hash_message,
    verify_signature
)

# Generate new keypair
private_key, public_key = generate_keypair()

# Hash message
message_hash = hash_message(b"Hello World")

# Verify signature
is_valid = verify_signature(message, signature, public_key)
```

### Network Utilities

```python
from src.utils.network import (
    get_web3_provider,
    wait_for_transaction,
    estimate_gas
)

# Get Web3 provider
w3 = get_web3_provider("https://sepolia.base.org")

# Wait for transaction
receipt = await wait_for_transaction(w3, tx_hash)

# Estimate gas
gas_estimate = await estimate_gas(w3, transaction)
```

---

## Error Handling

### Custom Exceptions

```python
from src.agent.exceptions import (
    RegistrationError,
    TEEError,
    ValidationError,
    SigningError
)

try:
    await agent.register()
except RegistrationError as e:
    print(f"Registration failed: {e}")
```

### Error Codes

| Code | Description |
|------|-------------|
| `REG001` | Registration failed |
| `TEE001` | TEE attestation error |
| `VAL001` | Validation failed |
| `SIG001` | Signing error |
| `NET001` | Network error |

---

## Async/Await Patterns

All SDK methods are async and should be awaited:

```python
import asyncio

async def main():
    # Create agent
    agent = MyAgent(config, registries)

    # Register agent
    agent_id = await agent.register()

    # Process task
    result = await agent.process_task(task_data)

    # Get attestation
    attestation = await agent.get_attestation()

# Run async function
asyncio.run(main())
```

---

## Plugin System

Extend agents with plugins:

```python
class CustomPlugin:
    def __init__(self, agent):
        self.agent = agent

    async def process(self, data):
        # Custom processing
        return enhanced_data

# Add plugin to agent
agent.add_plugin('custom', CustomPlugin(agent))

# Use plugin
plugin = agent.get_plugin('custom')
result = await plugin.process(data)
```

---

## Testing

### Unit Testing

```python
import pytest
from src.agent.base import AgentConfig, AgentRole

@pytest.mark.asyncio
async def test_agent_registration():
    config = AgentConfig(...)
    agent = TestAgent(config, registries)
    agent_id = await agent.register()
    assert agent_id > 0
```

### Mocking TEE

```python
from unittest.mock import AsyncMock

mock_tee = AsyncMock()
mock_tee.get_attestation.return_value = {'quote': b'...'}
agent.tee_auth = mock_tee
```

---

## Performance Optimization

### Connection Pooling

```python
from src.utils.network import ConnectionPool

pool = ConnectionPool(max_connections=10)
agent.connection_pool = pool
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_data(key):
    return fetch_data(key)
```

### Batch Operations

```python
# Batch multiple operations
results = await asyncio.gather(
    agent.process_task(task1),
    agent.process_task(task2),
    agent.process_task(task3)
)
```

---

## Best Practices

1. **Always use async/await** for SDK methods
2. **Handle errors gracefully** with try/except blocks
3. **Use environment variables** for configuration
4. **Implement proper logging** for debugging
5. **Test with TEE simulator** before production
6. **Use plugins** for extensibility
7. **Cache frequently accessed data**
8. **Batch operations** when possible

---

## Migration Guide

For users migrating from the old codebase:

### Old Pattern
```python
# Old way
from agents.base_agent import BaseAgent
agent = BaseAgent(private_key=key)
```

### New Pattern
```python
# New way
from src.agent.base import BaseAgent, AgentConfig
config = AgentConfig(...)
agent = MyAgent(config, registries)
```

---

## Support

For additional help:
- 📚 [Examples](../examples/)
- 🚀 [Quickstart Guide](quickstart.md)
- 🛠️ [Deployment Guide](deployment_guide.md)
- 💬 [Community Discord](https://discord.gg/...)
- 🐛 [Issue Tracker](https://github.com/...)