# TEE Agent End-to-End Implementation Plan

**Objective**: Build a complete ERC-8004 compliant TEE Agent system with wallet generation, on-chain registration, TEE verification, and A2A protocol integration.

**Target Environment**: https://3af8f2cbcd12330c938cd66efcf072694f48e105-8080.dstack-base-prod9.phala.network

---

## Overview

This plan outlines the implementation of a fully functional TEE Agent that:
1. Generates a wallet on startup and requests gas fees
2. Registers itself on-chain in the Identity Registry
3. Deploys and verifies TEE attestation via TEERegistry contract
4. Enables agent-to-agent communication via A2A protocol
5. Provides a visual dashboard for stakeholder demonstration

---

## Phase 1: Wallet Generation & Funding Interface

**Goal**: Create a startup flow for gas fee funding

### Backend: Wallet Generation API

**File**: `deployment/local_agent_server.py`

- [x] Generate wallet on startup (already exists via TEE)
- [ ] Add `/api/wallet` endpoint to display wallet address & QR code
- [ ] Add `/api/wallet/balance` endpoint for real-time balance checking
- [ ] Implement balance polling mechanism

**Endpoints**:
```python
GET /api/wallet
Response:
{
  "address": "0x...",
  "balance": "0.0",
  "balance_wei": "0",
  "qr_code_data": "ethereum:0x...?chainId=84532",
  "chain_id": 84532,
  "chain_name": "Base Sepolia",
  "funded": false,
  "minimum_balance": "0.001"  // ETH for gas
}
```

### Frontend: Funding Page

**File**: `static/funding.html`

Features:
- Display agent wallet address prominently
- Show QR code for easy mobile wallet funding
- Real-time balance updates (polling every 5s)
- "Continue to Registration" button (enabled when funded)
- Progress indicator showing funding status

**UI Components**:
- Wallet address display with copy button
- QR code generator
- Balance indicator
- Network info (Base Sepolia)
- Faucet links for testnet

---

## Phase 2: On-Chain Registration Flow

**Goal**: Register agent in Identity Registry

### Backend: Registration API

**File**: `deployment/local_agent_server.py`

**New Endpoints**:
```python
POST /api/register
Request:
{
  "agent_card_url": "https://agent.example.com/card"  // optional
}

Response:
{
  "success": true,
  "agent_id": 123,
  "tx_hash": "0x...",
  "domain": "localhost:8000",
  "address": "0x...",
  "explorer_url": "https://sepolia.basescan.org/tx/0x..."
}
```

### Update Registry Client

**File**: `src/agent/registry.py`

Tasks:
- [x] `newAgent()` function already implemented
- [ ] Add `check_balance()` helper
- [ ] Add `estimate_registration_gas()` function
- [ ] Add error handling for insufficient funds
- [ ] Add retry logic for failed registrations

**New Methods**:
```python
async def check_balance(self) -> Dict[str, Any]:
    """Check if wallet has sufficient balance for registration"""

async def estimate_registration_gas(self) -> int:
    """Estimate gas needed for registration"""
```

---

## Phase 3: TEE Verification & Attestation

**Goal**: Deploy TEERegistry contract and verify TEE execution

### Smart Contracts

**Directory**: `contracts/`

**Files to Create**:
1. `contracts/ITEERegistry.sol` - Interface
2. `contracts/TEERegistry.sol` - Implementation
3. `contracts/IZkVerifier.sol` - Verifier interface
4. `contracts/MockZkVerifier.sol` - Mock verifier for PoC
5. `contracts/deploy.js` - Deployment script

**ITEERegistry.sol**:
```solidity
interface ITEERegistry {
    struct TEEKey {
        uint256 agentId;
        string teeArch;           // "tdx", "sgx", "nitro"
        bytes32 codeMeasurement;  // Hash of agent code
        bytes pubkey;             // secp256k1 public key
        address verifier;         // zkVerifier that validated
        uint256 timestamp;
    }

    function registerTEEKey(
        uint256 agentId,
        string calldata teeArch,
        bytes32 codeMeasurement,
        bytes calldata pubkey,
        bytes calldata proof
    ) external returns (uint256 keyId);

    function verifyTEEKey(uint256 keyId) external view returns (bool);
    function getTEEKey(uint256 keyId) external view returns (TEEKey memory);
}
```

