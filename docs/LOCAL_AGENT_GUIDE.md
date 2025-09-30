# Local Agent Server Guide

Run ERC-8004 agent locally with HTTP API for interaction and TEE key verification.

---

## Quick Start

```bash
# From project root
./deployment/start_local_agent.sh
```

The server will start on `http://localhost:8000` with full API documentation at `http://localhost:8000/docs`.

---

## What This Does

The local agent server:

1. **Derives keys from TEE** - Uses real TEE hardware (Intel TDX via dstack) for secure key derivation
2. **Creates agent identity** - Generates deterministic Ethereum address from domain + salt
3. **Provides HTTP API** - Exposes endpoints for agent interaction and verification
4. **Demonstrates capabilities** - Shows TEE-secured signing and task processing
5. **Works without on-chain registration** - Runs independently while contract access is resolved

---

## API Endpoints

### `GET /`
Root endpoint with server information and available endpoints.

**Example:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "name": "ERC-8004 TEE Agent Server",
  "status": "operational",
  "domain": "localhost:8000",
  "address": "0x5d5A57CEFE52f59Ff9fD2A2f87F54BeE7D5587A7",
  "endpoints": {
    "status": "/api/status",
    "sign": "/api/sign",
    "process": "/api/process",
    "card": "/api/card",
    "attestation": "/api/attestation"
  }
}
```

---

### `GET /api/status`
Get agent status and identity information.

**Example:**
```bash
curl http://localhost:8000/api/status
```

**Response:**
```json
{
  "status": "operational",
  "agent": {
    "domain": "localhost:8000",
    "address": "0x5d5A57CEFE52f59Ff9fD2A2f87F54BeE7D5587A7",
    "agent_id": null,
    "is_registered": false,
    "chain_id": 84532
  },
  "tee": {
    "enabled": true,
    "endpoint": "/var/run/dstack.sock"
  },
  "timestamp": "2025-10-01T12:34:56.789"
}
```

---

### `POST /api/sign`
Sign a message with TEE-derived key. **This endpoint verifies the agent's cryptographic identity.**

**Example:**
```bash
curl -X POST http://localhost:8000/api/sign \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from agent!"}'
```

**Response:**
```json
{
  "message": "Hello from agent!",
  "message_hash": "0x1234...",
  "signature": "0xabcd...",
  "eip191_signature": "0x5678...",
  "signer_address": "0x5d5A57CEFE52f59Ff9fD2A2f87F54BeE7D5587A7",
  "domain": "localhost:8000",
  "timestamp": "2025-10-01T12:34:56.789",
  "verification": {
    "note": "Use eth_account.Account.recover_message() to verify EIP-191 signature",
    "expected_address": "0x5d5A57CEFE52f59Ff9fD2A2f87F54BeE7D5587A7"
  }
}
```

**Verify Signature (Python):**
```python
from eth_account import Account
from eth_account.messages import encode_defunct

# From API response
message = "Hello from agent!"
signature = "0x5678..."  # eip191_signature from response
expected_address = "0x5d5A57CEFE52f59Ff9fD2A2f87F54BeE7D5587A7"

# Verify
signable_message = encode_defunct(text=message)
recovered_address = Account.recover_message(signable_message, signature=signature)

assert recovered_address == expected_address
print(f"✅ Signature verified! Agent address: {recovered_address}")
```

---

### `POST /api/process`
Process a task with the agent.

**Example:**
```bash
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "task-001",
    "query": "market analysis",
    "data": {"symbol": "ETH", "timeframe": "7d"},
    "parameters": {"detail_level": "high"}
  }'
