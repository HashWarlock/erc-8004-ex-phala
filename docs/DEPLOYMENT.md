# Deployment Guide

## Prerequisites

- Flox environment manager (required for all operations)
- Git
- 4GB RAM minimum
- Access to Phala Cloud (for production TEE deployment)

## Local Development Deployment

### 1. Environment Setup

```bash
# Clone repository
git clone <repository>
cd erc-8004-ex-phala

# Install Flox if not already installed
curl -fsSL https://downloads.flox.dev/by/flox/sh | sh

# Activate Flox environment (provides all dependencies)
flox activate
```

### 2. Configure Environment

```bash
# Copy example configuration
cp .env.example .env
```

The `.env` file includes two modes:

**TEE Mode (USE_TEE_AUTH=true) - Recommended:**
```bash
# TEE Authentication with deterministic keys
USE_TEE_AUTH=true

# Agent domains and salts for key derivation
SERVER_AGENT_DOMAIN=alice.example.com
SERVER_AGENT_SALT=server-secret-salt-2024
VALIDATOR_AGENT_DOMAIN=bob.example.com
VALIDATOR_AGENT_SALT=validator-secret-salt-2024
CLIENT_AGENT_DOMAIN=charlie.example.com
CLIENT_AGENT_SALT=client-secret-salt-2024
```

**Traditional Mode (USE_TEE_AUTH=false):**
```bash
# Use Anvil's default test keys
USE_TEE_AUTH=false
SERVER_AGENT_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
VALIDATOR_AGENT_KEY=0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d
CLIENT_AGENT_KEY=0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a
```

### 3. Start Services

```bash
# Terminal 1: Start Anvil blockchain
flox activate -- make anvil

# Terminal 2: Deploy contracts and fund wallets
flox activate -- make deploy
# This automatically funds TEE wallets if USE_TEE_AUTH=true

# Terminal 3: Start API server
flox activate -- python run_api.py
# The API auto-registers and funds agents on startup
```

### 4. Verify Deployment

```bash
# Check API health
curl http://localhost:8000/health

# Run end-to-end test
flox activate -- make test-e2e

# Or run complete demo
flox activate -- ./run_demo.sh

# Test with TEE mode explicitly
USE_TEE_AUTH=true flox activate -- ./run_demo.sh
```

## Phala Cloud Production Deployment

### 1. Build and Deploy to Phala Testnet

```bash
# Deploy contracts to Phala testnet
flox activate -- ./scripts/deploy_phala_testnet.sh

# Fund TEE wallets on testnet
flox activate -- python scripts/fund_tee_wallets.py
```

### 2. Configure for Phala Cloud

```bash
# Set production environment variables
export RPC_URL=https://poc6-rpc.phala.network
export CHAIN_ID=1001  # Phala testnet chain ID
export USE_TEE_AUTH=true

# Generate secure API token
export API_TOKEN=$(openssl rand -hex 32)
```

### 3. Deploy with Docker

```bash
# Build Docker image
docker build -t erc8004-agents .

# Run with TEE support
docker run -d \
  --name erc8004-agents \
  -p 8000:8000 \
  -e RPC_URL=$RPC_URL \
  -e CHAIN_ID=$CHAIN_ID \
  -e USE_TEE_AUTH=true \
  -e API_TOKEN=$API_TOKEN \
  -v /var/run/dstack.sock:/var/run/dstack.sock \
  erc8004-agents
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

Use the provided `docker-compose.yml`:

```bash
# Start all services
flox activate -- docker-compose up -d

# View logs
flox activate -- docker-compose logs -f

# Stop services
flox activate -- docker-compose down
```

The compose file includes:
- Anvil blockchain (for testing)
- API server with TEE support
- Automatic contract deployment
- Health monitoring

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

1. **Anvil not running**
   ```bash
   # Start in separate terminal
   flox activate -- make anvil
   ```

2. **Contracts not deployed**
   ```bash
   # Deploy and fund wallets
   flox activate -- make deploy
   ```

3. **TEE wallets not funded**
   ```bash
   # Fund TEE wallets
   flox activate -- make tee-fund
   ```

4. **Import errors**
   ```bash
   # Always use flox activate
   flox activate -- <command>
   ```

5. **Reset everything**
   ```bash
   flox activate -- make reset
   # Then start fresh
   ```

### Debug Commands

```bash
# Check TEE status
flox activate -- make tee-status

# View deployed contracts
cat deployed_contracts.json

# Check agent balances
flox activate -- python scripts/fund_tee_wallets.py

# Run full test suite
flox activate -- make test

# View API logs
tail -f api.log
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