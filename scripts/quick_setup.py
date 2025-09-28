#!/usr/bin/env python3
"""
ERC-8004 TEE Agent Quick Setup

One-command setup for new builders.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def setup_agent_project():
    """Interactive setup for new agent project."""

    print("🤖 ERC-8004 TEE Agent Quick Setup")
    print("=" * 40)

    # Collect user preferences
    agent_type = input("Agent type (server/validator/client/custom) [server]: ").strip().lower()
    if agent_type not in ['server', 'validator', 'client', 'custom']:
        agent_type = 'server'

    agent_name = input(f"Agent name [my-{agent_type}-agent]: ").strip()
    if not agent_name:
        agent_name = f"my-{agent_type}-agent"

    domain = input("Agent domain (e.g., myagent.com) [localhost]: ").strip()
    if not domain:
        domain = "localhost"

    use_ai = input("Enable AI capabilities? (y/N): ").strip().lower() == 'y'
    use_tee = input("Use TEE authentication? (Y/n): ").strip().lower() != 'n'

    print(f"\n📦 Setting up {agent_name}...")

    # Create project directory
    project_dir = Path(agent_name)
    project_dir.mkdir(exist_ok=True)
    os.chdir(project_dir)

    # Install dependencies
    print("📥 Installing dependencies...")
    install_deps(use_ai)

    # Generate environment file
    create_env_file(domain, use_tee)

    # Generate agent implementation
    create_agent_file(agent_type, agent_name, use_ai)

    # Generate deployment script
    create_deployment_script(agent_name, agent_type)

    # Generate test file
    create_test_file(agent_name, agent_type)

    # Generate README
    create_readme(agent_name, agent_type, domain)

    # Generate requirements.txt for the project
    create_requirements_file(use_ai)

    print(f"✅ Setup complete!")
    print(f"""
Next steps:
1. cd {agent_name}
2. Edit .env with your configuration
3. Run: python deploy.py
4. Your agent will be registered and ready!

Documentation: https://github.com/your-org/erc-8004-tee-agents
""")


def install_deps(use_ai: bool):
    """Install required dependencies."""
    try:
        # Install base package
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "erc-8004-tee-agents"
        ], check=False, capture_output=True)

        # Install additional packages
        packages = [
            "web3>=6.0.0",
            "eth-account>=0.8.0",
            "python-dotenv>=1.0.0",
            "aiohttp>=3.8.0"
        ]

        if use_ai:
            packages.extend([
                "openai>=1.0.0",
                "anthropic>=0.3.0",
                "crewai>=0.1.0"
            ])

        for package in packages:
            subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], check=False, capture_output=True)

    except Exception as e:
        print(f"⚠️  Some dependencies may need manual installation: {e}")


def create_env_file(domain: str, use_tee: bool):
    """Create .env file with defaults."""

    import secrets
    salt = secrets.token_hex(16)

    env_content = f"""# {domain} Agent Configuration

# Network (Base Sepolia - ready to use!)
RPC_URL=https://sepolia.base.org
CHAIN_ID=84532

# ERC-8004 Registries (Pre-deployed on Base Sepolia)
IDENTITY_REGISTRY_ADDRESS=0x000c5A70B7269c5eD4238DcC6576e598614d3f70
REPUTATION_REGISTRY_ADDRESS=0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde
VALIDATION_REGISTRY_ADDRESS=0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d
TEE_VERIFIER_ADDRESS=0x1b841e88ba786027f39ecf9Cd160176b22E3603c

# Your Agent Configuration
AGENT_DOMAIN={domain}
AGENT_SALT={salt}

# TEE Settings
USE_TEE_AUTH={str(use_tee).lower()}
PHALA_ENDPOINT=https://api.phala.network
DSTACK_SIMULATOR_ENDPOINT=http://localhost:8090

# For testing (remove in production)
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
DEBUG=true

# Optional: AI Services
# OPENAI_API_KEY=your-openai-key-here
# ANTHROPIC_API_KEY=your-anthropic-key-here
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    print("✅ Created .env file")