```

**Response:**
```json
{
  "task_id": "task-001",
  "agent_id": null,
  "status": "completed",
  "timestamp": "2025-10-01T12:34:56.789",
  "query": "market analysis",
  "analysis": {
    "type": "market_analysis",
    "summary": "Market conditions analyzed",
    "trends": ["bullish", "stable"],
    "volatility": "medium",
    "recommendations": [
      "Monitor key indicators",
      "Consider risk hedging"
    ],
    "data_points_analyzed": 1
  },
  "confidence": 0.85
}
```

---

### `GET /api/card`
Get ERC-8004 compliant agent card.

**Example:**
```bash
curl http://localhost:8000/api/card
```

**Response:**
```json
{
  "name": "TEE Server Agent - localhost:8000",
  "description": "Advanced TEE-secured server agent...",
  "version": "1.0.0",
  "capabilities": [
    {
      "name": "market-analysis",
      "description": "Analyze market trends using TEE-secured computations"
    },
    {
      "name": "trend-analysis",
      "description": "Identify and analyze trends in time-series data"
    }
  ],
  "transport": {
    "type": "http",
    "endpoint": "https://localhost:8000",
    "authentication": {
      "type": "eip712",
      "required": false
    }
  },
  "registrations": [
    {
      "registry": "eip155:84532:0x000c5A70B7269c5eD4238DcC6576e598614d3f70",
      "status": "pending",
      "agentId": null
    }
  ],
  "trustModels": [
    {
      "type": "tee-attestation",
      "provider": "phala-network",
      "endpoint": "https://localhost:8000/api/attestation"
    }
  ],
  "infrastructure": {
    "platform": "phala-network",
    "tee_type": "intel-tdx",
    "attestation_provider": "dstack",
    "deployment": "local"
  },
  "metadata": {
    "role": "server",
    "pricing": {
      "baseFeemWei": "1000000000000000",
      "currency": "ETH",
      "unit": "per-request"
    },
    "endpoints": {
      "process": "https://localhost:8000/api/process",
      "status": "https://localhost:8000/api/status",
      "metrics": "https://localhost:8000/api/metrics"
    }
  }
}
```

---

### `GET /api/attestation`
Get TEE attestation for the agent.

**Example:**
```bash
curl http://localhost:8000/api/attestation
```

**Response:**
```json
{
  "agent_address": "0x5d5A57CEFE52f59Ff9fD2A2f87F54BeE7D5587A7",
  "endpoint": "/var/run/dstack.sock",
  "application_data": {
    "raw": "abcd1234...",
    "domain": "localhost:8000",
    "address": "0x5d5A57CEFE52f59Ff9fD2A2f87F54BeE7D5587A7",
    "size": 64,
    "method": "hash"
  },
  "quote_size": 10020,
  "event_log_size": 2048,
  "quote_preview": "...",
  "timestamp": "2025-10-01T12:34:56.789"
}
```

---

### `GET /health`
Health check endpoint.

**Example:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-01T12:34:56.789"
}
```

---

## Verifying Agent Identity

The agent's identity is derived deterministically from:
1. **Domain**: `localhost:8000` (or custom domain)
2. **Salt**: Unique string for key derivation
3. **TEE**: Intel TDX secure enclave via dstack

### Verification Steps

1. **Get Agent Address**:
```bash
curl http://localhost:8000/api/status | jq -r '.agent.address'
# Output: 0x5d5A57CEFE52f59Ff9fD2A2f87F54BeE7D5587A7
```

2. **Sign a Test Message**:
```bash
curl -X POST http://localhost:8000/api/sign \
  -H "Content-Type: application/json" \
  -d '{"message": "test-message-123"}' | jq
```

3. **Verify Signature** (Python):
```python
from eth_account import Account
from eth_account.messages import encode_defunct

# From API response
message = "test-message-123"
signature = "0x..."  # eip191_signature from response
address = "0x5d5A57CEFE52f59Ff9fD2A2f87F54BeE7D5587A7"

# Verify
signable_message = encode_defunct(text=message)
recovered = Account.recover_message(signable_message, signature=signature)

print(f"Expected: {address}")
print(f"Recovered: {recovered}")
print(f"Match: {recovered.lower() == address.lower()}")
```

4. **Verify TEE Attestation**:
```bash
curl http://localhost:8000/api/attestation | jq
```

The attestation proves:
- Agent runs in Intel TDX TEE
- Key was derived securely
- Application data includes domain and address

---

## Configuration

Set environment variables before starting:

```bash
# Agent configuration
export AGENT_DOMAIN="localhost:8000"
export AGENT_SALT="local-development-salt"

# Server configuration
export AGENT_HOST="0.0.0.0"
export AGENT_PORT="8000"

# Start server
./deployment/start_local_agent.sh
```

---

## Testing Workflow

### 1. Start Server
```bash
./deployment/start_local_agent.sh
```

### 2. Check Status
```bash
curl http://localhost:8000/api/status | jq
```

### 3. Verify Agent Identity
```bash
# Get address
ADDRESS=$(curl -s http://localhost:8000/api/status | jq -r '.agent.address')
echo "Agent Address: $ADDRESS"

# Sign message
curl -X POST http://localhost:8000/api/sign \
  -H "Content-Type: application/json" \
  -d '{"message": "verify-identity"}' | jq
```

### 4. Test Task Processing
```bash
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "test-001",
    "query": "market analysis",
    "data": {},
    "parameters": {}
  }' | jq
```