**MockZkVerifier.sol** (for PoC):
```solidity
contract MockZkVerifier {
    // Simplified verification for demo
    // In production: verify ZK-SNARK proof of attestation
    function verifyAttestation(
        bytes calldata attestation,
        bytes calldata proof
    ) external pure returns (bool) {
        // Mock: always return true for demo
        return attestation.length > 0;
    }
}
```

### Backend: TEE Registration

**File**: `deployment/local_agent_server.py`

**New Endpoints**:
```python
POST /api/tee/register
Request:
{
  "agent_id": 123
}

Response:
{
  "success": true,
  "key_id": 456,
  "tx_hash": "0x...",
  "tee_arch": "tdx",
  "code_measurement": "0x...",
  "pubkey": "0x...",
  "verified": true,
  "explorer_url": "https://sepolia.basescan.org/tx/0x..."
}

GET /api/tee/status/{agent_id}
Response:
{
  "registered": true,
  "key_id": 456,
  "tee_arch": "tdx",
  "verified": true,
  "attestation_valid": true
}
```

### Verification Flow

**File**: `src/agent/tee_verifier.py` (new)

```python
class TEEVerifier:
    async def generate_attestation_proof(self):
        """Generate proof from dstack TEE attestation"""

    async def register_tee_key(self, agent_id: int):
        """Register TEE key on-chain"""

    async def verify_tee_key(self, key_id: int):
        """Verify TEE key is valid"""
```

**Steps**:
1. Get attestation from dstack API
2. Extract code measurement
3. Generate proof (mock for PoC)
4. Submit to TEERegistry
5. Verify registration

---

## Phase 4: A2A Protocol Integration

**Goal**: Enable agent-to-agent communication

### Install A2A SDK

**File**: `package.json` (new)

```json
{
  "name": "erc8004-tee-agent",
  "version": "1.0.0",
  "dependencies": {
    "@a2aproject/a2a-js": "^latest"
  }
}
```

**Installation**:
```bash
npm install
```

### A2A Server Implementation

**File**: `src/agent/a2a_server.py` (new)

```python
class A2AServer:
    """A2A protocol server implementation"""

    async def get_agent_card(self) -> Dict[str, Any]:
        """Return ERC-8004 agent card"""

    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming A2A message"""

    async def handle_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming A2A task"""

    async def create_artifact(self, data: Any) -> str:
        """Create task artifact response"""
```

**New Endpoints**:
```python
GET /a2a/card
Response: {ERC-8004 AgentCard}

POST /a2a/message
Request:
{
  "from": "0x...",
  "content": "Hello agent!",
  "metadata": {}
}

POST /a2a/task
Request:
{
  "task_id": "...",
  "description": "...",
  "parameters": {}
}
```

### A2A Client

**File**: `src/agent/a2a_client.py` (new)

```python
class A2AClient:
    """A2A protocol client for agent communication"""

    async def send_message(
        self,
        target_agent: str,
        message: str
    ) -> Dict[str, Any]:
        """Send message to another agent"""

    async def request_task(
        self,
        target_agent: str,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Request task execution from another agent"""

    async def get_agent_card(self, agent_url: str) -> Dict[str, Any]:
        """Fetch agent card from another agent"""
```

---

## Phase 5: Visualization Dashboard

**Goal**: Simple frontend showing the complete flow

### Dashboard UI

**File**: `static/dashboard.html`

**Sections**:

1. **Step 1: Wallet Funding**
   - Status indicator
   - Wallet address
   - Current balance
   - Action: Fund wallet

2. **Step 2: Identity Registration**
   - Status indicator
   - Transaction hash (link to explorer)
   - Agent ID
   - Domain
   - Action: Register