def create_agent_file(agent_type: str, agent_name: str, use_ai: bool):
    """Create the main agent implementation file."""

    class_name = agent_name.replace('-', '').replace('_', '').title() + 'Agent'

    ai_import = """
from crewai import Agent, Task, Crew
import openai""" if use_ai else ""

    ai_setup = """
        # Setup AI capabilities
        self.setup_ai_agent()""" if use_ai else ""

    ai_methods = """
    def setup_ai_agent(self):
        \"\"\"Setup AI-powered analysis.\"\"\"
        self.ai_agent = Agent(
            role='analyst',
            goal='Provide intelligent analysis',
            backstory='Expert AI analyst'
        )
        print("🧠 AI capabilities enabled")

    async def ai_enhance(self, data):
        \"\"\"Enhance results with AI.\"\"\"
        # AI enhancement logic
        return data""" if use_ai else ""

    template = f"""#!/usr/bin/env python3
\"\"\"
{agent_name} - ERC-8004 TEE Agent Implementation
\"\"\"

import asyncio
from datetime import datetime
from erc8004_tee_agents import AgentConfig, AgentRole, RegistryAddresses
from erc8004_tee_agents.templates import {agent_type.title()}Agent
from dotenv import load_dotenv
import os{ai_import}

load_dotenv()


class {class_name}({agent_type.title()}Agent):
    \"\"\"Custom {agent_type} agent implementation.\"\"\"

    def __init__(self, config, registries):
        super().__init__(config, registries)
        print(f"🚀 {{agent_name}} initialized"){ai_setup}

    async def process_task(self, task_data):
        \"\"\"Process incoming tasks with custom logic.\"\"\"
        # Call parent implementation
        result = await super().process_task(task_data)

        # Add custom processing here
        result['custom_field'] = 'Custom processing applied'
        result['agent_name'] = '{agent_name}'

        return result{ai_methods}


async def main():
    \"\"\"Initialize and run the agent.\"\"\"

    # Load configuration from environment
    config = AgentConfig(
        domain=os.getenv('AGENT_DOMAIN', 'localhost'),
        salt=os.getenv('AGENT_SALT', 'default-salt'),
        role=AgentRole.{agent_type.upper()},
        rpc_url=os.getenv('RPC_URL', 'https://sepolia.base.org'),
        chain_id=int(os.getenv('CHAIN_ID', '84532')),
        use_tee_auth=os.getenv('USE_TEE_AUTH', 'true').lower() == 'true',
        private_key=os.getenv('PRIVATE_KEY') if os.getenv('DEBUG') == 'true' else None
    )

    # Set registry addresses
    registries = RegistryAddresses(
        identity=os.getenv('IDENTITY_REGISTRY_ADDRESS'),
        reputation=os.getenv('REPUTATION_REGISTRY_ADDRESS'),
        validation=os.getenv('VALIDATION_REGISTRY_ADDRESS'),
        tee_verifier=os.getenv('TEE_VERIFIER_ADDRESS')
    )

    # Create agent
    agent = {class_name}(config, registries)

    # Register agent
    print("📝 Registering agent...")
    agent_id = await agent.register()
    print(f"✅ Agent registered with ID: {{agent_id}}")

    # Get attestation
    attestation = await agent.get_attestation()
    print(f"🔐 TEE Attestation: {{attestation.get('quote', 'N/A')[:50]}}...")

    # Process a test task
    test_task = {{
        'task_id': 'test_001',
        'query': 'Test query',
        'data': {{'test': 'data'}}
    }}

    result = await agent.process_task(test_task)
    print(f"📊 Task result: {{result}}")

    print("\\n🎉 Agent is ready!")
    return agent


if __name__ == "__main__":
    asyncio.run(main())
"""

    filename = f"{agent_name.replace('-', '_')}.py"
    with open(filename, 'w') as f:
        f.write(template)

    # Make executable
    os.chmod(filename, 0o755)

    print(f"✅ Created {filename}")


def create_deployment_script(agent_name: str, agent_type: str):
    """Create deployment script."""

    module_name = agent_name.replace('-', '_')

    content = f"""#!/usr/bin/env python3
\"\"\"
Deploy {agent_name} to Phala Cloud and register with ERC-8004
\"\"\"

import asyncio
import os
from dotenv import load_dotenv
from {module_name} import main

async def deploy():
    \"\"\"Deploy and register the agent.\"\"\"
    load_dotenv()

    print("🚀 Deploying {agent_name}...")

    try:
        agent = await main()
        print(f"✅ Deployment successful!")
        print(f"Agent ID: {{agent.agent_id}}")
        print(f"Domain: {{agent.config.domain}}")
        print(f"Status: {{agent.get_status()}}")

    except Exception as e:
        print(f"❌ Deployment failed: {{e}}")
        raise

if __name__ == "__main__":
    asyncio.run(deploy())
"""

    with open('deploy.py', 'w') as f:
        f.write(content)

    os.chmod('deploy.py', 0o755)
    print("✅ Created deploy.py")