### 5. Get Agent Card
```bash
curl http://localhost:8000/api/card | jq
```

### 6. Get TEE Attestation
```bash
curl http://localhost:8000/api/attestation | jq
```

---

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Get agent status
response = requests.get(f"{BASE_URL}/api/status")
status = response.json()
print(f"Agent Address: {status['agent']['address']}")

# Sign a message
response = requests.post(
    f"{BASE_URL}/api/sign",
    json={"message": "Hello from client!"}
)
signature_data = response.json()
print(f"Signature: {signature_data['eip191_signature'][:20]}...")

# Verify signature
from eth_account import Account
from eth_account.messages import encode_defunct

message = signature_data['message']
signature = signature_data['eip191_signature']
signable = encode_defunct(text=message)
recovered = Account.recover_message(signable, signature=signature)

assert recovered.lower() == signature_data['signer_address'].lower()
print(f"✅ Signature verified!")

# Process task
response = requests.post(
    f"{BASE_URL}/api/process",
    json={
        "task_id": "task-123",
        "query": "analyze market data",
        "data": {"symbol": "ETH"}
    }
)
result = response.json()
print(f"Task Status: {result['status']}")
print(f"Analysis: {result.get('analysis', {}).get('summary')}")
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Local Agent Server                       │
│                   (FastAPI + uvicorn)                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Endpoints:                                                 │
│  • GET  /              - Server info                       │
│  • GET  /api/status    - Agent status & identity           │
│  • POST /api/sign      - Sign message with TEE key         │
│  • POST /api/process   - Process tasks                     │
│  • GET  /api/card      - ERC-8004 agent card               │
│  • GET  /api/attestation - TEE attestation                 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Agent Layer:                                               │
│  • ServerAgent         - Task processing logic             │
│  • AgentCardBuilder    - ERC-8004 compliance               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TEE Layer:                                                 │
│  • TEEAuthenticator    - Key derivation                    │
│  • DstackClient        - TEE operations                    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Intel TDX TEE (via dstack)                                │
│  • Secure key derivation                                    │
│  • Remote attestation                                       │
│  • Message signing                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Features

### ✅ TEE-Derived Keys
- Keys derived deterministically from domain + salt
- Secure key material never leaves TEE
- Same domain + salt = same address (reproducible)

### ✅ Cryptographic Verification
- Sign messages with TEE-derived key
- Verify signatures match expected address
- Prove agent identity cryptographically

### ✅ ERC-8004 Compliance
- Full agent card generation
- Capability definitions
- Transport and infrastructure metadata

### ✅ TEE Attestation
- Real Intel TDX attestations (~10KB)
- Application data includes domain + address
- Verifiable by third parties

### ✅ Works Offline
- No blockchain connection required
- Independent of on-chain registration
- Demonstrates agent capabilities locally

---

## Troubleshooting

### "No TEE environment detected!"
**Solution**: This server requires a TEE environment. Run in Phala's TEE infrastructure or with dstack simulator.

### "Agent not initialized"
**Solution**: Wait for server startup to complete. Check logs for errors during initialization.

### Import errors (fastapi, uvicorn)
**Solution**: Install dependencies:
```bash
pip install fastapi uvicorn[standard]
```

### Signature verification fails
**Solution**: Ensure you're using the `eip191_signature` field (not `signature`) for standard verification.

---

## Next Steps

1. **Test locally**: Run server and verify all endpoints work
2. **Verify identity**: Use signing endpoint to prove cryptographic identity
3. **Process tasks**: Test agent's analytical capabilities
4. **Get attestation**: Verify TEE attestation generation
5. **Deploy remotely**: Once contract access is resolved, deploy with public domain
6. **Register on-chain**: Complete ERC-8004 registration when contract is accessible

---

## Files

- **Server**: [deployment/local_agent_server.py](deployment/local_agent_server.py)
- **Startup Script**: [deployment/start_local_agent.sh](deployment/start_local_agent.sh)
- **Agent Implementation**: [src/templates/server_agent.py](src/templates/server_agent.py)
- **TEE Auth**: [src/agent/tee_auth.py](src/agent/tee_auth.py)
- **Agent Cards**: [src/agent/agent_card.py](src/agent/agent_card.py)

---

## Status

✅ **Ready for local testing**
- Server implementation complete
- All endpoints functional
- TEE integration verified
- ERC-8004 compliance confirmed

⏳ **Waiting for on-chain registration**
- Contract access control needs resolution
- See [CONTRACT_INVESTIGATION.md](CONTRACT_INVESTIGATION.md)
- Agent works independently in the meantime
