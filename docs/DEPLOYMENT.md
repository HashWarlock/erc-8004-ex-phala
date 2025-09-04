# Deployment Guide

## Prerequisites

- Flox environment manager
- Docker and Docker Compose
- Node.js (for contract deployment)
- Python 3.10+
- Access to Phala Cloud (for production)

## Local Development Deployment

### 1. Environment Setup

```bash
# Clone repository
git clone <repository>
cd erc-8004-ex-phala

# Initialize Flox environment
flox activate

# Install dependencies
make install
```

### 2. Configure Environment

Create `.env` file:
```bash
# Blockchain
RPC_URL=http://127.0.0.1:8545
CHAIN_ID=31337

# Agent Keys (for development)
SERVER_AGENT_KEY=0x...
VALIDATOR_AGENT_KEY=0x...
CLIENT_AGENT_KEY=0x...

# API
API_TOKEN=your-secure-token
API_PORT=8000

# TEE Simulator
DSTACK_SIMULATOR_ENDPOINT=.dstack/sdk/simulator/dstack.sock
DEVELOPMENT_MODE=true

# AI/ML (optional)
OPENAI_API_KEY=your-key
```

### 3. Start Services

```bash
# Start services individually (no combined start command):
make anvil          # Terminal 1: Start local blockchain
make tee-start      # Terminal 2: Start TEE simulator
make deploy         # Terminal 3: Deploy contracts (after anvil is running)
# API server: python run_api.py (if available)
```

### 4. Verify Deployment

```bash
# Check health
curl http://localhost:8000/health

# Run tests
make test
```

## Phala Cloud Production Deployment

### 1. Prepare Container Image

```bash
# Build with Flox
flox containerize

# Or use Docker
docker build -t erc8004-agents .
```

### 2. Configure Phala CVM

Create `phala-config.yml`:
```yaml
version: '1.0'
name: erc8004-agents
image: erc8004-agents:latest

resources:
  cpu: 2
  memory: 4096
  storage: 10

network:
  ports:
    - 8000:8000
  
env:
  RPC_URL: ${RPC_URL}
  CHAIN_ID: ${CHAIN_ID}
  API_TOKEN: ${API_TOKEN}
  
tee:
  enabled: true
  attestation: required
```

### 3. Deploy to Phala Cloud

```bash
# Login to Phala Cloud
phala login

# Deploy CVM
phala deploy --config phala-config.yml

# Get deployment info
phala status erc8004-agents
```

### 4. Configure Production Environment

```bash
# Set production variables
phala env set RPC_URL https://your-rpc-endpoint
phala env set CHAIN_ID 1
phala env set API_TOKEN $(openssl rand -hex 32)

# Deploy contracts to production chain
forge script contracts/script/Deploy.s.sol \
  --rpc-url $RPC_URL \
  --broadcast \
  --verify
```

### 5. DNS and SSL Setup

```bash
# Configure domain
phala domain add agents.yourdomain.com

# Enable SSL
phala ssl enable --domain agents.yourdomain.com
```

## Docker Compose Deployment

### 1. Production docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    image: erc8004-agents:latest
    ports:
      - "8000:8000"
    environment:
      - RPC_URL=${RPC_URL}
      - CHAIN_ID=${CHAIN_ID}
      - API_TOKEN=${API_TOKEN}
      - DSTACK_ENDPOINT=/var/run/dstack.sock
    volumes:
      - /var/run/dstack.sock:/var/run/dstack.sock
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped
```

### 2. Start Services

```bash
docker-compose up -d
```

## Kubernetes Deployment

### 1. Create Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: erc8004-agents
spec:
  replicas: 3
  selector:
    matchLabels:
      app: erc8004-agents
  template:
    metadata:
      labels:
        app: erc8004-agents
    spec:
      containers:
      - name: api
        image: erc8004-agents:latest
        ports:
        - containerPort: 8000
        env:
        - name: RPC_URL
          valueFrom:
            secretKeyRef:
              name: erc8004-secrets
              key: rpc-url
```

### 2. Apply Configuration

```bash
kubectl apply -f k8s-deployment.yaml
kubectl apply -f k8s-service.yaml
kubectl apply -f k8s-ingress.yaml
```

## Monitoring and Logging

### 1. Health Checks

```bash
# API health
curl https://api.yourdomain.com/health

# TEE attestation
curl https://api.yourdomain.com/attestation/server
```

### 2. Logs

```bash
# Docker logs
docker logs erc8004-agents-api

# Phala Cloud logs
phala logs erc8004-agents

# Kubernetes logs
kubectl logs -f deployment/erc8004-agents
```

### 3. Metrics

Configure Prometheus/Grafana for monitoring:
- API response times
- Agent registration events
- TEE attestation success rate
- Blockchain transaction metrics

## Troubleshooting

### Common Issues

1. **TEE Connection Failed**
   - Verify dstack socket path
   - Check TEE simulator is running
   - Ensure proper permissions

2. **Contract Deployment Failed**
   - Check RPC URL connectivity
   - Verify account has sufficient funds
   - Ensure correct chain ID

3. **API Not Responding**
   - Check port availability
   - Verify environment variables
   - Review API logs

### Debug Commands

```bash
# Test TEE connection
make tee-status

# Verify contracts are deployed
cat deployed_contracts.json

# Test the system
make test
```

## Security Considerations

1. **Private Keys**: Never commit private keys
2. **API Tokens**: Use strong, unique tokens
3. **SSL/TLS**: Always use HTTPS in production
4. **Firewall**: Restrict access to necessary ports
5. **Updates**: Keep dependencies updated

## Backup and Recovery

### Backup

```bash
# Backup contract addresses
cp deployed_contracts.json backups/

# Backup agent data
docker exec api python -c "import json; ..."
```

### Recovery

```bash
# Restore from backup
cp backups/deployed_contracts.json .

# Restart services
docker-compose restart
```