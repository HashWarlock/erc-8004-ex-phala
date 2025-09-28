#!/usr/bin/env python3
"""
Basic 3-Agent Workflow Example

Demonstrates a complete workflow with Server, Validator, and Client agents
interacting through the ERC-8004 protocol.
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
from src.agent.base import AgentConfig, AgentRole, RegistryAddresses
from src.templates.server_agent import ServerAgent
from src.templates.validator_agent import ValidatorAgent
from src.templates.client_agent import ClientAgent


class BasicWorkflowDemo:
    """Orchestrates a basic 3-agent workflow demonstration."""

    def __init__(self):
        """Initialize the demo with configuration."""
        load_dotenv()
        self.setup_complete = False
        self.agents = {}

    async def setup_agents(self):
        """Initialize all three agents with their configurations."""
        print("🚀 Setting up 3-Agent Workflow Demo")
        print("=" * 50)

        # Common registry addresses (Base Sepolia)
        registries = RegistryAddresses(
            identity=os.getenv('IDENTITY_REGISTRY_ADDRESS', '0x000c5A70B7269c5eD4238DcC6576e598614d3f70'),
            reputation=os.getenv('REPUTATION_REGISTRY_ADDRESS', '0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde'),
            validation=os.getenv('VALIDATION_REGISTRY_ADDRESS', '0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d'),
            tee_verifier=os.getenv('TEE_VERIFIER_ADDRESS', '0x1b841e88ba786027f39ecf9Cd160176b22E3603c')
        )

        # Use development mode for demo (no TEE required)
        use_tee = os.getenv('USE_TEE_AUTH', 'false').lower() == 'true'
        rpc_url = os.getenv('RPC_URL', 'https://sepolia.base.org')
        chain_id = int(os.getenv('CHAIN_ID', '84532'))

        # Private keys for demo (use different keys in production!)
        demo_keys = {
            'server': os.getenv('SERVER_PRIVATE_KEY', '0x' + '1' * 64),
            'validator': os.getenv('VALIDATOR_PRIVATE_KEY', '0x' + '2' * 64),
            'client': os.getenv('CLIENT_PRIVATE_KEY', '0x' + '3' * 64)
        }

        # 1. Initialize Server Agent (Alice)
        print("\n📊 Initializing Server Agent (Alice)...")
        server_config = AgentConfig(
            domain="alice.example.com",
            salt="alice-salt-demo",
            role=AgentRole.SERVER,
            rpc_url=rpc_url,
            chain_id=chain_id,
            use_tee_auth=use_tee,
            private_key=demo_keys['server'] if not use_tee else None
        )
        self.agents['server'] = ServerAgent(server_config, registries)
        print(f"✅ Server Agent initialized at domain: {server_config.domain}")

        # 2. Initialize Validator Agent (Bob)
        print("\n🔍 Initializing Validator Agent (Bob)...")
        validator_config = AgentConfig(
            domain="bob.example.com",
            salt="bob-salt-demo",
            role=AgentRole.VALIDATOR,
            rpc_url=rpc_url,
            chain_id=chain_id,
            use_tee_auth=use_tee,
            private_key=demo_keys['validator'] if not use_tee else None
        )
        self.agents['validator'] = ValidatorAgent(validator_config, registries)
        print(f"✅ Validator Agent initialized at domain: {validator_config.domain}")

        # 3. Initialize Client Agent (Charlie)
        print("\n📝 Initializing Client Agent (Charlie)...")
        client_config = AgentConfig(
            domain="charlie.example.com",
            salt="charlie-salt-demo",
            role=AgentRole.CLIENT,
            rpc_url=rpc_url,
            chain_id=chain_id,
            use_tee_auth=use_tee,
            private_key=demo_keys['client'] if not use_tee else None
        )
        self.agents['client'] = ClientAgent(client_config, registries)
        print(f"✅ Client Agent initialized at domain: {client_config.domain}")

        self.setup_complete = True
        print("\n✅ All agents initialized successfully!")

    async def register_agents(self):
        """Register all agents with ERC-8004 (optional for demo)."""
        if os.getenv('SKIP_REGISTRATION', 'true').lower() == 'true':
            print("\n⚠️  Skipping agent registration (demo mode)")
            # Assign mock IDs for demo
            self.agents['server'].agent_id = 1
            self.agents['validator'].agent_id = 2
            self.agents['client'].agent_id = 3
            return

        print("\n📝 Registering agents with ERC-8004...")
        try:
            for name, agent in self.agents.items():
                agent_id = await agent.register()
                print(f"✅ {name.title()} agent registered with ID: {agent_id}")
        except Exception as e:
            print(f"⚠️  Registration failed (continuing in demo mode): {e}")
            # Assign mock IDs
            self.agents['server'].agent_id = 1
            self.agents['validator'].agent_id = 2
            self.agents['client'].agent_id = 3

    async def demonstrate_workflow(self):
        """Run the complete 3-agent workflow demonstration."""
        if not self.setup_complete:
            await self.setup_agents()

        print("\n" + "=" * 50)
        print("🎭 Starting 3-Agent Workflow Demonstration")
        print("=" * 50)

        # Step 1: Client requests market analysis from Server
        print("\n📤 Step 1: Client requests market analysis from Server")
        market_request = {
            'task_id': 'demo_001',
            'query': 'market analysis for cryptocurrency trends',
            'data': {
                'asset': 'ETH',
                'timeframe': '24h',
                'metrics': ['price', 'volume', 'volatility']
            },
            'timestamp': datetime.utcnow().isoformat()
        }

        server_result = await self.agents['server'].process_task(market_request)
        print(f"✅ Server processed request: {server_result['status']}")
        print(f"   Analysis confidence: {server_result.get('confidence', 'N/A')}")

        # Step 2: Server requests validation from Validator
        print("\n🔍 Step 2: Server requests validation from Validator")

        # Create hash of the analysis result
        import hashlib
        result_json = json.dumps(server_result['analysis'], sort_keys=True)
        data_hash = hashlib.sha256(result_json.encode()).hexdigest()

        validation_request = {
            'request_id': 'val_001',
            'data_hash': data_hash,
            'data': server_result['analysis'],
            'validation_type': 'integrity',
            'requester': 'server_agent'
        }

        validator_result = await self.agents['validator'].process_task(validation_request)
        print(f"✅ Validator processed request: {validator_result['status']}")
        print(f"   Validation result: {'Valid' if validator_result.get('is_valid') else 'Invalid'}")
        print(f"   Confidence: {validator_result.get('confidence', 0)}")

        # Step 3: Client submits feedback based on results
        print("\n⭐ Step 3: Client submits feedback for both agents")

        # Feedback for Server
        server_feedback = {
            'task_type': 'feedback',
            'target_agent_id': self.agents['server'].agent_id,
            'rating': 5 if validator_result.get('is_valid') else 3,
            'comment': 'Good analysis with validated results' if validator_result.get('is_valid') else 'Analysis needs improvement',
            'data': {
                'service_type': 'market_analysis',
                'interaction_id': 'demo_001'
            }
        }

        client_feedback_result = await self.agents['client'].process_task(server_feedback)
        print(f"✅ Client submitted feedback for Server: Rating {server_feedback['rating']}/5")

        # Feedback for Validator
        validator_feedback = {
            'task_type': 'feedback',
            'target_agent_id': self.agents['validator'].agent_id,
            'rating': 5,
            'comment': 'Thorough validation service',
            'data': {
                'service_type': 'validation',
                'interaction_id': 'val_001'
            }
        }

        client_feedback_result2 = await self.agents['client'].process_task(validator_feedback)
        print(f"✅ Client submitted feedback for Validator: Rating {validator_feedback['rating']}/5")

        # Step 4: Display workflow summary
        print("\n" + "=" * 50)
        print("📊 Workflow Summary")
        print("=" * 50)

        summary = {
            'workflow_id': 'demo_workflow_001',
            'timestamp': datetime.utcnow().isoformat(),
            'participants': {
                'server': self.agents['server'].config.domain,
                'validator': self.agents['validator'].config.domain,
                'client': self.agents['client'].config.domain
            },
            'steps_completed': [
                'Market analysis requested',
                'Analysis completed by server',
                'Validation performed',
                'Feedback submitted'
            ],
            'results': {
                'analysis_status': server_result['status'],
                'validation_status': validator_result.get('is_valid', False),
                'feedback_submitted': True
            }
        }

        print(json.dumps(summary, indent=2))

        return summary

    async def cleanup(self):
        """Clean up resources."""
        print("\n🧹 Cleaning up...")
        # Any cleanup logic here
        self.agents.clear()
        self.setup_complete = False


async def main():
    """Run the basic workflow demonstration."""
    demo = BasicWorkflowDemo()

    try:
        # Setup agents
        await demo.setup_agents()

        # Register agents (optional)
        await demo.register_agents()

        # Run demonstration
        result = await demo.demonstrate_workflow()

        print("\n✨ Basic workflow demonstration completed successfully!")

    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await demo.cleanup()


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════╗
    ║  ERC-8004 TEE Agents - Basic Workflow   ║
    ║                                          ║
    ║  Server → Validator → Client Demo       ║
    ╚══════════════════════════════════════════╝
    """)

    asyncio.run(main())