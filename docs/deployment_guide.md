# Deployment Guide

Complete guide for deploying ERC-8004 TEE agents to production.

## Table of Contents

- [Overview](#overview)
- [Deployment Options](#deployment-options)
- [Phala Cloud Deployment](#phala-cloud-deployment)
- [Local TEE Simulator](#local-tee-simulator)
- [Blockchain Configuration](#blockchain-configuration)
- [Production Checklist](#production-checklist)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

---

## Overview

TEE agents can be deployed in three environments:

1. **Development** - Local testing without TEE
2. **Staging** - TEE simulator for integration testing
3. **Production** - Phala Cloud with real TEE hardware

## Deployment Options

### Quick Comparison

| Environment | TEE Required | Blockchain | Use Case |
|------------|--------------|------------|----------|
| Development | No | Testnet/Mock | Local testing |
| Staging | Simulator | Testnet | Integration testing |
| Production | Yes | Mainnet/Testnet | Live deployment |

---

## Phala Cloud Deployment

### Prerequisites

1. **Phala Cloud Account**
   - Register at [Phala Cloud](https://phala.network/cloud)
   - Get API credentials

2. **Agent Code Ready**
   - Tested locally
   - Dependencies resolved
   - Configuration complete

3. **Blockchain Setup**
   - Wallet funded with gas tokens
   - Contract addresses configured

### Step 1: Prepare Your Agent

```bash
# Clone and configure
git clone your-agent-repo
cd your-agent

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production values
```

### Step 2: Configure for Production

```env
# .env for production
USE_TEE_AUTH=true
SKIP_REGISTRATION=false

# Phala Cloud
PHALA_CLOUD_API_KEY=your-api-key
PHALA_CLOUD_ENDPOINT=https://api.phala.network

# Network (Base Mainnet example)
RPC_URL=https://mainnet.base.org
CHAIN_ID=8453

# Registry Contracts (update with mainnet addresses)
IDENTITY_REGISTRY_ADDRESS=0x...
REPUTATION_REGISTRY_ADDRESS=0x...
VALIDATION_REGISTRY_ADDRESS=0x...
TEE_VERIFIER_ADDRESS=0x...
```

### Step 3: Deploy to Phala Cloud

```bash
# Using deployment script
python scripts/deploy_agent.py \
  --environment production \
  --config .env \
  --name "my-agent"

# Or using Phala CLI
phala-cli deploy \
  --project . \
  --config .env \
  --name "my-agent"
```

### Step 4: Verify Deployment

```bash
# Check deployment status
python scripts/check_deployment.py

# Expected output:
# ✅ Agent deployed successfully
# ✅ TEE attestation valid
# ✅ Registered with ERC-8004
# ✅ Ready to receive tasks
```

### Step 5: Register with ERC-8004

```python
# Automatic registration during deployment
# Or manually:
python scripts/register_agent.py \
  --domain "my-agent.phala.network" \
  --endpoint "https://my-agent.phala.network"
```

---

## Local TEE Simulator

For testing TEE functionality without hardware.

### Setup Simulator

```bash
# Using Docker
docker run -d \
  --name tee-simulator \
  -p 8090:8090 \
  phalanetwork/tee-simulator:latest

# Verify it's running
curl http://localhost:8090/health
```

### Configure Agent

```env
# .env for simulator
USE_TEE_AUTH=true
DSTACK_SIMULATOR_ENDPOINT=http://localhost:8090

# Use testnet
RPC_URL=https://sepolia.base.org
CHAIN_ID=84532
```

### Test with Simulator

```python
# test_with_simulator.py
import asyncio
from src.agent.tee_auth import TEEAuthenticator

async def test_tee():
    auth = TEEAuthenticator(
        domain="test.local",
        salt="test-salt",
        use_tee=True
    )

    # Test key derivation
    address = await auth.derive_address()
    print(f"Derived address: {address}")

    # Test attestation
    attestation = await auth.get_attestation()
    print(f"Got attestation: {attestation['quote'][:32]}...")

asyncio.run(test_tee())
```

---

## Blockchain Configuration

### Network Selection

#### Base Mainnet
```env
RPC_URL=https://mainnet.base.org
CHAIN_ID=8453
EXPLORER=https://basescan.org
```

#### Base Sepolia (Testnet)
```env
RPC_URL=https://sepolia.base.org
CHAIN_ID=84532
EXPLORER=https://sepolia.basescan.org
```

#### Ethereum Mainnet
```env
RPC_URL=https://eth.llamarpc.com
CHAIN_ID=1
EXPLORER=https://etherscan.io
```

### Gas Configuration

```python
# config/gas.py
GAS_SETTINGS = {
    'base_mainnet': {
        'max_fee_per_gas': 1_000_000_000,  # 1 gwei
        'max_priority_fee': 100_000_000,   # 0.1 gwei
    },
    'ethereum_mainnet': {
        'max_fee_per_gas': 30_000_000_000,  # 30 gwei
        'max_priority_fee': 2_000_000_000,  # 2 gwei
    }
}
```

### Contract Deployment

If deploying your own contracts:

```bash
# Deploy contracts
cd contracts/
npx hardhat deploy --network base-mainnet

# Update addresses in .env
IDENTITY_REGISTRY_ADDRESS=0x...new_address
REPUTATION_REGISTRY_ADDRESS=0x...new_address
```

---

## Production Checklist

### Pre-Deployment

- [ ] **Code Review**
  - [ ] Security audit completed
  - [ ] No hardcoded secrets
  - [ ] Error handling implemented

- [ ] **Testing**
  - [ ] Unit tests passing
  - [ ] Integration tests passing
  - [ ] TEE simulator tests passing

- [ ] **Configuration**
  - [ ] Production environment variables set
  - [ ] Mainnet contract addresses configured
  - [ ] Gas settings optimized

- [ ] **Dependencies**
  - [ ] All packages pinned to versions
  - [ ] Security vulnerabilities checked
  - [ ] License compliance verified

### Deployment

- [ ] **Infrastructure**
  - [ ] Phala Cloud account active
  - [ ] API credentials secured
  - [ ] Monitoring configured

- [ ] **Blockchain**
  - [ ] Wallet funded with gas
  - [ ] Contract interactions tested
  - [ ] Gas estimates calculated

- [ ] **Security**
  - [ ] TEE attestation verified
  - [ ] Private keys secured
  - [ ] Access controls configured

### Post-Deployment

- [ ] **Verification**
  - [ ] Agent responding to health checks
  - [ ] TEE attestation valid
  - [ ] Registry registration confirmed

- [ ] **Monitoring**
  - [ ] Logs accessible
  - [ ] Metrics dashboard live
  - [ ] Alerts configured

- [ ] **Documentation**
  - [ ] Deployment documented
  - [ ] Runbook created
  - [ ] Team trained

---

## Monitoring & Maintenance

### Health Checks

```python
# health_check.py
import aiohttp
import asyncio

async def check_agent_health(endpoint):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{endpoint}/health") as resp:
            if resp.status == 200:
                data = await resp.json()
                return data['status'] == 'healthy'
    return False

# Run periodic health checks
async def monitor():
    while True:
        is_healthy = await check_agent_health("https://my-agent.phala.network")
        if not is_healthy:
            send_alert("Agent unhealthy!")
        await asyncio.sleep(60)  # Check every minute
```

### Logging

```python
# Configure logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Metrics Collection

```python
# metrics.py
from prometheus_client import Counter, Histogram, start_http_server

# Define metrics
task_counter = Counter('tasks_processed', 'Total tasks processed')
task_duration = Histogram('task_duration_seconds', 'Task processing duration')

# Start metrics server
start_http_server(8000)

# Use in agent
@task_duration.time()
async def process_task(self, task_data):
    result = await self._process(task_data)
    task_counter.inc()
    return result
```

### Automated Backups

```bash
#!/bin/bash
# backup.sh

# Backup agent state
tar -czf agent_backup_$(date +%Y%m%d).tar.gz \
  ./data \
  ./.env \
  ./logs

# Upload to S3
aws s3 cp agent_backup_*.tar.gz s3://my-backups/agents/

# Clean old backups
find . -name "agent_backup_*.tar.gz" -mtime +7 -delete
```

---

## Troubleshooting

### Common Issues

#### TEE Attestation Fails

```bash
# Error: TEE attestation failed
# Solution 1: Check TEE service status
curl http://localhost:8090/health

# Solution 2: Restart TEE simulator
docker restart tee-simulator

# Solution 3: Check attestation data is 64 bytes
python -c "
data = b'test' * 16  # Must be exactly 64 bytes
print(len(data))
"
```

#### Registration Fails

```bash
# Error: Agent registration failed
# Solution 1: Check gas balance
cast balance 0xYourAddress --rpc-url https://sepolia.base.org

# Solution 2: Verify contract address
cast call 0xContractAddress "owner()" --rpc-url https://sepolia.base.org

# Solution 3: Check network connectivity
curl https://sepolia.base.org
```

#### Agent Not Responding

```python
# Debug script
async def debug_agent():
    # Check process
    import psutil
    for proc in psutil.process_iter(['pid', 'name']):
        if 'python' in proc.info['name']:
            print(f"Python process: {proc.info}")

    # Check port
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8080))
    print(f"Port 8080 open: {result == 0}")

    # Check logs
    with open('agent.log', 'r') as f:
        print(f.readlines()[-10:])  # Last 10 lines
```

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `TEE001` | TEE initialization failed | Check TEE service |
| `TEE002` | Attestation failed | Verify 64-byte data |
| `REG001` | Registration failed | Check gas and contract |
| `NET001` | Network error | Verify RPC endpoint |
| `AUTH001` | Authentication failed | Check credentials |

### Getting Help

1. **Check Logs**
   ```bash
   tail -f agent.log
   grep ERROR agent.log
   ```

2. **Run Diagnostics**
   ```bash
   python scripts/diagnose.py
   ```

3. **Community Support**
   - Discord: [Join Server](https://discord.gg/...)
   - GitHub Issues: [Report Issue](https://github.com/...)

---

## Advanced Deployment

### Multi-Region Deployment

```yaml
# deploy-config.yaml
regions:
  - name: us-east
    endpoint: https://us-east.phala.network
    replicas: 3
  - name: eu-west
    endpoint: https://eu-west.phala.network
    replicas: 2
  - name: asia-pacific
    endpoint: https://ap.phala.network
    replicas: 2
```

### Load Balancing

```nginx
# nginx.conf
upstream agents {
    server agent1.phala.network:8080;
    server agent2.phala.network:8080;
    server agent3.phala.network:8080;
}

server {
    listen 443 ssl;
    server_name my-agent.com;

    location / {
        proxy_pass http://agents;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Auto-Scaling

```python
# autoscale.py
async def auto_scale(current_load):
    if current_load > 80:
        # Scale up
        await deploy_new_instance()
    elif current_load < 20:
        # Scale down
        await remove_instance()
```

---

## Security Best Practices

1. **Never commit private keys**
   ```bash
   # .gitignore
   .env
   *.key
   *.pem
   ```

2. **Use secret management**
   ```python
   import os
   from dotenv import load_dotenv
   load_dotenv()

   # Or use cloud secrets
   from aws_secretsmanager import get_secret
   api_key = get_secret("phala_api_key")
   ```

3. **Regular updates**
   ```bash
   # Update dependencies weekly
   pip install --upgrade -r requirements.txt
   ```

4. **Audit logs**
   ```python
   logger.info(f"Task processed by {agent_id}: {task_id}")
   ```

---

## Conclusion

You now have everything needed to deploy TEE agents to production:
- ✅ Phala Cloud deployment steps
- ✅ TEE simulator for testing
- ✅ Production checklist
- ✅ Monitoring setup
- ✅ Troubleshooting guide

For additional support:
- 📚 [API Reference](api_reference.md)
- 🚀 [Quickstart Guide](quickstart.md)
- 💡 [Examples](../examples/)
- 💬 [Community Support](https://discord.gg/...)