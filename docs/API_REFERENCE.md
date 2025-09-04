# API Reference

## Base URL
- Development: `http://localhost:8000`
- Production: Configured per deployment

## Authentication
Most endpoints require Bearer token authentication:
```http
Authorization: Bearer <token>
```

## Endpoints

### Health & Status

#### GET /health
Health check endpoint
```json
{
  "status": "healthy",
  "agents": {
    "server": {"agent_id": 1, "registered": true},
    "validator": {"agent_id": 2, "registered": true},
    "client": {"agent_id": 3, "registered": true}
  }
}
```

### Agent Operations

#### GET /agents
Get all registered agents
```json
{
  "server": {
    "agent_id": 1,
    "domain": "server.erc8004.local",
    "address": "0x...",
    "card": {...}
  },
  ...
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

### TEE Attestation

#### GET /attestation/{agent_type}
Get TEE attestation for agent
```json
{
  "attestation": {
    "has_attestation": true,
    "tee_endpoint": "/var/run/dstack.sock",
    "quote": "base64_encoded_quote",
    "agent_address": "0x..."
  }
}
```

### Workflow

#### POST /workflow/complete
Execute complete workflow
```json
// Request
{
  "symbol": "ETH",
  "timeframe": "4h"
}

// Response
{
  "workflow": {
    "analysis": {...},
    "validation": {...},
    "feedback": {...},
    "transactions": ["0x...", "0x..."]
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

# TEE
DSTACK_SIMULATOR_ENDPOINT=/path/to/socket

# AI/ML
OPENAI_API_KEY=your-openai-key
```