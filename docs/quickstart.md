# Quick Start Guide

Get your first TEE agent deployed in under 5 minutes! 🚀

## Prerequisites

- Python 3.8 or higher
- Node.js (for blockchain interactions)
- Git

## Installation

### 1. Clone and Install (30 seconds)

```bash
# Clone the repository
git clone https://github.com/your-org/erc-8004-tee-agents
cd erc-8004-tee-agents

# Install the SDK
pip install -e .
```

### 2. Quick Setup (2 minutes)

Run the interactive setup wizard:

```bash
python scripts/quick_setup.py
```

Follow the prompts:
1. Choose your agent type (server/validator/client)
2. Enter agent name and domain
3. Select deployment mode (development/production)
4. Choose AI capabilities (optional)

This creates your project with:
- ✅ Configured agent code
- ✅ Environment settings
- ✅ Deployment scripts
- ✅ Example workflows

### 3. Test Locally (1 minute)

```bash
# Run your agent locally
cd my-agent-project
python run.py
```

Your agent is now running! Try the example workflows in the console output.

### 4. Deploy to Production (1 minute)

```bash
# Deploy to Phala Cloud
python deploy.py
```

Your agent is now:
- ✅ Running in a TEE environment
- ✅ Registered with ERC-8004
- ✅ Ready to receive tasks

## Your First Agent in 50 Lines

Here's a complete working agent:

```python
#!/usr/bin/env python3
"""My First TEE Agent"""

import asyncio
from src.agent.base import AgentConfig, AgentRole
from src.templates.server_agent import ServerAgent

class MyAgent(ServerAgent):
    """A simple market analysis agent."""

    async def process_task(self, task_data):
        """Process incoming tasks."""
        # Your custom logic here
        query = task_data.get('query', '')

        # Perform analysis
        analysis = {
            'query': query,
            'result': f'Analysis for {query}',
            'confidence': 0.95
        }

        return {
            'status': 'completed',
            'analysis': analysis,
            'confidence': analysis['confidence']
        }

async def main():
    """Run the agent."""
    # Configuration
    config = AgentConfig(
        domain="my-agent.example.com",
        salt="my-unique-salt",
        role=AgentRole.SERVER,
        rpc_url="https://sepolia.base.org",
        chain_id=84532
    )

    # Create and run agent
    agent = MyAgent(config, registries=None)

    # Process a test task
    result = await agent.process_task({
        'query': 'ETH price analysis',
        'data': {'timeframe': '24h'}
    })

    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Development Mode

For quick testing without blockchain or TEE:

```bash
# Set development mode in .env
USE_TEE_AUTH=false
SKIP_REGISTRATION=true

# Run with test keys
python run.py
```

## Production Mode

For real deployment with TEE and blockchain:

```bash
# Set production mode in .env
USE_TEE_AUTH=true
SKIP_REGISTRATION=false

# Deploy to Phala Cloud
python scripts/deploy_agent.py
```

## Common Commands

```bash
# Setup new project
python scripts/quick_setup.py

# Run locally
python run.py

# Deploy to production
python deploy.py

# Run tests
pytest tests/

# View examples
cd examples/basic_workflow && python run.py
```

## Next Steps

### Try the Examples

1. **Basic Workflow** - Standard 3-agent interaction
   ```bash
   cd examples/basic_workflow
   python run.py
   ```

2. **AI-Enhanced** - Agents with AI capabilities
   ```bash
   cd examples/ai_enhanced
   python run.py
   ```

3. **Custom Validation** - Domain-specific logic
   ```bash
   cd examples/custom_validation
   python run.py
   ```

### Customize Your Agent

1. **Add Custom Logic**
   - Override `process_task()` method
   - Add validation rules
   - Integrate external APIs

2. **Enable AI Features**
   - Add OpenAI/Anthropic API keys
   - Use AI plugins
   - Create intelligent workflows

3. **Deploy to Mainnet**
   - Update contract addresses
   - Configure mainnet RPC
   - Deploy with real TEE

## Configuration

### Essential Settings

```env
# Network
RPC_URL=https://sepolia.base.org
CHAIN_ID=84532

# Mode
USE_TEE_AUTH=false  # true for production
SKIP_REGISTRATION=true  # false for production

# Contracts (Base Sepolia)
IDENTITY_REGISTRY_ADDRESS=0x000c5A70B7269c5eD4238DcC6576e598614d3f70
REPUTATION_REGISTRY_ADDRESS=0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde
VALIDATION_REGISTRY_ADDRESS=0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d
TEE_VERIFIER_ADDRESS=0x1b841e88ba786027f39ecf9Cd160176b22E3603c
```

### Optional AI Configuration

```env
# AI Providers (choose one or more)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

## Troubleshooting

### Import Errors
```bash
# Reinstall in development mode
pip install -e .
```

### Network Issues
```bash
# Check RPC connectivity
curl https://sepolia.base.org
```

### TEE Simulator
```bash
# Run local TEE simulator for testing
docker run -p 8090:8090 phalanetwork/tee-simulator
```

## Getting Help

- 📖 [API Reference](api_reference.md)
- 🚀 [Deployment Guide](deployment_guide.md)
- 💡 [Examples](../examples/README.md)
- ❓ [FAQ](faq.md)
- 🐛 [Issue Tracker](https://github.com/your-org/erc-8004-tee-agents/issues)

## Success! 🎉

You now have:
- ✅ A working TEE agent
- ✅ Local testing environment
- ✅ Production deployment ready
- ✅ Examples to build upon

**Total time: < 5 minutes!**

Ready to build trustless, autonomous agents? Let's go! 🚀