3. **Step 3: TEE Verification**
   - Status indicator
   - TEE architecture (TDX)
   - Code measurement
   - Attestation status
   - Transaction hash
   - Action: Verify TEE

4. **Step 4: Agent Status**
   - Overall status (Ready/Active)
   - Capabilities list
   - A2A endpoint
   - Action: Go to interaction

5. **Step 5: A2A Interaction**
   - Send test message
   - View responses
   - Agent card display

**Technology**:
- HTML5
- Tailwind CSS
- Alpine.js (lightweight reactivity)
- Chart.js (optional: for status visualization)

### Status Aggregation API

**File**: `deployment/local_agent_server.py`

```python
GET /api/status/full
Response:
{
  "wallet": {
    "address": "0x...",
    "balance": "0.1",
    "funded": true
  },
  "registration": {
    "registered": true,
    "agent_id": 123,
    "domain": "localhost:8000",
    "tx_hash": "0x...",
    "explorer_url": "..."
  },
  "tee": {
    "verified": true,
    "key_id": 456,
    "tee_arch": "tdx",
    "code_measurement": "0x...",
    "tx_hash": "0x...",
    "explorer_url": "..."
  },
  "agent": {
    "status": "active",
    "capabilities": [...],
    "a2a_endpoint": "http://localhost:8000/a2a"
  },
  "links": {
    "agent_card": "/api/card",
    "a2a_card": "/a2a/card",
    "dashboard": "/dashboard"
  }
}
```

---

## Phase 6: Integration & Demo

**Goal**: Connect all pieces and create demo scenarios

### Update Main Server

**File**: `deployment/local_agent_server.py`

**Integration Tasks**:
- [ ] Add all new endpoints
- [ ] Integrate registration flow
- [ ] Add A2A message handling
- [ ] Add static file serving
- [ ] Add WebSocket support (optional, for real-time updates)

**Startup Flow**:
1. Initialize TEE authenticator
2. Generate wallet address
3. Check if registered
4. If not registered: show funding page
5. If registered: check TEE verification
6. If not verified: trigger TEE registration
7. Start A2A server
8. Display dashboard

### Demo Scenarios

**File**: `examples/demo_scenarios.py` (new)

**Scenario 1: Agent Self-Registration**
```python
async def demo_self_registration():
    """Demonstrate complete registration flow"""
    # 1. Generate wallet
    # 2. Fund wallet (manual)
    # 3. Register on-chain
    # 4. Verify TEE
    # 5. Activate A2A
```

**Scenario 2: TEE Verification Proof**
```python
async def demo_tee_verification():
    """Demonstrate TEE attestation verification"""
    # 1. Generate attestation
    # 2. Create proof
    # 3. Submit on-chain
    # 4. Verify proof
```

**Scenario 3: A2A Message Exchange**
```python
async def demo_a2a_communication():
    """Demonstrate agent-to-agent messaging"""
    # 1. Agent A sends message to Agent B
    # 2. Agent B processes and responds
    # 3. Agent A receives response
```

**Scenario 4: Contract Interaction Verification**
```python
async def demo_contract_verification():
    """Verify all on-chain data"""
    # 1. Query Identity Registry
    # 2. Query TEE Registry
    # 3. Verify signatures match
    # 4. Check attestation validity
```

### Documentation

**Files**:
1. `docs/STAKEHOLDER_DEMO.md` - EF presentation guide
2. `docs/DEPLOYMENT.md` - Production deployment
3. `docs/A2A_INTEGRATION.md` - A2A protocol guide
4. `README.md` - Updated with new features

