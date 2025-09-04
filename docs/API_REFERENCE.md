# API Reference

## Base URL
- Development: `http://localhost:8000`
- Production: Configured per deployment

## Features
- ERC-8004 compliant agent operations
- Phala Cloud TEE integration for secure key management
- Automatic wallet funding for TEE agents
- Real-time WebSocket updates
- Complete workflow automation

## Authentication
Most endpoints require Bearer token authentication:
```http
Authorization: Bearer <token>
```

## TEE Mode
When `USE_TEE_AUTH=true`, agents use deterministic key derivation via Phala's TEE simulator. The API automatically funds TEE wallets on startup.

## Endpoints

### Health & Status

#### GET /health
Health check endpoint with agent registration status
```json
{
  "status": "healthy",
  "tee_mode": true,
  "agents": {
    "server": {
      "agent_id": 1,
      "registered": true,
      "address": "0xC6aB3F953c7F0B33B1E9056Fa6f795B329c3323D",
      "domain": "alice.example.com"
    },
    "validator": {
      "agent_id": 2,
      "registered": true,
      "address": "0x83247F3B9772D2b0220A08b8fF01E95A28f7423F",
      "domain": "bob.example.com"
    },
    "client": {
      "agent_id": 3,
      "registered": true,
      "address": "0x54AF215206E971ADE501373E0a6Ace7369B5c22d",
      "domain": "charlie.example.com"
    }
  },
  "blockchain": {
    "connected": true,
    "chain_id": 31337,
    "rpc_url": "http://localhost:8545"
  }
}
```

### Agent Operations

#### GET /agents
Get all registered agents with their TEE or traditional configuration
```json
{
  "server": {
    "agent_id": 1,
    "domain": "alice.example.com",
    "address": "0xC6aB3F953c7F0B33B1E9056Fa6f795B329c3323D",
    "tee_enabled": true,
    "balance_eth": "0.1",
    "card": {
      "name": "Market Analysis Server",
      "description": "AI-powered market analysis agent"
    }
  },
  "validator": {
    "agent_id": 2,
    "domain": "bob.example.com",
    "address": "0x83247F3B9772D2b0220A08b8fF01E95A28f7423F",
    "tee_enabled": true,
    "balance_eth": "0.1",
    "card": {
      "name": "Work Validator",
      "description": "Validates analysis quality"
    }
  },
  "client": {
    "agent_id": 3,
    "domain": "charlie.example.com",
    "address": "0x54AF215206E971ADE501373E0a6Ace7369B5c22d",
    "tee_enabled": true,
    "balance_eth": "0.1",
    "card": {
      "name": "Feedback Client",
      "description": "Provides service feedback"
    }
  }
}
```

#### GET /agents/{agent_type}
Get specific agent information
- `agent_type`: server | validator | client

### Server Agent

#### POST /server/analyze
Perform market analysis
```json
// Request
{
  "symbol": "BTC",
  "timeframe": "1d",
  "indicators": ["trend", "volume"]
}

// Response
{
  "agent_id": 1,
  "analysis": {
    "symbol": "BTC",
    "timeframe": "1d",
    "trend": "bullish",
    "confidence": 85,
    "recommendation": "BUY"
  }
}
```

#### POST /server/validate
Submit work for validation
```json
// Request
{
  "analysis_data": {...},
  "validator_agent_id": 2
}

// Response
{
  "transaction_hash": "0x...",
  "validation_requested": true
}
```

### Validator Agent

#### POST /validator/validate
Validate analysis work
```json
// Request
{
  "analysis_data": {...},
  "server_agent_id": 1
}

// Response
{
  "agent_id": 2,
  "validation": {
    "is_valid": true,
    "score": 92,
    "confidence": 88
  }
}
```

#### GET /validator/pending
Get pending validation requests
```json
{
  "pending": [
    {
      "request_id": "0x...",
      "server_agent_id": 1,
      "data_hash": "0x...",
      "timestamp": 1234567890
    }
  ]
}
```

### Client Agent

#### POST /client/feedback/authorize
Authorize feedback submission
```json
// Request
{
  "server_agent_id": 1
}

// Response
{
  "transaction_hash": "0x...",
  "authorized": true
}
```

