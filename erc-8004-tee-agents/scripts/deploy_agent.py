#!/usr/bin/env python3
"""
Deploy Agent to Phala Cloud

One-click deployment script for TEE agents.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.agent.base import AgentConfig, AgentRole, RegistryAddresses, create_agent


async def deploy_agent():
    """Deploy agent to Phala Cloud and register with ERC-8004."""

    print("🚀 ERC-8004 TEE Agent Deployment")
    print("=" * 40)

    # Load environment
    load_dotenv()

    # Get agent type from user or environment
    agent_type = os.getenv('AGENT_TYPE')
    if not agent_type:
        agent_type = input("Agent type (server/validator/client/custom): ").strip().lower()
        if agent_type not in ['server', 'validator', 'client', 'custom']:
            print("❌ Invalid agent type")
            return False

    print(f"\n📋 Deploying {agent_type} agent...")

    # Load configuration
    config = load_agent_config()
    registries = load_registry_addresses()

    print(f"🔗 Network: {config.rpc_url}")
    print(f"🌐 Domain: {config.domain}")
    print(f"🔐 TEE Mode: {'Enabled' if config.use_tee_auth else 'Disabled (Dev Mode)'}")

    # Create agent instance
    try:
        agent = create_agent(agent_type, config, registries)
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        return False

    # Register agent with ERC-8004
    print("\n📝 Registering with ERC-8004...")
    try:
        agent_id = await agent.register()
        print(f"✅ Agent registered with ID: {agent_id}")
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return False

    # Get TEE attestation
    print("\n🔐 Getting TEE attestation...")
    try:
        attestation = await agent.get_attestation()
        if attestation.get('error'):
            print(f"⚠️  Attestation degraded: {attestation['error']}")
        else:
            quote = attestation.get('quote', 'N/A')
            if quote and quote != 'N/A':
                print(f"✅ Attestation received: {quote[:50]}...")
            else:
                print("ℹ️  Running in development mode (no TEE attestation)")
    except Exception as e:
        print(f"⚠️  Attestation failed: {e}")

    # Deploy to Phala Cloud (if configured)
    if config.use_tee_auth and os.getenv('PHALA_DEPLOY', 'false').lower() == 'true':
        print("\n☁️  Deploying to Phala Cloud...")
        success = await deploy_to_phala(agent, config)
        if not success:
            print("⚠️  Phala deployment skipped, agent registered locally")

    # Save deployment info
    save_deployment_info(agent, config)

    # Display summary
    print("\n" + "=" * 40)
    print("🎉 Deployment Complete!")
    print("=" * 40)
    print(f"Agent Type: {agent_type}")
    print(f"Agent ID: {agent_id}")
    print(f"Domain: {config.domain}")
    print(f"Address: {await agent._get_agent_address()}")
    print(f"Status: {agent.get_status()}")

    return True


def load_agent_config() -> AgentConfig:
    """Load agent configuration from environment."""

    # Determine role from agent type or default
    role_map = {
        'server': AgentRole.SERVER,
        'validator': AgentRole.VALIDATOR,
        'client': AgentRole.CLIENT,
        'custom': AgentRole.CUSTOM
    }

    agent_type = os.getenv('AGENT_TYPE', 'server').lower()
    role = role_map.get(agent_type, AgentRole.CUSTOM)

    return AgentConfig(
        domain=os.getenv('AGENT_DOMAIN', 'localhost'),
        salt=os.getenv('AGENT_SALT', 'default-salt'),
        role=role,
        rpc_url=os.getenv('RPC_URL', 'https://sepolia.base.org'),
        chain_id=int(os.getenv('CHAIN_ID', '84532')),
        use_tee_auth=os.getenv('USE_TEE_AUTH', 'true').lower() == 'true',
        tee_endpoint=os.getenv('DSTACK_SIMULATOR_ENDPOINT') or os.getenv('PHALA_ENDPOINT'),
        private_key=os.getenv('PRIVATE_KEY') if os.getenv('DEBUG', 'false').lower() == 'true' else None
    )


def load_registry_addresses() -> RegistryAddresses:
    """Load registry addresses from environment."""

    return RegistryAddresses(
        identity=os.getenv('IDENTITY_REGISTRY_ADDRESS', '0x000c5A70B7269c5eD4238DcC6576e598614d3f70'),
        reputation=os.getenv('REPUTATION_REGISTRY_ADDRESS', '0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde'),
        validation=os.getenv('VALIDATION_REGISTRY_ADDRESS', '0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d'),
        tee_verifier=os.getenv('TEE_VERIFIER_ADDRESS', '0x1b841e88ba786027f39ecf9Cd160176b22E3603c')
    )


async def deploy_to_phala(agent: Any, config: AgentConfig) -> bool:
    """
    Deploy agent to Phala Cloud.

    Args:
        agent: Agent instance
        config: Agent configuration

    Returns:
        Success status
    """
    try:
        # This would include:
        # 1. Package agent code
        # 2. Upload to Phala Cloud
        # 3. Configure CVM instance
        # 4. Start agent service

        print("📦 Packaging agent code...")
        # Package logic here

        print("📤 Uploading to Phala Cloud...")
        # Upload logic here

        print("⚙️  Configuring CVM...")
        # CVM configuration here

        print("▶️  Starting agent service...")
        # Service start logic here

        # For now, this is a placeholder
        print("ℹ️  Phala deployment requires additional setup")
        return False

    except Exception as e:
        print(f"❌ Phala deployment failed: {e}")
        return False


def save_deployment_info(agent: Any, config: AgentConfig):
    """Save deployment information to file."""

    deployment_info = {
        'agent_id': agent.agent_id,
        'domain': config.domain,
        'role': config.role.value,
        'network': {
            'rpc_url': config.rpc_url,
            'chain_id': config.chain_id
        },
        'registries': {
            'identity': agent.registries.identity,
            'reputation': agent.registries.reputation,
            'validation': agent.registries.validation,
            'tee_verifier': agent.registries.tee_verifier
        },
        'tee_enabled': config.use_tee_auth,
        'status': agent.get_status()
    }

    # Save to file
    deployment_file = Path('.agent_deployment.json')
    with open(deployment_file, 'w') as f:
        json.dump(deployment_info, f, indent=2)

    print(f"\n📄 Deployment info saved to {deployment_file}")


async def main():
    """Main entry point."""
    try:
        success = await deploy_agent()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Deployment cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())