# ERC-8004 Trustless Agents - Developer Task List

## 🎯 Current Sprint Tasks

### High Priority (Complete First)
- [ ] Set up development environment with Flox
- [ ] Start Anvil blockchain (`make anvil`)
- [ ] Deploy contracts (`make deploy`)
- [ ] Run end-to-end test (`make test-e2e`)
- [ ] Verify TEE mode works (`USE_TEE_AUTH=true ./run_demo.sh`)

### Medium Priority (Core Features)
- [ ] Implement custom market analysis logic
- [ ] Add new validation strategies
- [ ] Extend feedback mechanisms
- [ ] Create custom agent types
- [ ] Add WebSocket real-time updates

### Low Priority (Nice to Have)
- [ ] Add more comprehensive logging
- [ ] Implement agent metrics dashboard
- [ ] Create performance benchmarks
- [ ] Add more test coverage
- [ ] Document API endpoints with examples

## 📋 Setup Checklist

### 1. Initial Setup
- [ ] Install Flox: `curl -fsSL https://downloads.flox.dev/by/flox/sh | sh`
- [ ] Clone repository
- [ ] Run `flox activate` in project directory
- [ ] Copy `.env.example` to `.env`
- [ ] Configure TEE mode if desired (`USE_TEE_AUTH=true`)

### 2. Blockchain Setup
- [ ] Start Anvil: `make anvil` (separate terminal)
- [ ] Deploy contracts: `make deploy`
- [ ] Fund TEE wallets (if using TEE): `make tee-fund`

### 3. Testing
- [ ] Run unit tests: `make test-unit`
- [ ] Run integration tests: `make test-int`
- [ ] Run E2E tests: `make test-e2e`
- [ ] Run full demo: `./run_demo.sh`

### 4. Development
- [ ] Start API server: `python run_api.py`
- [ ] Check API health: `curl http://localhost:8000/health`
- [ ] Test agent endpoints
- [ ] Implement custom features

## 🔧 Common Development Tasks

### Adding a New Agent Type
1. [ ] Create new agent class in `agents/`
2. [ ] Inherit from `ERC8004BaseAgent` or `ERC8004TEEAgent`
3. [ ] Implement required methods
4. [ ] Add tests in `tests/unit/`
5. [ ] Update API endpoints if needed

### Modifying Smart Contracts
1. [ ] Edit contracts in `contracts/src/`
2. [ ] Run `make build` to compile
3. [ ] Run `make deploy` to redeploy
4. [ ] Update agent code if ABI changed
5. [ ] Run tests to verify

### Testing with TEE Mode
1. [ ] Set `USE_TEE_AUTH=true` in `.env`
2. [ ] Ensure TEE simulator is running
3. [ ] Run `make tee-fund` to fund wallets
4. [ ] Test with `USE_TEE_AUTH=true make test`

### API Development
1. [ ] Modify endpoints in `api/main.py`
2. [ ] Update models in `api/models.py`
3. [ ] Test with `python run_api.py`
4. [ ] Update API documentation
5. [ ] Add integration tests

## 🐛 Debugging Tips

### Common Issues
- **Anvil not running**: Start with `make anvil` in separate terminal
- **Contracts not deployed**: Run `make deploy`
- **TEE wallets unfunded**: Run `make tee-fund`
- **Import errors**: Ensure `flox activate` is run
- **Test failures**: Check blockchain state, may need `make reset`

### Useful Commands
```bash
# Reset everything
make reset

# Check TEE status
make tee-status

# View contract addresses
cat deployed_contracts.json

# Watch API logs
tail -f api.log

# Clean build artifacts
make clean
```

## 📚 Key Files to Understand

### Core Agent Logic
- `agents/base_agent.py` - Base agent implementation
- `agents/tee_base_agent.py` - TEE-enabled base agent
- `agents/server_agent.py` - Market analysis agent
- `agents/validator_agent.py` - Validation agent
- `agents/client_agent.py` - Feedback agent

### Smart Contracts
- `contracts/src/IdentityRegistry.sol` - Agent registration
- `contracts/src/ReputationRegistry.sol` - Feedback system
- `contracts/src/ValidationRegistry.sol` - Work validation

### API Layer
- `api/main.py` - FastAPI application
- `api/models.py` - Request/response models
- `api/websocket.py` - WebSocket support

### Configuration
- `.env` - Environment configuration
- `Makefile` - Build and test commands
- `flox.toml` - Flox environment setup

## 🚀 Next Steps

After completing initial setup:
1. Review the architecture in `docs/ARCHITECTURE.md`
2. Try modifying an agent's behavior
3. Add a new API endpoint
4. Write additional tests
5. Experiment with TEE mode features

## 📝 Notes

- Always use `flox activate` before running commands
- TEE mode provides deterministic key generation
- Agents auto-fund when balance < 0.01 ETH
- All interactions are recorded on-chain
- API supports both REST and WebSocket

---
*Last Updated: [Current Date]*
*Version: 1.0.0*