#### POST /client/feedback/submit
Submit feedback for service
```json
// Request
{
  "server_agent_id": 1,
  "score": 85,
  "comment": "Excellent analysis"
}

// Response
{
  "feedback": {
    "client_id": 3,
    "server_id": 1,
    "score": 85,
    "timestamp": 1234567890
  }
}
```

#### GET /client/reputation/{server_id}
Check server reputation
```json
{
  "reputation": {
    "server_id": 1,
    "feedback_count": 10,
    "average_score": 87.5,
    "trust_level": "high"
  }
}
```

### TEE Operations

#### GET /tee/status
Get TEE simulator status and configuration
```json
{
  "tee_enabled": true,
  "simulator_endpoint": ".dstack/sdk/simulator/dstack.sock",
  "simulator_active": true,
  "agents": {
    "server": {
      "domain": "alice.example.com",
      "address": "0xC6aB3F953c7F0B33B1E9056Fa6f795B329c3323D",
      "funded": true,
      "balance_eth": "0.1"
    },
    "validator": {
      "domain": "bob.example.com",
      "address": "0x83247F3B9772D2b0220A08b8fF01E95A28f7423F",
      "funded": true,
      "balance_eth": "0.1"
    },
    "client": {
      "domain": "charlie.example.com",
      "address": "0x54AF215206E971ADE501373E0a6Ace7369B5c22d",
      "funded": true,
      "balance_eth": "0.1"
    }
  }
}
```

#### POST /tee/fund
Manually trigger TEE wallet funding
```json
// Response
{
  "funded": ["server", "validator", "client"],
  "already_funded": [],
  "total_eth_sent": "0.3"
}
```

### Workflow

#### POST /workflow/complete
Execute complete workflow with all agent interactions
```json
// Request
{
  "symbol": "ETH",
  "timeframe": "4h",
  "auto_fund": true  // Auto-fund agents if needed
}

// Response
{
  "workflow": {
    "agents_registered": true,
    "tee_mode": true,
    "analysis": {
      "symbol": "ETH",
      "trend": "bullish",
      "confidence": 87
    },
    "validation": {
      "is_valid": true,
      "score": 92
    },
    "feedback": {
      "submitted": true,
      "score": 85
    },
    "transactions": [
      "0x...analysis_tx",
      "0x...validation_tx",
      "0x...feedback_tx"
    ],
    "reputation_updated": true
  }
}
```

### WebSocket Endpoints

#### WS /ws
Main WebSocket connection for all events

#### WS /ws/{agent_type}
Agent-specific WebSocket channels

Message format:
```json
{
  "event": "analysis_completed",
  "agent_type": "server",
  "data": {...},
  "timestamp": 1234567890
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or missing authentication token"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "error": "Detailed error message"
}
```

## Rate Limiting

- Default: 100 requests per minute per IP
- WebSocket: 10 connections per IP
- Configurable via environment variables

## CORS Configuration

Default allowed origins:
- `http://localhost:*`
- Configured production domains

## Environment Variables

```bash
# API Configuration
API_TOKEN=your-api-token
API_PORT=8000

# Blockchain
RPC_URL=http://127.0.0.1:8545
CHAIN_ID=31337

# TEE Authentication Mode
USE_TEE_AUTH=true  # Enable Phala Cloud TEE mode

# TEE Agent Configuration (for deterministic keys)
SERVER_AGENT_DOMAIN=alice.example.com
SERVER_AGENT_SALT=server-secret-salt-2024
VALIDATOR_AGENT_DOMAIN=bob.example.com
VALIDATOR_AGENT_SALT=validator-secret-salt-2024
CLIENT_AGENT_DOMAIN=charlie.example.com
CLIENT_AGENT_SALT=client-secret-salt-2024

# Traditional Mode Keys (when USE_TEE_AUTH=false)
SERVER_AGENT_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
VALIDATOR_AGENT_KEY=0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d
CLIENT_AGENT_KEY=0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a

# TEE Simulator
DSTACK_SIMULATOR_ENDPOINT=.dstack/sdk/simulator/dstack.sock

# AI/ML (Optional)
OPENAI_API_KEY=your-openai-key
```