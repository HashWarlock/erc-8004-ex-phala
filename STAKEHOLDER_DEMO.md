# ERC-8004 TEE Agent - Stakeholder Demonstration

**Ethereum Foundation Presentation**

---

## Executive Summary

Trustless AI agent registration and verification using Intel TDX Trusted Execution Environments on Base Sepolia, implementing the ERC-8004 standard.

**Key Achievement**: Cryptographically provable agent identity secured in hardware.

---

## Architecture

```
┌─────────────┐
│   Wallet    │ → Fund agent address
└─────────────┘
       ↓
┌─────────────┐
│  Identity   │ → Register on-chain (agentId)
│  Registry   │
└─────────────┘
       ↓
┌─────────────┐
│     TEE     │ → Verify attestation
│  Registry   │ → Link pubkey to agentId
└─────────────┘
       ↓
┌─────────────┐
│ Agent Ready │ → A2A communication
└─────────────┘
```

---

## Live Demo Steps

### 1. Wallet Generation (30 sec)
- Open http://localhost:8000
- Show TEE-derived address: `0xc86b...9d16`
- Display QR code for funding
- Fund with Base Sepolia faucet

**Tech**: Deterministic key derivation in Intel TDX enclave

### 2. Identity Registration (1 min)
```bash
curl -X POST http://localhost:8000/api/register
```

**Result**:
- Agent ID: `123`
- Tx: `0xabc...def`
- Explorer: basescan.org/tx/...

**Contract**: `IdentityRegistry.newAgent(domain, address)`

### 3. TEE Verification (1 min)
```bash
curl -X POST http://localhost:8000/api/tee/register
```

**Result**:
- TEE attestation: 10KB Intel TDX quote
- Code measurement: `0x123...abc`
- Pubkey registered on-chain

**Contract**: `TEERegistry.addKey(agentId, teeArch, measurement, pubkey, proof)`

### 4. Agent Interaction (30 sec)
```bash
# Get agent card
curl http://localhost:8000/a2a/card

# Send message
curl -X POST http://localhost:8000/a2a/message \
  -d '{"from":"0x...", "content":"hello"}'
```

**Protocol**: ERC-8004 A2A messaging

---

## Trust Model

**Problem**: How do you trust an AI agent?

**Solution**: Hardware-backed cryptographic proof

1. **TEE Attestation**: Intel TDX proves code running in secure enclave
2. **Code Measurement**: Hash of agent binary verified on-chain
3. **Key Binding**: Cryptographic link between attestation and pubkey
4. **On-Chain Registry**: Immutable record on Base Sepolia

**Verification**: Anyone can verify agent authenticity by checking:
- Attestation quote validity
- Code measurement matches expected hash
- Pubkey maps to correct agent ID
- All signed messages from this agent are trustworthy

---

## Technical Deep Dive

### TEE Key Derivation
```python
# Deterministic from domain + salt
key = derive_key("domain.com", "salt")
# Same input → Same key (reproducible)
# Keys never leave TEE
```

### Attestation Flow
```
1. Agent requests attestation from dstack
2. TEE generates quote (10KB)
3. Quote contains:
   - Code measurement (SHA256)
   - Runtime measurements
   - Agent pubkey
4. Submit to TEERegistry
5. On-chain verification
```

### Smart Contracts

**TEERegistry.sol**
```solidity
struct Key {
    bytes32 teeArch;        // "tdx"
    bytes32 codeMeasurement; // Binary hash
    bytes pubkey;           // secp256k1
    address verifier;       // Who verified
}

function addKey(
    uint256 agentId,
    bytes32 teeArch,
    bytes32 codeMeasurement,
    address pubkey,
    string codeConfigUri,
    address verifier,
    bytes proof
) external;
```

**Deployed**: Base Sepolia (chainId: 84532)

---

## Security Guarantees

1. **Hardware Root of Trust**: Intel TDX
2. **Reproducible Builds**: Same code → Same measurement
3. **Attestation Verification**: Cryptographic proof of execution environment
4. **On-Chain Audit Trail**: All registrations recorded
5. **Key Isolation**: Private keys never exposed

**Attack Resistance**:
- ❌ Can't fake attestation (hardware-signed)
- ❌ Can't extract keys (TEE-protected)
- ❌ Can't modify code undetected (measurement changes)

---

## ERC-8004 Compliance

✅ **Agent Cards**: JSON metadata with capabilities
✅ **Identity Registry**: On-chain agent registration
✅ **TEE Registry**: Hardware attestation verification
✅ **A2A Protocol**: Agent-to-agent messaging
✅ **Reputation**: Framework ready (separate contract)

**Standard**: https://eips.ethereum.org/EIPS/eip-8004

---

## Use Cases

1. **Financial Agents**: Trustless DeFi trading bots
2. **Oracle Agents**: Verifiable off-chain computation
3. **Multi-Agent Systems**: Provably secure coordination
4. **Compliance**: Auditable AI decision-making
5. **Privacy**: Encrypted agent-to-agent communication

---

## Roadmap

**Current (PoC)**: ✅
- TEE key derivation
- On-chain registration
- Attestation verification
- A2A messaging

**Next (Q1 2025)**:
- Production ZK verifier (vs mock)
- Reputation system integration
- Multi-TEE support (SGX, Nitro)
- Agent marketplace

**Future**:
- Cross-chain agents
- DAO governance
- Agent swarms

---

## Metrics

| Metric | Value |
|--------|-------|
| Registration Gas | ~300k |
| TEE Verification Gas | ~500k |
| Attestation Size | 10KB |
| Key Derivation | <1s |
| Total Setup Time | ~2 min |

**Cost**: ~$0.01 on Base Sepolia (at 1 gwei)

---

## Demo URLs

- **Agent Server**: http://localhost:8000
- **Funding Page**: http://localhost:8000/funding
- **Dashboard**: http://localhost:8000/dashboard
- **API Docs**: http://localhost:8000/docs
- **Agent Card**: http://localhost:8000/a2a/card

**Explorer**: https://sepolia.basescan.org

---

## Technical Stack

- **TEE**: Intel TDX via Phala dstack
- **Blockchain**: Base Sepolia (Optimistic Rollup)
- **Backend**: Python/FastAPI
- **Contracts**: Solidity ^0.8.20
- **Frontend**: HTML/Tailwind/Alpine.js
- **Protocol**: ERC-8004

---

## Questions?

**Code**: github.com/HashWarlock/erc-8004-ex-phala
**Spec**: ERC-8004 Trustless Agents v0.9
**Contact**: hashwarlock@protonmail.com

---

## Appendix: Commands

```bash
# Start agent
python deployment/local_agent_server.py

# Deploy contracts
./scripts/deploy_contracts.sh

# Check wallet
curl localhost:8000/api/wallet

# Register
curl -X POST localhost:8000/api/register

# TEE verify
curl -X POST localhost:8000/api/tee/register

# A2A message
curl -X POST localhost:8000/a2a/message \
  -H "Content-Type: application/json" \
  -d '{"from":"0x123","content":"test"}'
```
