# Development Setup Guide

## Prerequisites

- macOS, Linux, or WSL2 on Windows
- Git
- Flox package manager
- Docker Desktop (optional)

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd erc-8004-ex-phala

# Activate Flox environment
flox activate

# Install dependencies
make install

# Start development environment (run in separate terminals)
make anvil        # Terminal 1: blockchain
make tee-start    # Terminal 2: TEE simulator  
make deploy       # Terminal 3: deploy contracts
```

## Detailed Setup

### 1. Install Flox

```bash
# macOS
brew install flox

# Linux
curl -L https://flox.dev/install | sh

# Verify installation
flox --version
```

### 2. Project Initialization

```bash
# Activate the Flox environment
flox activate

# This provides:
# - Python 3.10+
# - Node.js 18+
# - Foundry (forge, cast, anvil)
# - dstack SDK
# - All Python packages
```

### 3. Environment Configuration

Create `.env` file from example:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```bash
# Development blockchain
RPC_URL=http://127.0.0.1:8545
CHAIN_ID=31337

# Development accounts (DO NOT use in production)
SERVER_AGENT_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
VALIDATOR_AGENT_KEY=0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d
CLIENT_AGENT_KEY=0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a

# API Configuration  
API_TOKEN=test-token-123
API_PORT=8000

# TEE Configuration
DSTACK_SIMULATOR_ENDPOINT=.dstack/sdk/simulator/dstack.sock
DEVELOPMENT_MODE=true

# Optional: AI/ML
OPENAI_API_KEY=your-key-here
```

### 4. Start Local Blockchain

```bash
# Start Anvil (local Ethereum)
make anvil

# In another terminal, verify connection
cast block-number --rpc-url http://127.0.0.1:8545
```

### 5. Deploy Smart Contracts

```bash
# Deploy all contracts
make deploy

# Verify deployment
cat deployed_contracts.json
```

### 6. Start TEE Simulator

```bash
# Start dstack simulator
make tee-start

# Verify TEE is running
make tee-status
```

### 7. Start API Server

```bash
# Start the API
make api-start

# Or for development with auto-reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Verify Setup

```bash
# Check all services
make status

# Run tests
make test
```

## Development Workflow

### Code Structure

```
erc-8004-ex-phala/
├── agents/          # Agent implementations
│   ├── base_agent.py
│   ├── server_agent.py
│   ├── validator_agent.py
│   └── client_agent.py
├── api/            # FastAPI application
│   ├── main.py
│   ├── routes/
│   └── models.py
├── contracts/      # Solidity smart contracts
│   ├── src/
│   └── script/
├── tests/          # Test suites
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── docs/          # Documentation
```

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make changes and test**
   ```bash
   # Run tests after changes
   make test
   
   # Run specific tests
   pytest tests/unit/test_your_feature.py
   ```

3. **Format code**
   ```bash
   # Format Python code
   flox activate -- ruff format .
   
   # Check for issues
   flox activate -- ruff check .
   ```

4. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

### Adding New Agents

1. Create new agent class:
```python
# agents/custom_agent.py
from agents.base_agent import ERC8004BaseAgent

class CustomAgent(ERC8004BaseAgent):
    def __init__(self, agent_domain: str, private_key: str):
        super().__init__(agent_domain, private_key)
    
    def custom_method(self):
        # Your implementation
        pass
```

2. Add tests:
```python
# tests/unit/test_custom_agent.py
def test_custom_agent():
    agent = CustomAgent("custom.local", TEST_KEY)
    assert agent.custom_method() == expected
```

3. Add API endpoint:
```python
# api/routes/custom.py
@router.post("/custom/action")
async def custom_action():
    # Your endpoint
    pass
```

### Working with Smart Contracts

1. **Modify contracts**
   ```solidity
   // contracts/src/YourContract.sol
   ```

2. **Compile**
   ```bash
   forge build
   ```

3. **Test**
   ```bash
   forge test
   ```

4. **Deploy**
   ```bash
   forge script contracts/script/Deploy.s.sol --broadcast
   ```

## Common Development Tasks

### Running Specific Tests

```bash
# Unit tests only
pytest tests/unit/

# With coverage
pytest --cov=agents --cov-report=html

# Specific test
pytest tests/unit/test_base_agent.py::test_initialization
```

### Debugging

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Run with debugging
pytest -s tests/your_test.py
```

### Viewing Logs

```bash
# API logs
tail -f api.log

# Contract logs
cast logs --rpc-url http://127.0.0.1:8545

# Docker logs (if using Docker)
docker-compose logs -f
```

### Database Reset

```bash
# Stop and restart Anvil blockchain
# (Stop with Ctrl+C in the anvil terminal, then)
make anvil

# Redeploy contracts
make deploy
```

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Solidity
- Prettier
- GitLens

Settings (`.vscode/settings.json`):
```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "solidity.compileUsingRemoteVersion": "0.8.19"
}
```

### PyCharm

1. Set Python interpreter to Flox environment
2. Configure pytest as test runner
3. Add environment variables from `.env`

## Cleanup Commands

### Regular Cleanup
```bash
# Clean build artifacts and cache (preserves deployed contracts)
make clean
```

### Deep Cleanup
```bash
# Remove everything including deployed contracts
make clean-all
```

### Full Reset
```bash
# Reset to completely fresh state
make reset

# This will:
# - Clean all artifacts
# - Remove deployed contracts
# - Delete .env and recreate from .env.example
# - Show next steps to get started again
```

## Troubleshooting

### Common Issues

1. **Flox not found**
   ```bash
   # Reload shell
   source ~/.bashrc
   # or
   source ~/.zshrc
   ```

2. **Port already in use**
   ```bash
   # Find process using port
   lsof -i :8545
   # Kill process
   kill -9 <PID>
   ```

3. **Contract deployment fails**
   ```bash
   # Ensure Anvil is running
   make anvil
   
   # Check account balance
   cast balance 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
   ```

4. **Import errors**
   ```bash
   # Ensure in Flox environment
   flox activate
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

## Performance Tips

1. **Use pytest-xdist for parallel tests**
   ```bash
   pytest -n auto
   ```

2. **Cache contract compilations**
   ```bash
   export FOUNDRY_CACHE=true
   ```

3. **Use local IPFS for testing**
   ```bash
   ipfs daemon --offline
   ```

## Next Steps

- Read [Architecture Guide](ARCHITECTURE.md)
- Review [API Reference](API_REFERENCE.md)
- See [Testing Guide](TESTING.md)
- Check [Contributing Guidelines](CONTRIBUTING.md)