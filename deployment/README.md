# Deployment Tools

Production deployment tools for ERC-8004 TEE Agents on Base Sepolia.

## Quick Reference

### Check Wallet Status
```bash
python deployment/check_wallets.py
```
Shows funding status for all configured agents.

### Deploy to Base Sepolia
```bash
python deployment/deploy_production.py
```
Full deployment workflow with automatic checks and verification.

---

## Tools

### 1. check_wallets.py

**Purpose**: Check funding status of TEE-derived addresses

**Usage**:
```bash
python deployment/check_wallets.py
```

**Output**:
- Table of all configured agents
- Balance for each address
- Minimum funding required
- List of addresses needing funds

**Example Output**:
```
Agent Name       | Address      | Balance | Min Needed | Status
Production Agent | 0x5d5A...    | 0.0000  | 0.0005     | ✗ Needs Funds
Test Agent       | 0x0B35...    | 0.0100  | 0.0005     | ✓ Funded
```

### 2. deploy_production.py

**Purpose**: Full production deployment workflow

**Usage**:
```bash
# Using default .env.production
python deployment/deploy_production.py

# Using custom environment file
python deployment/deploy_production.py --env .env.custom
```

**Workflow**:
1. ✅ Check TEE environment
2. ✅ Load configuration
3. ✅ Derive agent address
4. ✅ Check funding status
5. ✅ Register on-chain (if funded)
6. ✅ Verify registration
7. ✅ Generate attestation
8. ✅ Save deployment report

**Output**:
- Console logs for each step
- JSON report in `deployment/reports/`
- Deployment summary

---

## Configuration

Edit `.env.production` to configure your deployment:

```bash
# Agent Configuration
AGENT_DOMAIN=your-agent.phala.network
AGENT_SALT=your-unique-salt-here
AGENT_TYPE=server

# Network (Base Sepolia)
RPC_URL=https://sepolia.base.org
CHAIN_ID=84532

# Registry Addresses
IDENTITY_REGISTRY_ADDRESS=0x000c5A70B7269c5eD4238DcC6576e598614d3f70
REPUTATION_REGISTRY_ADDRESS=0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde
VALIDATION_REGISTRY_ADDRESS=0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d
TEE_VERIFIER_ADDRESS=0x1b841e88ba786027f39ecf9Cd160176b22E3603c

# TEE
USE_TEE_AUTH=true
```

---

## Addresses Needing Funding

Run `check_wallets.py` to see current status. Example addresses:

```
Test Agent:       0x0B35c3107A995658AdD717CCE359AB3DB204D650
Server Agent:     0x9979E31E0a53300E05762DFF87c69e5db77787bf
Production Agent: 0x5d5A57CEFE52f59Ff9fD2A2f87F54BeE7D5587A7
```

**Get Base Sepolia ETH**:
- Coinbase Faucet: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet
- Base Bridge: https://bridge.base.org/

**Recommended Amount**: 0.01 ETH per address

---

## Deployment Reports

Reports are automatically saved to `deployment/reports/`:

```
deployment/reports/
├── deploy-20251001-120000.json
├── deploy-20251001-130000.json
└── ...
```

**Report Contents**:
- Deployment ID and timestamp
- Configuration used
- Agent address
- Funding status
- Registration result (Agent ID if successful)
- Attestation details
- Complete logs

**Example Report**:
```json
{
  "deployment_id": "deploy-20251001-120000",
  "timestamp": "2025-10-01T12:00:00",
  "config": {
    "domain": "agent.phala.network",
    "role": "server",
    "chain_id": 84532
  },
  "address": "0x5d5A57CEFE52f59Ff9fD2A2f87F54BeE7D5587A7",
  "funding": {
    "funded": true,
    "balance_eth": "0.0100"
  },
  "registration": {
    "agent_id": 1,
    "success": true
  },
  "attestation": {
    "generated": true,
    "size": 10020
  }
}
```

---

## Troubleshooting

### "TEE socket not found"
**Cause**: Not running in production TEE environment
**Solution**: Deploy from production TEE instance

### "Failed to connect to RPC"
**Cause**: Network issues or invalid RPC URL
**Solution**: Check `RPC_URL` in config, try alternative:
- `https://base-sepolia-rpc.publicnode.com`
- `https://sepolia.base.org`

### "Address not funded"
**Cause**: Agent address has 0 ETH
**Solution**: Send Base Sepolia ETH to the address

### "Registration failed"
**Possible Causes**:
- Insufficient gas (send more ETH)
- Domain already registered (change `AGENT_SALT`)
- Contract interaction error (check registry addresses)

---

## Workflow Examples

### First Time Deployment

```bash
# 1. Check what addresses need funding
python deployment/check_wallets.py

# 2. Fund the address(es) using Coinbase faucet
# (Send to address shown in output)

# 3. Verify funding
python deployment/check_wallets.py

# 4. Deploy
python deployment/deploy_production.py
```

### Deploy Multiple Agents

```bash
# Edit .env.production:
# - Change AGENT_SALT to "agent-1-salt"
# - Run deployment
python deployment/deploy_production.py

# Edit .env.production again:
# - Change AGENT_SALT to "agent-2-salt"
# - Run deployment again
python deployment/deploy_production.py

# Each salt creates a unique address
```

### Check Deployment History

```bash
# List all deployment reports
ls -lh deployment/reports/

# View latest report
cat deployment/reports/deploy-*.json | jq .

# Find successful deployments
grep -l '"success": true' deployment/reports/*.json
```

---

## Network Information

**Base Sepolia**:
- Chain ID: 84532
- RPC: https://sepolia.base.org
- Explorer: https://sepolia.basescan.org
- Faucet: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet

**Registry Contracts**:
- Identity: `0x000c5A70B7269c5eD4238DcC6576e598614d3f70`
- Reputation: `0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde`
- Validation: `0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d`
- TEE Verifier: `0x1b841e88ba786027f39ecf9Cd160176b22E3603c`

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Deploy Agent

on:
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -e .

      - name: Check wallets
        run: python deployment/check_wallets.py

      - name: Deploy
        run: python deployment/deploy_production.py
        env:
          AGENT_SALT: ${{ secrets.AGENT_SALT }}

      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: deployment-report
          path: deployment/reports/*.json
```

---

## Additional Resources

- **Full Guide**: [../DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)
- **Refactoring Summary**: [../REFACTORING_SUMMARY.md](../REFACTORING_SUMMARY.md)
- **Development Guide**: [../CLAUDE.md](../CLAUDE.md)
- **Quickstart**: [../QUICKSTART.md](../QUICKSTART.md)