**STAKEHOLDER_DEMO.md** structure:
```markdown
# ERC-8004 TEE Agent Demonstration

## Executive Summary
## Architecture Overview
## Live Demonstration Steps
## Technical Deep Dive
## Security & Trust Model
## Roadmap & Next Steps
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Dashboard                    │
│  1. Fund Wallet → 2. Register → 3. Verify TEE → 4. A2A  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Server                         │
│  • /api/wallet         - Generate & display address      │
│  • /api/register       - Identity Registry registration  │
│  • /api/tee/register   - TEE attestation & verification  │
│  • /api/a2a/*          - A2A protocol endpoints          │
│  • /api/status/full    - Complete agent state            │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Smart Contracts (Base Sepolia)              │
│  • IdentityRegistry    - Agent registration              │
│  • TEERegistry         - TEE key verification            │
│  • zkVerifier          - Attestation proof verification  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   dstack TEE Environment                 │
│  • https://3af8f2...dstack-base-prod9.phala.network     │
│  • Intel TDX attestation generation                      │
│  • Secure key derivation                                 │
└─────────────────────────────────────────────────────────┘
```

---

## Deliverables

1. ✅ **Functional Agent Server** - All endpoints working
2. ✅ **Smart Contracts** - Deployed to Base Sepolia
3. ✅ **Web Dashboard** - Visual flow demonstration
4. ✅ **A2A Integration** - Working agent communication
5. ✅ **Documentation** - Complete guide for EF stakeholders
6. ✅ **Demo Script** - Step-by-step presentation flow

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.9+, FastAPI |
| Smart Contracts | Solidity ^0.8.20 |
| Frontend | HTML5, Tailwind CSS, Alpine.js |
| A2A Protocol | `@a2aproject/a2a-js` |
| TEE | dstack API (Intel TDX) |
| Blockchain | Base Sepolia (Chain ID: 84532) |
| Web3 | web3.py, ethers.js |

---

## Environment Variables

```bash
# Agent Identity
AGENT_DOMAIN="localhost:8000"
AGENT_SALT="production-salt-here"
AGENT_TYPE="server"

# Blockchain (Base Sepolia)
RPC_URL="https://sepolia.base.org"
CHAIN_ID="84532"
IDENTITY_REGISTRY_ADDRESS="0x19fad4adD9f8C4A129A078464B22E1506275FbDd"
TEE_REGISTRY_ADDRESS="<deploy-address>"
ZK_VERIFIER_ADDRESS="<deploy-address>"

# TEE
USE_TEE_AUTH="true"
TEE_ENDPOINT="https://3af8f2cbcd12330c938cd66efcf072694f48e105-8080.dstack-base-prod9.phala.network"

# Server
AGENT_HOST="0.0.0.0"
AGENT_PORT="8000"

# A2A
A2A_ENABLED="true"
```

---

## Timeline Estimate

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1 | Wallet generation & funding UI | 2-3 hours |
| Phase 2 | On-chain registration flow | 1-2 hours |
| Phase 3 | TEE verification & contracts | 4-6 hours |
| Phase 4 | A2A protocol integration | 3-4 hours |
| Phase 5 | Dashboard visualization | 2-3 hours |
| Phase 6 | Integration & demo scenarios | 2-3 hours |
| **Total** | | **14-21 hours** |

---

## Success Criteria

- [ ] Agent generates wallet and displays funding instructions
- [ ] Agent successfully registers on-chain with valid agent ID
- [ ] TEE attestation is verified and recorded on-chain
- [ ] A2A protocol communication works between agents
- [ ] Dashboard shows all steps visually
- [ ] Demo can be presented to Ethereum Foundation stakeholders
- [ ] All components are documented
- [ ] Code is production-ready and tested

---

## Next Steps

1. Review and approve this plan
2. Set up development environment
3. Begin Phase 1 implementation
4. Deploy smart contracts to testnet
5. Integrate all components
6. Test end-to-end flow
7. Create stakeholder presentation
8. Schedule demo with EF

---

## References

- [ERC-8004 Specification](https://github.com/h4x3rotab/dstack-erc8004-poc/blob/master/ERC-8004%20Trustless%20Agents%20v0.9.md)
- [TEERegistry Documentation](https://github.com/h4x3rotab/dstack-erc8004-poc/blob/master/CLAUDE.md)
- [A2A Protocol](https://github.com/a2aproject/a2a-js)
- [dstack Documentation](https://docs.phala.network/tech-specs/dstack)
- [Base Sepolia](https://docs.base.org/network-information)