def create_test_file(agent_name: str, agent_type: str):
    """Create test file for the agent."""

    module_name = agent_name.replace('-', '_')

    content = f"""#!/usr/bin/env python3
\"\"\"
Tests for {agent_name}
\"\"\"

import asyncio
import pytest
from {module_name} import {agent_name.replace('-', '').replace('_', '').title()}Agent
from erc8004_tee_agents import AgentConfig, AgentRole, RegistryAddresses

@pytest.mark.asyncio
async def test_agent_creation():
    \"\"\"Test agent creation.\"\"\"
    config = AgentConfig(
        domain="test.local",
        salt="test-salt",
        role=AgentRole.{agent_type.upper()},
        rpc_url="http://localhost:8545",
        chain_id=31337,
        use_tee_auth=False,
        private_key="0x" + "1" * 64
    )

    registries = RegistryAddresses(
        identity="0x" + "0" * 40,
        reputation="0x" + "1" * 40,
        validation="0x" + "2" * 40,
        tee_verifier="0x" + "3" * 40
    )

    agent = {agent_name.replace('-', '').replace('_', '').title()}Agent(config, registries)
    assert agent is not None
    assert agent.config.domain == "test.local"

@pytest.mark.asyncio
async def test_task_processing():
    \"\"\"Test task processing.\"\"\"
    # Add your test logic here
    pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""

    with open(f'test_{module_name}.py', 'w') as f:
        f.write(content)

    print(f"✅ Created test_{module_name}.py")


def create_readme(agent_name: str, agent_type: str, domain: str):
    """Create project README."""

    content = f"""# {agent_name}

ERC-8004 TEE {agent_type.title()} Agent

## Quick Start

1. **Configure**: Edit `.env` with your settings
2. **Deploy**: `python deploy.py`
3. **Test**: `python test_{agent_name.replace('-', '_')}.py`

## What This Does

- ✅ Registers as ERC-8004 {agent_type} agent
- ✅ TEE-secured key derivation
- ✅ Blockchain attestation
- ✅ Ready for trustless interactions

## Configuration

Edit `.env` file:
- `AGENT_DOMAIN`: Your agent's domain ({domain})
- `AGENT_SALT`: Unique salt for key derivation
- `USE_TEE_AUTH`: Enable/disable TEE mode
- `PRIVATE_KEY`: Fallback key for testing

## Architecture

```
Your Agent ({agent_name})
    ↓
TEE Security (Phala Cloud)
    ↓
ERC-8004 Registry (Base Sepolia)
    ↓
Trustless Network
```

## Testing

Run tests:
```bash
python test_{agent_name.replace('-', '_')}.py
```

Run agent locally:
```bash
python {agent_name.replace('-', '_')}.py
```

## Deployment

Deploy to Phala Cloud:
```bash
python deploy.py
```

## Documentation

- [ERC-8004 Standard](https://eips.ethereum.org/EIPS/eip-8004)
- [TEE Agents SDK](https://github.com/your-org/erc-8004-tee-agents)
- [Phala Cloud](https://phala.network)

## Support

- Discord: [ERC-8004 Community](https://discord.gg/erc8004)
- Issues: [GitHub Issues](https://github.com/your-org/erc-8004-tee-agents/issues)
"""

    with open('README.md', 'w') as f:
        f.write(content)

    print("✅ Created README.md")


def create_requirements_file(use_ai: bool):
    """Create requirements.txt for the project."""

    requirements = [
        "erc-8004-tee-agents>=0.1.0",
        "web3>=6.0.0",
        "eth-account>=0.8.0",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.8.0",
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0"
    ]

    if use_ai:
        requirements.extend([
            "openai>=1.0.0",
            "anthropic>=0.3.0",
            "crewai>=0.1.0"
        ])

    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(requirements))

    print("✅ Created requirements.txt")


def main():
    """Main entry point."""
    try:
        setup_agent_project()
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()