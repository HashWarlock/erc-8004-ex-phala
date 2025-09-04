# ERC-8004 Agent API

REST API and WebSocket interface for the trustless multi-agent system.

## Features

- **RESTful endpoints** for all agent operations
- **WebSocket support** for real-time updates
- **TEE attestation** endpoints for secure verification
- **OpenAPI documentation** with interactive testing
- **Authentication** via Bearer tokens
- **CORS support** for web frontends
- **Health checks** for monitoring

## Quick Start

### Running with Flox

```bash
# Start Anvil blockchain
flox activate -- anvil

# In another terminal, deploy contracts
flox activate -- make deploy

# Start API server
flox activate -- python run_api.py
```

### Running with Docker

```bash
# Build and run with docker-compose
docker-compose up api
```

## API Endpoints

### Health & Info

- `GET /health` - Health check
- `GET /agents` - List all agents
- `GET /agents/{agent_type}` - Get specific agent info

### Server Agent (Alice)

- `POST /server/analyze` - Request market analysis
  ```json
  {
    "symbol": "BTC",
    "timeframe": "1d",
    "indicators": ["trend", "volume", "sentiment"]
  }
  ```

### Validator Agent (Bob)

- `POST /validator/validate` - Validate analysis
  ```json
  {
    "analysis_data": {...},
    "server_agent_id": 1
  }
  ```

### Client Agent (Charlie)

- `POST /client/feedback/authorize` - Authorize feedback
  ```json
  {
    "server_agent_id": 1
  }
  ```

- `POST /client/feedback/submit` - Submit feedback
  ```json
  {
    "server_agent_id": 1,
    "score": 90,
    "comment": "Excellent service"
  }
  ```

- `GET /client/reputation/{server_agent_id}` - Check reputation

### Workflow

- `POST /workflow/complete` - Execute complete workflow
  ```json
  {
    "symbol": "BTC",
    "timeframe": "1d"
  }
  ```

### TEE Attestation

- `GET /attestation/{agent_type}` - Get TEE attestation

## WebSocket Interface

Connect to real-time updates:

```javascript
// Connect to all updates
const ws = new WebSocket('ws://localhost:8000/ws');

// Connect to specific agent channel
const wsServer = new WebSocket('ws://localhost:8000/ws/server');
const wsValidator = new WebSocket('ws://localhost:8000/ws/validator');
const wsClient = new WebSocket('ws://localhost:8000/ws/client');
```

### WebSocket Events

- `analysis_update` - Market analysis updates
- `validation_update` - Validation results
- `feedback_update` - Feedback submissions
- `agent_event` - General agent events

## Authentication

Set the `API_TOKEN` environment variable to enable authentication:

```bash
API_TOKEN=your-secure-token-here
```

Include the token in requests:

```bash
curl -H "Authorization: Bearer your-secure-token-here" \
  http://localhost:8000/agents
```

## Configuration

Environment variables:

- `API_HOST` - Host to bind (default: 0.0.0.0)
- `API_PORT` - Port to listen (default: 8000)
- `API_TOKEN` - Authentication token (optional)
- `API_WORKERS` - Number of workers (default: 1)
- `API_LOG_LEVEL` - Log level (default: info)
- `USE_TEE_AUTH` - Enable TEE authentication (default: false)

## API Documentation

Interactive documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

```bash
# Run API tests
flox activate -- pytest tests/api/test_api.py -v

# Test with curl
curl http://localhost:8000/health

# Test market analysis
curl -X POST http://localhost:8000/server/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC", "timeframe": "1d"}'
```

## Rate Limiting

The API includes built-in rate limiting to prevent abuse:
- 100 requests per minute per IP for general endpoints
- 10 requests per minute for analysis endpoints
- WebSocket connections limited to 10 per IP

## Error Handling

Standard HTTP status codes:
- `200` - Success
- `400` - Bad request
- `401` - Unauthorized
- `404` - Not found
- `429` - Rate limited
- `500` - Server error
- `503` - Service unavailable

Error response format:
```json
{
  "detail": "Error message",
  "status_code": 500,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Production Deployment

### With Gunicorn

```bash
gunicorn api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### With Docker

```bash
docker build -f api/Dockerfile -t erc8004-api .
docker run -p 8000:8000 --env-file .env erc8004-api
```

### With Kubernetes

See `k8s/api-deployment.yaml` for Kubernetes deployment configuration.

## Security Considerations

1. **Always use HTTPS in production** - Set up SSL certificates
2. **Secure API tokens** - Use strong, randomly generated tokens
3. **Configure CORS properly** - Restrict allowed origins
4. **Enable rate limiting** - Prevent DoS attacks
5. **Validate all inputs** - Pydantic models provide validation
6. **Monitor logs** - Track suspicious activity

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│   FastAPI    │────▶│   Agents    │
│  (Browser)  │     │   Server     │     │  (Python)   │
└─────────────┘     └──────────────┘     └─────────────┘
       │                    │                     │
       │                    │                     │
       ▼                    ▼                     ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  WebSocket  │     │   Pydantic   │     │ Blockchain  │
│   Updates   │     │  Validation  │     │  (Anvil)    │
└─────────────┘     └──────────────┘     └─────────────┘
```

## Monitoring

Health check endpoint for monitoring:

```bash
# Prometheus format
curl http://localhost:8000/metrics

# JSON health check
curl http://localhost:8000/health
```

## Contributing

1. Add new endpoints in `api/main.py`
2. Define models in `api/models.py`
3. Add WebSocket events in `api/websocket.py`
4. Write tests in `tests/api/`
5. Update this README

## License

MIT License - See LICENSE file for details