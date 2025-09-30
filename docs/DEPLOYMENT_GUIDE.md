# Production Deployment Guide - Base Sepolia

**Status**: Ready for Production Testing
**Network**: Base Sepolia (Chain ID: 84532)
**Environment**: Production TEE

---

## Quick Start

### 1. Check Wallet Status

```bash
python deployment/check_wallets.py
```

This will show you which TEE-derived addresses need funding.

### 2. Fund Your Agent Addresses

The tool identified these addresses that need Base Sepolia ETH:

#### **Production Agent**
```
Address: 0x5d5A57CEFE52f59Ff9fD2A2f87F54BeE7D5587A7
Domain: agent.phala.network
Salt: production-salt-change-this-value
```

#### **Test Agent**
```
Address: 0x0B35c3107A995658AdD717CCE359AB3DB204D650
Domain: test-agent.phala.network
Salt: test-salt-123
```

#### **Server Agent**
```
Address: 0x9979E31E0a53300E05762DFF87c69e5db77787bf
Domain: server-agent.test.phala.network
Salt: server-test-salt
```

**Get Testnet ETH:**
- **Coinbase Faucet**: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet
- **Bridge from Sepolia**: https://bridge.base.org/

**Recommended Amount**: At least **0.01 ETH** per address (covers ~20 transactions)

### 3. Deploy to Base Sepolia

```bash
# Using production environment
python deployment/deploy_production.py

# Or with custom env file
python deployment/deploy_production.py --env .env.custom
```

---

## Deployment Workflow

The deployment script performs these steps automatically:

### Step 1: TEE Environment Check
✅ Verifies `/var/run/dstack.sock` is accessible
✅ Tests key derivation from TEE
✅ Confirms production environment ready

### Step 2: Load Configuration
✅ Reads `.env.production` settings
✅ Configures agent domain, salt, role
✅ Loads Base Sepolia registry addresses

### Step 3: Derive Agent Address
✅ Uses TEE to derive deterministic address
✅ Domain + Salt → Unique Ethereum Address
✅ Displays address for funding verification

### Step 4: Check Funding
✅ Connects to Base Sepolia RPC
✅ Checks ETH balance at derived address
✅ Estimates gas costs for registration
✅ **Stops here if not funded** (requires manual funding)

### Step 5: Register On-Chain *(if funded)*
✅ Creates agent instance
✅ Submits registration transaction
✅ Waits for transaction confirmation
✅ Returns Agent ID

### Step 6: Verify Registration
✅ Queries Identity Registry contract
✅ Confirms agent is active on-chain
✅ Displays agent information

### Step 7: Generate Attestation
✅ Creates TEE attestation (10KB quote)
✅ Includes 64-byte application data
✅ Provides cryptographic proof of TEE execution

### Step 8: Save Report
✅ Generates deployment report JSON
✅ Saves to `deployment/reports/`
✅ Includes all deployment details

---

## Configuration

### Environment Variables (.env.production)

```bash
# Agent Configuration
AGENT_DOMAIN=agent.phala.network
AGENT_SALT=your-unique-salt-here  # CHANGE THIS!
AGENT_TYPE=server                  # server, validator, client, custom

# Base Sepolia Network
RPC_URL=https://sepolia.base.org
CHAIN_ID=84532

# ERC-8004 Registries (Base Sepolia)
IDENTITY_REGISTRY_ADDRESS=0x000c5A70B7269c5eD4238DcC6576e598614d3f70
REPUTATION_REGISTRY_ADDRESS=0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde
VALIDATION_REGISTRY_ADDRESS=0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d
TEE_VERIFIER_ADDRESS=0x1b841e88ba786027f39ecf9Cd160176b22E3603c

# TEE Configuration
USE_TEE_AUTH=true
```

**Important**: Change `AGENT_SALT` to a unique value for each agent!

---

## Directory Structure (Refactored)

```
erc-8004-ex-phala/
├── src/                          # Core SDK
│   ├── agent/                   # Agent components
│   │   ├── base.py             # BaseAgent class
│   │   ├── tee_auth.py         # TEE integration
│   │   ├── registry.py         # Registry client
│   │   └── eip712.py           # Signing
│   ├── templates/               # Agent templates
│   └── utils/                   # Utilities
│
├── tests/                        # Test suites
│   ├── production/              # Production TEE tests
│   │   └── test_production_tee.py
│   ├── integration/             # Integration tests
│   │   └── test_local_deployment.py
│   └── unit/                    # Unit tests
│
├── deployment/                   # Deployment tools
│   ├── deploy_production.py    # Main deployment script
│   ├── check_wallets.py        # Wallet checker
│   └── reports/                # Deployment reports
│
├── examples/                     # Examples
│   ├── simple_agent_example.py
│   ├── basic_workflow/
│   ├── ai_enhanced/
│   └── custom_validation/
│
├── docs/                        # Additional docs
├── scripts/                     # Utility scripts
│
├── .env                         # Local development
├── .env.production              # Production config
├── DEPLOYMENT_GUIDE.md          # This file
└── CLAUDE.md                    # Developer guide
```

---

## Smart Contract Integration

### Identity Registry
- **Address**: `0x000c5A70B7269c5eD4238DcC6576e598614d3f70`
- **Purpose**: Agent registration and identity management
- **Key Functions**:
  - `registerAgent(domain, address, card)` → agentId
  - `getAgent(agentId)` → agent info
  - `getAgentByDomain(domain)` → agentId

### Reputation Registry
- **Address**: `0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde`
- **Purpose**: Agent reputation tracking
- **Key Functions**:
  - `submitFeedback(agentId, rating, data)`
  - `getReputation(agentId)` → stats

