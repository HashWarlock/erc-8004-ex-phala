#!/usr/bin/env python3
"""
Simple Working Agent Example

A minimal, production-ready agent that demonstrates:
- TEE key derivation
- Real attestation generation
- Task processing
- Status reporting

This agent runs locally and can be extended for production use.
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

from src.agent.base import BaseAgent, AgentConfig, AgentRole, RegistryAddresses


class SimpleWorkingAgent(BaseAgent):
    """
    Simple working agent implementation.
    Extends BaseAgent with minimal task processing logic.
    """

    def __init__(self, config: AgentConfig, registries: RegistryAddresses):
        """Initialize the simple agent."""
        super().__init__(config, registries)
        self.task_count = 0
        print("✨ Simple Working Agent initialized")

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming tasks.

        Args:
            task_data: Task information

        Returns:
            Processing result
        """
        self.task_count += 1

        task_id = task_data.get("task_id", "unknown")
        task_type = task_data.get("type", "generic")
        query = task_data.get("query", "")

        print(f"\n📝 Processing Task #{self.task_count}")
        print(f"   ID: {task_id}")
        print(f"   Type: {task_type}")
        print(f"   Query: {query[:50]}...")

        # Simulate processing
        await asyncio.sleep(0.5)

        # Generate result
        result = {
            "task_id": task_id,
            "status": "completed",
            "processed_at": datetime.now().isoformat(),
            "agent_address": self.address if hasattr(self, 'address') else await self._get_agent_address(),
            "result": f"Processed: {query}",
            "tee_secured": self.config.use_tee_auth
        }

        print(f"   ✅ Task completed")

        return result

    async def _create_agent_card(self) -> Dict[str, Any]:
        """
        Create agent card with capabilities.

        Returns:
            Agent card dictionary
        """
        return {
            "name": "Simple Working Agent",
            "version": "1.0.0",
            "role": self.config.role.value,
            "capabilities": [
                "task_processing",
                "tee_secured_operations",
                "status_reporting"
            ],
            "endpoints": {
                "status": "/status",
                "process": "/process"
            },
            "tee_enabled": self.config.use_tee_auth,
            "created_at": datetime.now().isoformat()
        }


async def main():
    """Run simple agent example."""
    print("\n" + "="*70)
    print("🚀 SIMPLE WORKING AGENT EXAMPLE")
    print("   Production-ready minimal agent with TEE support")
    print("="*70)

    # Load environment
    load_dotenv()

    # Configuration
    config = AgentConfig(
        domain=os.getenv("AGENT_DOMAIN", "simple-agent.example.com"),
        salt=os.getenv("AGENT_SALT", f"simple-{datetime.now().timestamp()}"),
        role=AgentRole.SERVER,
        rpc_url=os.getenv("RPC_URL", "https://sepolia.base.org"),
        chain_id=int(os.getenv("CHAIN_ID", "84532")),
        use_tee_auth=True,  # Enable TEE
        tee_endpoint=None   # Auto-detect
    )

    registries = RegistryAddresses(
        identity=os.getenv("IDENTITY_REGISTRY_ADDRESS", "0x000c5A70B7269c5eD4238DcC6576e598614d3f70"),
        reputation=os.getenv("REPUTATION_REGISTRY_ADDRESS", "0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde"),
        validation=os.getenv("VALIDATION_REGISTRY_ADDRESS", "0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d"),
        tee_verifier=os.getenv("TEE_VERIFIER_ADDRESS", "0x1b841e88ba786027f39ecf9Cd160176b22E3603c")
    )

    # Create agent
    print("\n1️⃣  Creating Agent...")
    agent = SimpleWorkingAgent(config, registries)

    # Get agent address
    print("\n2️⃣  Getting TEE-Derived Address...")
    address = await agent._get_agent_address()
    print(f"   Address: {address}")

    # Get attestation
    print("\n3️⃣  Generating TEE Attestation...")
    attestation = await agent.get_attestation()
    if "error" not in attestation:
        print(f"   ✓ Attestation: {len(attestation.get('quote', b''))} bytes")
        print(f"   ✓ App data: {attestation['application_data']['size']} bytes")
    else:
        print(f"   ✗ Error: {attestation['error']}")

    # Create agent card
    print("\n4️⃣  Creating Agent Card...")
    agent_card = await agent._create_agent_card()
    print(f"   Name: {agent_card['name']}")
    print(f"   Role: {agent_card['role']}")
    print(f"   Capabilities: {', '.join(agent_card['capabilities'])}")
    print(f"   TEE Enabled: {agent_card['tee_enabled']}")

    # Process some test tasks
    print("\n5️⃣  Processing Test Tasks...")

    test_tasks = [
        {
            "task_id": "task-001",
            "type": "analysis",
            "query": "Analyze market trends for Q4 2024"
        },
        {
            "task_id": "task-002",
            "type": "validation",
            "query": "Validate transaction data for smart contract"
        },
        {
            "task_id": "task-003",
            "type": "computation",
            "query": "Compute risk score for portfolio allocation"
        }
    ]

    results = []
    for task in test_tasks:
        result = await agent.process_task(task)
        results.append(result)

    # Show status
    print("\n6️⃣  Agent Status...")
    status = agent.get_status()
    print(f"   Domain: {status['domain']}")
    print(f"   Role: {status['role']}")
    print(f"   TEE Mode: {status['use_tee']}")
    print(f"   Tasks Processed: {agent.task_count}")

    # Summary
    print("\n" + "="*70)
    print("✅ EXAMPLE COMPLETE")
    print("="*70)
    print(f"Agent Address: {address}")
    print(f"Tasks Processed: {agent.task_count}")
    print(f"TEE Secured: {config.use_tee_auth}")
    print(f"Chain: Base Sepolia ({config.chain_id})")
    print("\n💡 Next Steps:")
    print("   - Implement custom task logic in process_task()")
    print("   - Register agent on-chain with agent.register()")
    print("   - Deploy to production TEE environment")
    print("   - Set up monitoring and logging")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())