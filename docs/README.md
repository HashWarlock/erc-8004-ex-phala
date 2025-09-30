# Documentation

Complete documentation for ERC-8004 TEE Agents.

---

## Getting Started

**New to the project? Start here:**

1. **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
   - Installation steps
   - First agent setup
   - Basic usage examples

2. **[../README.md](../README.md)** - Project overview
   - Features and capabilities
   - Agent types
   - Architecture

---

## Guides

### Development

- **[CLAUDE.md](CLAUDE.md)** - Development guide for Claude Code
  - Commands (build, test, deploy)
  - Architecture overview
  - Critical dstack SDK patterns
  - Testing strategy

- **[IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md)** - Implementation details
  - Design decisions
  - Technical notes

- **[DSTACK_SDK_CORRECTIONS.md](DSTACK_SDK_CORRECTIONS.md)** - dstack SDK usage patterns
  - Correct API usage
  - Common mistakes to avoid

### Deployment

- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Production deployment
  - TEE environment setup
  - Configuration management
  - Registry interaction
  - Troubleshooting

- **[LOCAL_AGENT_GUIDE.md](LOCAL_AGENT_GUIDE.md)** - Local agent server
  - HTTP API reference
  - Signature verification
  - Testing workflow
  - Client examples

### Features

- **[COMPUTER_CONTROL_GUIDE.md](COMPUTER_CONTROL_GUIDE.md)** - Computer control agent
  - Sandbox integration
  - 8 operation types
  - API reference
  - Python client examples

### Investigation

- **[CONTRACT_INVESTIGATION.md](CONTRACT_INVESTIGATION.md)** - Registry contract analysis
  - Contract investigation
  - ABI verification
  - Access control findings

---

## Reports

Test and deployment reports:

- **[reports/PRODUCTION_TEE_VALIDATION.md](reports/PRODUCTION_TEE_VALIDATION.md)** - Production TEE test results
- **[reports/LOCAL_DEPLOYMENT_RESULTS.md](reports/LOCAL_DEPLOYMENT_RESULTS.md)** - Local deployment tests
- **[reports/READY_FOR_DEPLOYMENT.md](reports/READY_FOR_DEPLOYMENT.md)** - Deployment readiness checklist
- **[reports/REFACTORING_SUMMARY.md](reports/REFACTORING_SUMMARY.md)** - Refactoring changelog

---

## Quick Reference

### Common Tasks

**Start local agent:**
```bash
./deployment/start_local_agent.sh
```

**Run tests:**
```bash
make test                    # All tests
pytest tests/production/     # Production TEE tests
pytest tests/integration/    # Integration tests
```

**Deploy to production:**
```bash
python deployment/deploy_production.py
```

**Check wallet funding:**
```bash
python deployment/check_wallets.py
```

### Key Files

- **Agent Implementation**: [../src/agent/](../src/agent/)
- **Agent Templates**: [../src/templates/](../src/templates/)
- **Deployment Scripts**: [../deployment/](../deployment/)
- **Examples**: [../examples/](../examples/)
- **Tests**: [../tests/](../tests/)

---

## Documentation Structure

```
docs/
├── README.md                          # This file
├── QUICKSTART.md                      # Quick start guide
├── CLAUDE.md                          # Development guide
├── DEPLOYMENT_GUIDE.md                # Production deployment
├── LOCAL_AGENT_GUIDE.md               # Local server guide
├── COMPUTER_CONTROL_GUIDE.md          # Computer control
├── CONTRACT_INVESTIGATION.md          # Contract analysis
├── IMPLEMENTATION_NOTES.md            # Implementation details
├── DSTACK_SDK_CORRECTIONS.md          # dstack patterns
└── reports/                           # Test/deployment reports
    ├── PRODUCTION_TEE_VALIDATION.md
    ├── LOCAL_DEPLOYMENT_RESULTS.md
    ├── READY_FOR_DEPLOYMENT.md
    └── REFACTORING_SUMMARY.md
```

---

## External Resources

- **[ERC-8004 Standard](https://eips.ethereum.org/EIPS/eip-8004)** - Agent protocol specification
- **[Phala Network](https://phala.network)** - TEE infrastructure provider
- **[dstack Docs](https://docs.phala.network/tech-specs/dstack)** - TEE SDK documentation
- **[Base Sepolia](https://sepolia.base.org)** - L2 testnet
- **[aio-sandbox](https://sandbox.agent-infra.com)** - Sandbox API for computer control

---

## Contributing

When adding documentation:

1. **Place correctly:**
   - Guides → `docs/`
   - Reports → `docs/reports/`
   - API reference → Within guides

2. **Link properly:**
   - Use relative paths
   - Update this README
   - Cross-reference related docs

3. **Keep updated:**
   - Update when code changes
   - Add examples
   - Include troubleshooting

4. **Format consistently:**
   - Use markdown headers
   - Include code blocks
   - Add navigation sections

---

## Getting Help

1. **Check documentation** - Start with QUICKSTART.md
2. **Review examples** - See [../examples/](../examples/)
3. **Run tests** - Verify your environment with `make test`
4. **Open issue** - Report bugs or request features on GitHub
