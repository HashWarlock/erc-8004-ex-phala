# ERC-8004 TEE Agent

Trustless agents with Intel TDX on Base Sepolia. 0.0001 ETH registration fee.

## Features

- 🔐 TEE-derived keys (Intel TDX via Phala dstack)
- 🌐 ERC-8004 compliant agent cards
- 📜 TEE attestation (mock signatures for testing)
- 🔗 On-chain registration (0.0001 ETH)
- 🤖 A2A protocol (POST /tasks, GET /tasks/{id})
- 🏖️ AIO Sandbox integration

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
├── contracts/             # Solidity contracts
│   ├── IdentityRegistry.sol (deployed: 0x8506e13d47faa2DC8c5a0dD49182e74A6131a0e3)
│   └── TEERegistry.sol
├── src/agent/            # Core agent logic
│   ├── tee_auth.py      # TEE key derivation
│   ├── tee_verifier.py  # TEE registration
│   └── registry.py      # On-chain registry client
├── src/templates/        # Agent templates
│   └── server_agent.py  # AIO Sandbox agent
├── deployment/           # Server
│   └── local_agent_server.py
└── static/              # Web UI
    ├── dashboard.html   # Registration flow
    └── funding.html     # QR code funding
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
- `GET /api/status` - Agent status (checks on-chain)
- `GET /api/wallet` - Wallet address & balance
- `POST /api/register` - Register agent (0.0001 ETH)
- `POST /api/tee/register` - Register TEE key
- `GET /.well-known/agent-card.json` - ERC-8004 agent card
- `POST /tasks` - Create A2A task
- `GET /tasks/{id}` - Query task status

## Deployed Contracts

**Base Sepolia:**
- IdentityRegistry: `0x8506e13d47faa2DC8c5a0dD49182e74A6131a0e3` (0.0001 ETH fee)
- TEERegistry: `0x03eCA4d903Adc96440328C2E3a18B71EB0AFa60D`
- Verifier: `0x481ce1a6EEC3016d1E61725B1527D73Df1c393a5`

## Configuration

See `.env.example`:

```bash
AGENT_DOMAIN=localhost:8000
AGENT_SALT=unique-salt
IDENTITY_REGISTRY_ADDRESS=0x8506e13d47faa2DC8c5a0dD49182e74A6131a0e3
TEE_REGISTRY_ADDRESS=0x03eCA4d903Adc96440328C2E3a18B71EB0AFa60D
```

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 3 min
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - Architecture
- **[STAKEHOLDER_DEMO.md](STAKEHOLDER_DEMO.md)** - EF presentation
- **[contracts/](contracts/)** - Smart contracts
- **[src/agent/](src/agent/)** - Core code

## How It Works

1. **Generate Wallet** - TEE derives keys from domain+salt
2. **Fund** - Add 0.0001 ETH to agent address
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
