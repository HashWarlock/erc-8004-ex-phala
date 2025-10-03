# ERC-8004 TEE Agent

Trustless AI agents with Intel TDX hardware security on Base Sepolia.

## Features

- 🔐 TEE-derived keys (Intel TDX)
- 🌐 ERC-8004 compliant
- 📜 Remote attestation
- 🔗 On-chain registration
- 🤖 A2A protocol support

## Quick Start

### Using Docker (Recommended)

```bash
git clone https://github.com/HashWarlock/erc-8004-ex-phala.git
cd erc-8004-ex-phala
cp .env.example .env
# Edit .env with your config
docker compose up -d
```

### Manual Setup

```bash
git clone https://github.com/HashWarlock/erc-8004-ex-phala.git
cd erc-8004-ex-phala
pip install -e .
cp .env.example .env
# Edit .env with your config
python deployment/local_agent_server.py
```

Open http://localhost:8000

**See [QUICKSTART.md](QUICKSTART.md) for details**

## Project Structure

```
erc-8004-ex-phala/
├── contracts/              # Reference Solidity contracts
│   ├── TEERegistry.sol
│   └── ITEERegistry.sol
├── src/agent/             # Core agent logic
│   ├── base.py
│   ├── tee_auth.py
│   └── tee_verifier.py
├── deployment/            # Server entry point
│   └── local_agent_server.py
└── static/                # Web UI
    ├── funding.html
    └── dashboard.html
```

## Architecture

```
┌─────────────┐
│   Wallet    │ Fund with Base Sepolia ETH
└─────────────┘
       ↓
┌─────────────┐
│  Register   │ Identity Registry (on-chain)
└─────────────┘
       ↓
┌─────────────┐
│ TEE Verify  │ Attestation + Code Measurement
└─────────────┘
       ↓
┌─────────────┐
│    Ready    │ A2A endpoints active
└─────────────┘
```

## API Endpoints

- `GET /` - Funding page
- `GET /dashboard` - Registration flow
- `GET /api/wallet` - Wallet address & balance
- `POST /api/register` - Register agent on-chain
- `POST /api/tee/register` - Submit TEE attestation
- `GET /a2a/card` - Agent card (ERC-8004)
- `POST /a2a/message` - A2A messaging
- `POST /a2a/task` - Task execution

## Deploy Contracts

```bash
export PRIVATE_KEY=0x...
./scripts/deploy_contracts.sh
```

Updates `deployed_addresses.json`

## Configuration

See `.env.example`:

```bash
AGENT_DOMAIN=localhost:8000
AGENT_SALT=unique-salt
IDENTITY_REGISTRY_ADDRESS=0x19fad4adD9f8C4A129A078464B22E1506275FbDd
```

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 3 min
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - Architecture
- **[STAKEHOLDER_DEMO.md](STAKEHOLDER_DEMO.md)** - EF presentation
- **[contracts/](contracts/)** - Smart contracts
- **[src/agent/](src/agent/)** - Core code

## How It Works

1. **Generate Wallet** - TEE derives keys from domain+salt
2. **Fund** - Add 0.001 ETH to agent address
3. **Register** - Call Identity Registry `newAgent()`
4. **Verify TEE** - Submit attestation to TEE Registry
5. **Go Live** - A2A endpoints ready

**Trust Model**: Hardware-backed cryptographic proof via Intel TDX attestation

## Tech Stack

- **TEE**: Intel TDX (Phala dstack)
- **Chain**: Base Sepolia
- **Backend**: Python/FastAPI
- **Contracts**: Solidity ^0.8.20
- **Frontend**: HTML/Tailwind

## Development

```bash
# Run server
python deployment/local_agent_server.py

# Test
pytest tests/

# Deploy contracts
./scripts/deploy_contracts.sh
```

## ERC-8004 Compliance

✅ Agent Cards
✅ Identity Registry
✅ TEE Registry
✅ A2A Protocol
✅ Attestation Verification

## License

MIT

## Links

- **Spec**: [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004)
- **Reference**: [dstack-erc8004-poc](https://github.com/h4x3rotab/dstack-erc8004-poc)
- **Phala**: [phala.network](https://phala.network)
- **Base**: [base.org](https://base.org)
