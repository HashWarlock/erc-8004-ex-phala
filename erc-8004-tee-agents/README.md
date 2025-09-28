# ERC-8004 TEE Agent SDK

🚀 **Build trustless agents in under 5 minutes!**

A streamlined, developer-friendly SDK for creating TEE-secured agents that interact through the ERC-8004 standard on Base Sepolia.

## ✨ Features

- **🔐 TEE-Secured**: Built-in Phala Cloud integration for secure key derivation and attestation
- **⚡ Quick Setup**: Deploy your first agent in < 5 minutes
- **📦 Plug-and-Play**: Pre-configured templates for common agent types
- **🔗 ERC-8004 Native**: Full integration with Identity, Reputation, and Validation registries
- **🧠 AI-Ready**: Optional CrewAI integration for intelligent agents
- **🛠️ Developer-First**: Clean APIs, comprehensive docs, working examples

## 🏃 Quick Start

```bash
# Install the SDK
pip install erc-8004-tee-agents

# Set up your first agent (interactive)
erc8004-setup

# Deploy to Phala Cloud
python deploy.py
```

That's it! Your agent is now registered and running. 🎉

## 📚 Installation

### From PyPI (Recommended)
```bash
pip install erc-8004-tee-agents
```

### From Source
```bash
git clone https://github.com/your-org/erc-8004-tee-agents
cd erc-8004-tee-agents
pip install -e .
```

### With AI Capabilities
```bash
pip install erc-8004-tee-agents[ai]
```

## 🎯 Usage Examples

### Create a Simple Agent

```python
from erc8004_tee_agents import BaseAgent, AgentConfig, RegistryAddresses

# Configure your agent
config = AgentConfig(
    domain="my-agent.com",
    salt="unique-salt-123",
    role=AgentRole.SERVER,
    rpc_url="https://sepolia.base.org",
    chain_id=84532
)

# Set registry addresses (Base Sepolia)
registries = RegistryAddresses(
    identity="0x000c5A70B7269c5eD4238DcC6576e598614d3f70",
    reputation="0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde",
    validation="0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d",
    tee_verifier="0x1b841e88ba786027f39ecf9Cd160176b22E3603c"
)

# Create and register agent
agent = BaseAgent(config, registries)
agent_id = await agent.register()
print(f"Agent registered with ID: {agent_id}")

# Get TEE attestation
attestation = await agent.get_attestation()
print(f"TEE Attestation: {attestation['quote'][:50]}...")
```

### Use Agent Templates

```python
from erc8004_tee_agents.templates import ServerAgent

# Use pre-built server agent template
server = ServerAgent(config, registries)
await server.register()

# Process a task
result = await server.process_task({
    "task_id": "123",
    "query": "Analyze market trends"
})
```

## 🏗️ Architecture

```
Your Agent
    ↓
TEE Security (Phala Cloud)
    ↓
ERC-8004 Registries
    ↓
Trustless Network
```

## 📦 What's Included

### Core Components
- `BaseAgent` - Extensible base class for all agents
- `TEEAuthenticator` - Secure key derivation and attestation
- `RegistryClient` - ERC-8004 contract interactions
- `EIP712Signer` - Typed data signing

### Agent Templates
- `ServerAgent` - Market analysis and data processing
- `ValidatorAgent` - Validation services
- `ClientAgent` - Feedback and reputation management
- `CustomAgent` - Minimal template for custom logic

### Developer Tools
- Interactive setup script
- One-click deployment
- Key generation utilities
- Comprehensive examples

## 🛠️ Development

```bash
# Install dev dependencies
make install-dev

# Run tests
make test

# Lint code
make lint

# Format code
make format

# Run examples
make examples
```

## 📖 Documentation

- [Quickstart Guide](docs/quickstart.md)
- [API Reference](docs/api_reference.md)
- [Deployment Guide](docs/deployment_guide.md)
- [Examples](docs/examples.md)

## 🔗 Resources

- [ERC-8004 Standard](https://eips.ethereum.org/EIPS/eip-8004)
- [Phala Network](https://phala.network)
- [Base Sepolia Explorer](https://sepolia.basescan.org)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙋 Support

- Discord: [Join our community](https://discord.gg/erc8004)
- Issues: [GitHub Issues](https://github.com/your-org/erc-8004-tee-agents/issues)
- Docs: [Full Documentation](https://docs.erc8004-agents.dev)

---

Built with ❤️ by the ERC-8004 community