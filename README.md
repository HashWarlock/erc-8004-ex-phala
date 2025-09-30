# ERC-8004 TEE Agents

Production-ready implementation of [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) Trustless Agent Protocol with Intel TDX TEE security via Phala Network's dstack.

## Features

- 🔐 **TEE-Secured Keys** - Deterministic key derivation in Intel TDX enclaves
- 🌐 **ERC-8004 Compliant** - Full agent card generation and protocol compliance
- 🤖 **Multiple Agent Types** - Server, Client, Validator, and Computer Control agents
- 📜 **Remote Attestation** - Cryptographic proof of TEE execution
- 🔗 **On-Chain Registration** - Identity, reputation, and validation registries
- 🖥️ **Computer Control** - System control via aio-sandbox API integration

---

## Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/yourusername/erc-8004-ex-phala
cd erc-8004-ex-phala

# Install dependencies
pip install -e .

# Optional: Computer control capabilities
pip install aio-sandbox
```

### 2. Local Agent Server

Start a TEE-secured agent server locally:

```bash
# Configure
export AGENT_DOMAIN="localhost:8000"
export AGENT_SALT="your-unique-salt-here"

# Start server
./deployment/start_local_agent.sh
```

Access at `http://localhost:8000` with API docs at `/docs`.

### 3. Computer Control Agent

Run agent with system control capabilities:

```bash
# Configure sandbox
export SANDBOX_URL="http://localhost:8080"

# Start computer control agent
python deployment/computer_control_server.py
```

Execute commands via HTTP API:

```bash
curl -X POST http://localhost:8000/api/control \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "test-1",
    "type": "shell",
    "command": "ls -la"
  }'
```

---

## Agent Types

### 1. Server Agent
Market analysis and data processing with TEE security.

```python
from src.templates.server_agent import ServerAgent

agent = ServerAgent(config, registries)
await agent.initialize()
result = await agent.process_task(task_data)
```

### 2. Computer Control Agent
System control via sandbox API integration.

```python
from src.templates.computer_control_agent import ComputerControlAgent

agent = ComputerControlAgent(config, registries, sandbox_url)
await agent.initialize()
result = await agent.process_task({
    "type": "shell",
    "command": "pwd"
})
```

### 3. Validator Agent
Validation and verification services.

```python
from src.templates.validator_agent import ValidatorAgent

agent = ValidatorAgent(config, registries)
await agent.initialize()
result = await agent.validate_task(validation_data)
```

### 4. Client Agent
Task submission and coordination.

```python
from src.templates.client_agent import ClientAgent

agent = ClientAgent(config, registries)
await agent.initialize()
result = await agent.submit_task(task_data)
```

---

## Project Structure

```
erc-8004-ex-phala/
├── src/
│   ├── agent/               # Core agent components
│   │   ├── base.py         # BaseAgent class
│   │   ├── tee_auth.py     # TEE authentication
│   │   ├── registry.py     # Contract interactions
│   │   ├── agent_card.py   # ERC-8004 agent cards
│   │   └── eip712.py       # EIP-712 signing
│   ├── templates/           # Agent templates
│   │   ├── server_agent.py
│   │   ├── computer_control_agent.py
│   │   ├── validator_agent.py
│   │   └── client_agent.py
│   └── utils/              # Utilities
├── deployment/             # Deployment scripts
│   ├── local_agent_server.py
│   ├── computer_control_server.py
│   ├── deploy_production.py
│   ├── check_wallets.py
│   └── start_local_agent.sh
├── examples/               # Example implementations
│   ├── computer_control_demo.py
│   ├── simple_agent_example.py
│   └── basic_workflow/
├── tests/                  # Test suite
│   ├── production/         # Production TEE tests
│   ├── integration/        # Integration tests
│   └── unit/              # Unit tests
└── scripts/               # Utility scripts
    ├── deploy_agent.py
    └── register_agent.py
```

---

## Documentation

📚 **[Complete Documentation](docs/)** - All guides and references

