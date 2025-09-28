#!/usr/bin/env python3
"""
Register Agent with ERC-8004

Standalone agent registration script.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.agent.base import AgentConfig, AgentRole, RegistryAddresses, create_agent


async def register_agent():
    """Register an existing agent with ERC-8004 registries."""

    print("📝 ERC-8004 Agent Registration")
    print("=" * 40)

    # Load environment
    load_dotenv()

    # Check if agent already deployed
    deployment_file = Path('.agent_deployment.json')
    if deployment_file.exists():
        with open(deployment_file, 'r') as f:
            existing = json.load(f)
            if existing.get('agent_id'):
                print(f"ℹ️  Agent already registered with ID: {existing['agent_id']}")
                update = input("Re-register agent? (y/N): ").strip().lower()
                if update != 'y':
                    return

    # Get agent type
    agent_type = os.getenv('AGENT_TYPE', 'server').lower()
    print(f"Agent type: {agent_type}")

    # Load configuration
    config = AgentConfig(
        domain=os.getenv('AGENT_DOMAIN', 'localhost'),
        salt=os.getenv('AGENT_SALT', 'default-salt'),
        role=AgentRole[agent_type.upper()],
        rpc_url=os.getenv('RPC_URL', 'https://sepolia.base.org'),
        chain_id=int(os.getenv('CHAIN_ID', '84532')),
        use_tee_auth=os.getenv('USE_TEE_AUTH', 'true').lower() == 'true',
        private_key=os.getenv('PRIVATE_KEY') if os.getenv('DEBUG') == 'true' else None
    )

    registries = RegistryAddresses(
        identity=os.getenv('IDENTITY_REGISTRY_ADDRESS', '0x000c5A70B7269c5eD4238DcC6576e598614d3f70'),
        reputation=os.getenv('REPUTATION_REGISTRY_ADDRESS', '0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde'),
        validation=os.getenv('VALIDATION_REGISTRY_ADDRESS', '0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d'),
        tee_verifier=os.getenv('TEE_VERIFIER_ADDRESS', '0x1b841e88ba786027f39ecf9Cd160176b22E3603c')
    )

    # Create agent
    agent = create_agent(agent_type, config, registries)

    print(f"\nRegistering {agent_type} agent...")
    print(f"Domain: {config.domain}")
    print(f"Network: Base Sepolia")

    try:
        # Register agent
        agent_id = await agent.register()
        print(f"✅ Successfully registered with ID: {agent_id}")

        # Get agent info
        agent_info = await agent.get_agent_info()
        print(f"\n📋 Agent Information:")
        print(f"  - ID: {agent_id}")
        print(f"  - Domain: {agent_info.get('domain')}")
        print(f"  - Address: {agent_info.get('address')}")
        print(f"  - Active: {agent_info.get('isActive')}")

        # Save registration info
        registration_info = {
            'agent_id': agent_id,
            'domain': config.domain,
            'role': config.role.value,
            'address': await agent._get_agent_address(),
            'registries': {
                'identity': registries.identity,
                'reputation': registries.reputation,
                'validation': registries.validation
            }
        }

        with open('.agent_registration.json', 'w') as f:
            json.dump(registration_info, f, indent=2)

        print(f"\n📄 Registration info saved to .agent_registration.json")

    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return False

    return True


if __name__ == "__main__":
    asyncio.run(register_agent())