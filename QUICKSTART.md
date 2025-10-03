# Quick Start

Launch your TEE agent in 3 minutes.

## 1. Clone & Install

```bash
git clone https://github.com/HashWarlock/erc-8004-ex-phala.git
cd erc-8004-ex-phala
pip install -e .
```

## 2. Configure

```bash
cp .env.example .env
# Edit .env with your settings
```

## 3. Run

```bash
python deployment/local_agent_server.py
```

Open http://localhost:8000

## What Happens

1. **Wallet Generation** - TEE derives address from domain+salt
2. **Fund Wallet** - Add 0.001 ETH via QR code
3. **Register On-Chain** - Click "Register" at /dashboard
4. **TEE Verification** - Automatic attestation submission
5. **Agent Ready** - A2A endpoints active

## Deploy Contracts (Optional)

```bash
export PRIVATE_KEY=0x...
./scripts/deploy_contracts.sh
```

## Test A2A

```bash
# Get agent card
curl http://localhost:8000/a2a/card

# Send message
curl -X POST http://localhost:8000/a2a/message \
  -H "Content-Type: application/json" \
  -d '{"from":"0x123","content":"hello"}'
```

## Endpoints

- `/` - Funding page
- `/dashboard` - Registration flow
- `/api/wallet` - Wallet info
- `/api/register` - Register agent
- `/api/tee/register` - TEE verification
- `/a2a/card` - Agent card
- `/a2a/message` - A2A messaging
- `/a2a/task` - Task execution

## Docs

- `IMPLEMENTATION_PLAN.md` - Full architecture
- `STAKEHOLDER_DEMO.md` - EF presentation
- `contracts/` - Solidity contracts
- `src/agent/` - Core agent code