### Validation Registry
- **Address**: `0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d`
- **Purpose**: Validation request/response coordination
- **Key Functions**:
  - `requestValidation(validatorId, dataHash)`
  - `submitValidationResponse(dataHash, response)`

### TEE Verifier
- **Address**: `0x1b841e88ba786027f39ecf9Cd160176b22E3603c`
- **Purpose**: TEE attestation verification
- **Note**: Integrated with registration process

---

## Testing Production Deployment

### Pre-Deployment Tests (Already Passed ✅)

```bash
# Test TEE integration
python tests/production/test_production_tee.py

# Test local deployment
python tests/integration/test_local_deployment.py

# Test simple agent
python examples/simple_agent_example.py
```

### Post-Funding Tests

After funding your addresses, you can test:

```bash
# Check funding status
python deployment/check_wallets.py

# Deploy to Base Sepolia (DRY RUN first)
# 1. Set AGENT_SALT to something unique
# 2. Run deployment
python deployment/deploy_production.py
```

---

## Funding Instructions

### For You (Agent Deployer)

**I recommend funding these addresses first for testing:**

1. **Primary Test Agent**
   ```
   Address: 0x0B35c3107A995658AdD717CCE359AB3DB204D650
   Amount: 0.01 ETH (recommended)
   Purpose: Initial registration testing
   ```

2. **Server Agent** (if testing multi-agent)
   ```
   Address: 0x9979E31E0a53300E05762DFF87c69e5db77787bf
   Amount: 0.01 ETH
   Purpose: Server role testing
   ```

### Steps to Fund:

1. **Get Base Sepolia ETH**:
   - Visit: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet
   - Connect wallet (MetaMask, etc.)
   - Request testnet ETH

2. **Send to Agent Addresses**:
   - Use MetaMask or any wallet
   - Network: Base Sepolia
   - Send at least 0.01 ETH to each address above

3. **Verify Funding**:
   ```bash
   python deployment/check_wallets.py
   ```

4. **Deploy**:
   ```bash
   python deployment/deploy_production.py
   ```

---

## Expected Results

### Successful Deployment Output:

```
================================================================================
ERC-8004 AGENT PRODUCTION DEPLOYMENT
Base Sepolia - deploy-20251001-123456
================================================================================

STEP 1: Checking TEE Environment
✓ TEE socket found: /var/run/dstack.sock
✓ TEE key derivation working

STEP 2: Loading Configuration
✓ Domain: agent.phala.network
✓ Role: server
✓ Chain: Base Sepolia (84532)

STEP 3: Deriving Agent Address from TEE
✓ Agent Address: 0x5d5A57CEFE52f59Ff9fD2A2f87F54BeE7D5587A7

STEP 4: Checking Funding Status
✓ Address is funded
  Balance: 0.0100 ETH
  Estimated Cost: 0.0005 ETH

STEP 5: Registering Agent On-Chain
✓ Agent registered successfully!
  Agent ID: 1

STEP 6: Verifying Registration
✓ Agent verified on-chain
  Domain: agent.phala.network
  Active: True

STEP 7: Generating TEE Attestation
✓ Attestation generated
  Quote size: 10020 bytes

DEPLOYMENT SUMMARY
Agent Address: 0x5d5A57CEFE52f59Ff9fD2A2f87F54BeE7D5587A7
Funded: ✓
Registered: ✓ (ID: 1)
Attestation: ✓

✅ DEPLOYMENT SUCCESSFUL!
```

---

## Troubleshooting

### "Address not funded"
**Solution**: Send Base Sepolia ETH to the displayed address

### "RPC connection failed"
**Solution**: Check `RPC_URL` in `.env.production`, try alternative RPC:
- `https://base-sepolia-rpc.publicnode.com`
- `https://sepolia.base.org`

### "Registration failed"
**Possible causes**:
- Insufficient gas
- Contract not found (check registry addresses)
- Domain already registered (change `AGENT_SALT`)

### "TEE socket not found"
**Solution**: Ensure you're running in production TEE environment, not locally

---

## Next Steps After Deployment

1. **Verify on Block Explorer**
   - Visit: https://sepolia.basescan.org/
   - Search for your agent address
   - View registration transaction

2. **Test Agent Functionality**
   - Process test tasks
   - Submit reputation feedback
   - Request validation

3. **Deploy Additional Agents**
   - Change `AGENT_SALT` for unique address
   - Repeat deployment process
   - Test multi-agent interactions

4. **Production Monitoring**
   - Monitor transaction costs
   - Track agent interactions
   - Review deployment reports in `deployment/reports/`

---

## Support & Resources

- **Deployment Reports**: `deployment/reports/*.json`
- **Development Guide**: [CLAUDE.md](CLAUDE.md)
- **TEE Validation**: [PRODUCTION_TEE_VALIDATION.md](PRODUCTION_TEE_VALIDATION.md)
- **Quickstart**: [QUICKSTART.md](QUICKSTART.md)

---

## Summary Checklist

- [ ] Reviewed configuration in `.env.production`
- [ ] Changed `AGENT_SALT` to unique value
- [ ] Checked wallet status: `python deployment/check_wallets.py`
- [ ] Funded at least one agent address with 0.01 ETH
- [ ] Ran deployment: `python deployment/deploy_production.py`
- [ ] Verified registration on Base Sepolia
- [ ] Saved agent ID and transaction hashes
- [ ] Tested agent functionality

---

**Ready to deploy!** 🚀

Send Base Sepolia ETH to the addresses above, then run `python deployment/deploy_production.py`