**Quick Links:**
- **[Quick Start](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[Local Agent Guide](docs/LOCAL_AGENT_GUIDE.md)** - Run agent locally with HTTP API
- **[Computer Control Guide](docs/COMPUTER_CONTROL_GUIDE.md)** - System control agent
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Production deployment
- **[Development Guide](docs/CLAUDE.md)** - For developers using Claude Code

---

## TEE Integration

### Key Derivation

Keys are derived deterministically from domain + salt in Intel TDX:

```python
from src.agent.tee_auth import TEEAuthenticator

auth = TEEAuthenticator(
    domain="agent.example.com",
    salt="unique-salt",
    use_tee=True
)

address = await auth.derive_address()
# Same domain + salt = same address (reproducible)
```

### Attestation

Generate remote attestations proving TEE execution:

```python
attestation = await auth.get_attestation()
# Returns ~10KB Intel TDX attestation
```

### Signature Verification

Verify agent signatures cryptographically:

```python
from eth_account import Account
from eth_account.messages import encode_defunct

message = encode_defunct(text="test message")
signature = await auth.sign_with_tee(message)
recovered = Account.recover_message(message, signature=signature)
assert recovered == agent_address
```

---

## Testing

### Run All Tests

```bash
make test
```

### Production TEE Tests

```bash
pytest tests/production/ -v
```

### Integration Tests

```bash
pytest tests/integration/ -v
```

### Demo Scripts

```bash
# Computer control demo
python examples/computer_control_demo.py

# Simple agent example
python examples/simple_agent_example.py

# Basic workflow
python examples/basic_workflow/run.py
```

---

## Configuration

### Environment Variables

```bash
# Agent Identity
AGENT_DOMAIN="localhost:8000"
AGENT_SALT="your-unique-salt-here"
AGENT_TYPE="server"

# Blockchain (Base Sepolia)
RPC_URL="https://sepolia.base.org"
CHAIN_ID="84532"
IDENTITY_REGISTRY_ADDRESS="0x000c5A70B7269c5eD4238DcC6576e598614d3f70"

# TEE
USE_TEE_AUTH="true"

# Sandbox (for computer control)
SANDBOX_URL="http://localhost:8080"

# Server
AGENT_HOST="0.0.0.0"
AGENT_PORT="8000"
```

### Configuration Files

- **`.env.example`** - Template configuration
- **`.env.production`** - Production settings (Base Sepolia)
- **`.env`** - Local development (git-ignored)

---

## ERC-8004 Compliance

### Agent Cards

All agents generate ERC-8004 compliant agent cards:

```python
card = await agent._create_agent_card()

# Card includes:
# - capabilities: List of agent capabilities
# - transport: HTTP/WebSocket configuration
# - trustModels: TEE attestation, reputation
# - infrastructure: Phala Network, Intel TDX
# - registrations: On-chain registry info
# - metadata: Pricing, endpoints, performance
```

### Registry Integration

Interact with ERC-8004 registries on Base Sepolia:

```python
from src.agent.registry import RegistryClient

registry = RegistryClient(config, registries)

# Register agent
agent_id = await registry.register_agent(
    domain="agent.example.com",
    agent_card_url="https://agent.example.com/card"
)

# Get agent info
info = await registry.get_agent_info(agent_id)
```

---

## Development

### Build

```bash
make build
```

### Lint

```bash
make lint
```

### Format

```bash
make format
```

### Clean

```bash
make clean
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Application                        │
│            (Server/Client/Validator/Computer)               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  BaseAgent                                                  │
│  • Task processing                                          │
│  • Agent card generation                                    │
│  • Registry interactions                                    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TEEAuthenticator                                           │
│  • Key derivation                                           │
│  • Message signing                                          │
│  • Attestation generation                                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Intel TDX (via dstack)                                     │
│  • Secure enclave                                           │
│  • Remote attestation                                       │
│  • Key protection                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Base Sepolia (L2)                        │
├─────────────────────────────────────────────────────────────┤
│  • Identity Registry: 0x000c5A70...                         │
│  • Reputation Registry: TBD                                 │
│  • Validation Registry: TBD                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Requirements

- Python 3.9+
- TEE environment (Intel TDX via Phala dstack) or simulator
- Web3 provider (Base Sepolia RPC)
- Optional: aio-sandbox for computer control

---

## License

MIT License - see [LICENSE](LICENSE) file

---

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## Status

✅ **Completed:**
- TEE integration with Intel TDX
- ERC-8004 agent cards
- Multiple agent templates
- Local HTTP servers
- Computer control via sandbox
- Production TEE validation
- Integration testing

⏳ **In Progress:**
- On-chain registration (waiting for contract access)
- Reputation system integration
- Multi-agent coordination

---

## Support

For issues or questions:
- Open an issue on GitHub
- Review documentation in project root
- Check [CLAUDE.md](CLAUDE.md) for development guidance

---

## Links

- **ERC-8004 Standard**: https://eips.ethereum.org/EIPS/eip-8004
- **Phala Network**: https://phala.network
- **dstack**: https://docs.phala.network/tech-specs/dstack
- **Base Sepolia**: https://sepolia.base.org
- **aio-sandbox**: https://sandbox.agent-infra.com
