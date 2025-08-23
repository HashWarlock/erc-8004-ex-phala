# Phala Cloud CVM Deployment Guide

## Overview

This guide covers deploying the ERC-8004 Trustless Agents to Phala Cloud's Confidential VM (CVM) infrastructure with TEE attestation support.

## Prerequisites

1. **Phala Cloud Account**: Register at [https://phala.network](https://phala.network)
2. **Container Image**: Built using `flox containerize`
3. **Deployed Contracts**: ERC-8004 contracts deployed to target blockchain
4. **Environment Variables**: Configured in `.env` file

## Container Build Process

### 1. Build Container with Flox

```bash
# Build OCI container from Flox environment
flox containerize --dir=. --runtime=docker --tag=erc8004-phala

# Verify image
docker images | grep erc8004
```

The Flox-built container includes:
- Python 3.11+ with virtual environment
- dstack SDK for TEE operations
- Web3.py for blockchain interaction
- All project dependencies

### 2. Push to Container Registry

```bash
# Tag for your registry
docker tag erc-8004-ex-phala:erc8004-phala your-registry/erc8004-phala:latest

# Push to registry
docker push your-registry/erc8004-phala:latest
```

## Deployment Configuration

### docker-compose.yml

The `docker-compose.yml` is configured for Phala Cloud deployment:

```yaml
version: '3.8'

services:
  app:
    image: erc-8004-ex-phala:erc8004-phala
    environment:
      - AGENT_TYPE=${AGENT_TYPE:-server}
      - RPC_URL=${RPC_URL}
      - PRIVATE_KEY=${PRIVATE_KEY}
      - CONTRACT_ADDRESS=${CONTRACT_ADDRESS}
    volumes:
      - /var/run/tappd.sock:/var/run/tappd.sock  # TEE socket
    ports:
      - "8080:8080"
    command: ["-c", "python -m agents.server_agent"]
```

### app-compose.json (dstack-specific)

For dstack SDK deployments, `app-compose.json` embeds the Docker Compose configuration:

```json
{
  "manifest_version": 1,
  "name": "erc8004-trustless-agents",
  "runner": "docker-compose",
  "docker_compose_file": "...",  // Embedded YAML
  "public_tcbinfo": true,
  "kms_enabled": true,
  "allowed_envs": ["RPC_URL", "PRIVATE_KEY", "CONTRACT_ADDRESS"]
}
```

## Environment Variables

Create `.env` file with your configuration:

```bash
# Blockchain Configuration
RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
PRIVATE_KEY=0x_YOUR_PRIVATE_KEY
CONTRACT_ADDRESS=0x_DEPLOYED_CONTRACT_ADDRESS

# Agent Configuration
AGENT_TYPE=server  # server, validator, or client
```

## Deployment Steps

### 1. Deploy to Phala Cloud

1. **Login to Phala Cloud Console**
2. **Create New Application**
3. **Upload docker-compose.yml**
4. **Configure Environment Variables** (encrypted by TEE)
5. **Select CVM Resources**:
   - CPU: 2 cores recommended
   - Memory: 4GB minimum
   - Storage: 10GB

### 2. Verify TEE Attestation

Once deployed, verify TEE attestation:

```python
# Test script to verify attestation
import requests

response = requests.get('http://your-cvm-url:8080/attestation')
quote = response.json()['quote']
print(f"TDX Quote: {quote[:100]}...")
```

### 3. Monitor Deployment

Check deployment status:

```bash
# View container logs
docker logs erc8004-trustless-agent

# Check health
curl http://your-cvm-url:8080/health
```

## Security Considerations

### TEE Socket Mounting

- **Phala OS 0.3.x**: Uses `/var/run/tappd.sock`
- **dstack OS 0.5.x**: Uses `/var/run/dstack.sock`
- Ensure correct socket is mounted for your deployment

### Environment Variable Encryption

Phala Cloud automatically encrypts environment variables using the TEE's KMS. Sensitive data like private keys are only accessible within the TEE.

### Network Security

- CVM runs in isolated network environment
- Only specified ports are exposed
- All traffic is encrypted

## Testing in CVM

### 1. Local Simulation

Test with TEE simulator before deployment:

```bash
# Start simulator
make tee-start

# Run tests
make test-tee
```

### 2. Integration Testing

```bash
# Test agent registration
flox activate -- python tests/integration/test_agents.py

# Test TEE functions
flox activate -- python tests/integration/test_tee_simulator.py
```

## Troubleshooting

### Container Won't Start

1. Check Flox environment is properly containerized
2. Verify socket mounting is correct
3. Check environment variables are set

### TEE Attestation Fails

1. Ensure socket is properly mounted
2. Verify dstack SDK can connect
3. Check TEE simulator logs

### Connection Issues

1. Verify RPC_URL is accessible from CVM
2. Check network policies
3. Ensure ports are properly exposed

## Production Checklist

- [ ] Container image pushed to registry
- [ ] Environment variables configured
- [ ] Contracts deployed to mainnet/testnet
- [ ] TEE attestation tested
- [ ] Health checks configured
- [ ] Monitoring set up
- [ ] Backup strategy defined
- [ ] Security audit completed

## Support

- **Phala Documentation**: [docs.phala.network](https://docs.phala.network)
- **dstack SDK**: [github.com/Dstack-TEE/dstack](https://github.com/Dstack-TEE/dstack)
- **Project Issues**: [GitHub Issues](https://github.com/your-repo/issues)