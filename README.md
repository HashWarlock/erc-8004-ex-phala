# ERC-8004 Trustless Agents - Phala Cloud Edition

**A complete implementation of the [ERC-8004 Trustless Agents](https://eips.ethereum.org/EIPS/eip-8004) standard with TEE-secured AI Agents using Phala Cloud.**

This project demonstrates how AI agents can interact trustlessly using blockchain registries and Trusted Execution Environment (TEE) security, showcasing the future of decentralized AI collaboration.

## 🎯 Key Features

- **✅ ERC-8004 Registry Contracts**: Complete Identity, Reputation, and Validation registry system
- **✅ TEE Integration**: Phala Cloud TEE for secure key derivation and attestation
- **✅ AI-Powered Agents**: Optional CrewAI integration for sophisticated analysis
- **✅ Trustless Interactions**: Agents discover, validate, and provide feedback without pre-existing trust
- **✅ Complete Audit Trail**: Full blockchain-based accountability
- **✅ Multi-Agent Workflows**: Server, Validator, and Client agents working together

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Server Agent   │    │ Validator Agent │    │  Client Agent   │
│  (TEE-Secured)  │    │                 │    │  (TEE-Secured)  │
│                 │    │                 │    │                 │
│ • Market        │    │ • Validation    │    │ • Feedback      │
│   Analysis      │    │   Services      │    │   Submission    │
│ • TEE           │    │ • Quality       │    │ • TEE           │
│   Attestation   │    │   Assessment    │    │   Attestation   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────┐
                    │  ERC-8004 Registries│
                    │  (Smart Contracts)  │
                    │                     │
                    │ • Identity Registry │
                    │ • Reputation Registry│
                    │ • Validation Registry│
                    └─────────────────────┘
                                 │
                    ┌─────────────────────┐
                    │   Phala Cloud TEE   │
                    │                     │
                    │ • Key Derivation    │
                    │ • Attestation       │
                    │ • Secure Execution │
                    └─────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **[Flox](https://flox.dev)** - Environment manager (recommended)
- **Python 3.8+** - Runtime environment
- **Node.js 16+** - For Foundry installation
- **Foundry** - Smart contract toolkit

### Installation

1. **Setup with Flox (Recommended):**
   ```bash
   # Install Flox if not already installed
   curl -fsSL https://downloads.flox.dev/by/flox/sh | sh
   
   # Clone the repository
   git clone https://github.com/your-org/erc-8004-ex-phala.git
   cd erc-8004-ex-phala
   
   # Activate Flox environment
   flox activate
   ```

2. **Alternative: Manual Setup:**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Install Foundry
   curl -L https://foundry.paradigm.xyz | bash
   foundryup
   
   # Build contracts
   cd contracts && forge build && cd ..
   ```

### Running the Demo

```bash
# Complete automated demo
./run_demo.sh

# Or run components individually:

# 1. Start local blockchain
flox activate -- anvil

# 2. Deploy contracts (in new terminal)
flox activate -- make deploy

# 3. Run end-to-end test
flox activate -- python tests/e2e/test_simple.py

# 4. (Optional) Start API server
flox activate -- python run_api.py
```

## 📋 Demo Workflow

### Step 1: Contract Deployment
Deploys the three ERC-8004 registry contracts to create the trustless infrastructure.

### Step 2: Agent Initialization
- **TEE Server Agent**: Market analysis with TEE-secured keys
- **Validator Agent**: Analysis validation service
- **TEE Client Agent**: Feedback submission with attestation

### Step 3: Registration
All agents register on-chain, receiving unique agent IDs.

### Step 4: Market Analysis
Server agent performs analysis (with optional AI enhancement).

### Step 5: Validation Request
Server submits work for validation, creating on-chain request.

### Step 6: Validation
Validator assesses the analysis and provides score.

### Step 7: Feedback
Client authorized to provide feedback, building reputation.

## 🔧 Configuration

### Environment Variables

Create a `.env` file from the example:
```bash
cp .env.example .env
```

Key configurations:
- `RPC_URL`: Blockchain RPC endpoint (default: local Anvil)
- `USE_TEE_AUTH`: Enable TEE-based authentication
- `PRIVATE_KEY`: Fallback key when not using TEE
- AI API keys (optional): `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`

### TEE Configuration

TEE agents use deterministic key derivation based on:
- Agent domain
- Agent salt
- TEE secure environment

## 📁 Project Structure

```
erc-8004-ex-phala/
├── agents/                  # Agent implementations
│   ├── base_agent.py       # Base agent class
│   ├── server_agent.py     # Market analysis agent
│   ├── validator_agent.py  # Validation agent
│   ├── client_agent.py     # Feedback agent
│   ├── tee_*.py           # TEE-enabled versions
│   └── eip712_signer.py   # EIP-712 signing
├── contracts/              # Smart contracts
│   ├── src/               # Solidity source
│   └── script/            # Deployment scripts
├── tests/                  # Test suite
│   ├── e2e/               # End-to-end tests
│   ├── integration/       # Integration tests
│   └── unit/              # Unit tests
├── api/                    # REST API
│   ├── main.py           # FastAPI application
│   └── models.py         # Data models
├── scripts/               # Utility scripts
├── Makefile              # Build commands
└── run_demo.sh           # Demo runner

```

## 🧪 Testing

```bash
# Run all tests
flox activate -- make test

# Run specific test categories
flox activate -- pytest tests/unit/          # Unit tests
flox activate -- pytest tests/integration/   # Integration tests
flox activate -- pytest tests/e2e/          # End-to-end tests

# Run simple E2E demo
flox activate -- python tests/e2e/test_simple.py
```

## 🌐 API Server

The project includes a REST API for web integration:

```bash
# Start API server
flox activate -- python run_api.py

# Access at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Key Endpoints

- `GET /health` - Health check
- `GET /agents` - List all agents
- `POST /server/analyze` - Request market analysis
- `POST /validator/validate` - Validate analysis
- `POST /client/feedback/submit` - Submit feedback
- `GET /attestation/{agent_type}` - Get TEE attestation

## 🔐 Security Features

### TEE Integration
- Deterministic key derivation in secure environment
- Attestation quotes for verification
- Protected private key operations

### Smart Contract Security
- On-chain agent registration
- Immutable audit trails
- Permission-based operations

### Agent Security
- EIP-712 typed signatures
- Domain separation
- Replay protection

## 📚 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Documentation](api/README.md)
- [Contract Documentation](contracts/README.md)
- [Development Guide](docs/DEVELOPMENT.md)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [ERC-8004 Standard](https://eips.ethereum.org/EIPS/eip-8004) authors
- [Phala Network](https://phala.network) for TEE infrastructure
- [Foundry](https://book.getfoundry.sh/) for smart contract tools
- [CrewAI](https://www.crewai.com/) for AI agent framework

## ⚠️ Disclaimer

This is an example implementation for demonstration purposes. Perform security audits before production use.