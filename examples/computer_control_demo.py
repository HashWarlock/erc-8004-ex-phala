#!/usr/bin/env python3
"""
Computer Control Agent Demo

Demonstrates TEE-secured computer control capabilities.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.base import AgentConfig, RegistryAddresses
from src.templates.computer_control_agent import ComputerControlAgent
from src.agent.tee_auth import TEEAuthenticator


async def demo_shell_execution(agent: ComputerControlAgent):
    """Demo: Execute shell commands."""
    print("\n" + "=" * 80)
    print("DEMO: Shell Execution")
    print("=" * 80)

    tasks = [
        {
            "task_id": "shell-001",
            "type": "shell",
            "command": "pwd"
        },
        {
            "task_id": "shell-002",
            "type": "shell",
            "command": "ls -la | head -10"
        },
        {
            "task_id": "shell-003",
            "type": "shell",
            "command": "echo 'Hello from TEE Agent!'"
        }
    ]

    for task in tasks:
        print(f"\n📌 Task: {task['task_id']}")
        print(f"   Command: {task['command']}")
        result = await agent.process_task(task)
        print(f"   Status: {result.get('status')}")
        if result.get('status') == 'completed':
            print(f"   Output:\n{result.get('output', '').strip()}")
        else:
            print(f"   Error: {result.get('error')}")


async def demo_file_operations(agent: ComputerControlAgent):
    """Demo: File operations."""
    print("\n" + "=" * 80)
    print("DEMO: File Operations")
    print("=" * 80)

    # Write a test file
    print("\n📝 Writing test file...")
    write_task = {
        "task_id": "file-001",
        "type": "file_write",
        "path": "/tmp/tee_agent_test.txt",
        "content": "Hello from TEE Computer Control Agent!\nTimestamp: {}\n".format(
            asyncio.get_event_loop().time()
        )
    }
    result = await agent.process_task(write_task)
    print(f"   Status: {result.get('status')}")
    if result.get('status') == 'completed':
        print(f"   Wrote {result.get('bytes_written')} bytes to {result.get('path')}")

    # Read the file back
    print("\n📖 Reading test file...")
    read_task = {
        "task_id": "file-002",
        "type": "file_read",
        "path": "/tmp/tee_agent_test.txt"
    }
    result = await agent.process_task(read_task)
    print(f"   Status: {result.get('status')}")
    if result.get('status') == 'completed':
        print(f"   Content:\n{result.get('content', '').strip()}")

    # List files
    print("\n📂 Listing /tmp directory...")
    list_task = {
        "task_id": "file-003",
        "type": "file_list",
        "directory": "/tmp"
    }
    result = await agent.process_task(list_task)
    print(f"   Status: {result.get('status')}")
    if result.get('status') == 'completed':
        files = result.get('files', [])
        print(f"   Found {len(files)} items")
        for f in files[:5]:  # Show first 5
            print(f"     - {f}")


async def demo_code_execution(agent: ComputerControlAgent):
    """Demo: Code execution."""
    print("\n" + "=" * 80)
    print("DEMO: Code Execution")
    print("=" * 80)

    # Python code
    print("\n🐍 Executing Python code...")
    python_task = {
        "task_id": "code-001",
        "type": "code_python",
        "code": """
import datetime
import platform

print(f"Python Version: {platform.python_version()}")
print(f"Current Time: {datetime.datetime.now()}")
print(f"Platform: {platform.system()}")

# Simple calculation
result = sum(range(1, 101))
print(f"Sum of 1-100: {result}")
"""
    }
    result = await agent.process_task(python_task)
    print(f"   Status: {result.get('status')}")
    if result.get('status') == 'completed':
        print(f"   Output:\n{result.get('output', '').strip()}")
    else:
        print(f"   Error: {result.get('error')}")

    # Node.js code
    print("\n📦 Executing Node.js code...")
    nodejs_task = {
        "task_id": "code-002",
        "type": "code_nodejs",
        "code": """
console.log('Node.js Version:', process.version);
console.log('Platform:', process.platform);

// Simple calculation
const result = Array.from({length: 100}, (_, i) => i + 1)
    .reduce((sum, n) => sum + n, 0);
console.log('Sum of 1-100:', result);
"""
    }
    result = await agent.process_task(nodejs_task)
    print(f"   Status: {result.get('status')}")
    if result.get('status') == 'completed':
        print(f"   Output:\n{result.get('output', '').strip()}")
    else:
        print(f"   Error: {result.get('error')}")


async def demo_system_info(agent: ComputerControlAgent):
    """Demo: System information."""
    print("\n" + "=" * 80)
    print("DEMO: System Information")
    print("=" * 80)

    task = {
        "task_id": "system-001",
        "type": "system_info"
    }

    result = await agent.process_task(task)
    print(f"\n   Status: {result.get('status')}")
    if result.get('status') == 'completed':
        info = result.get('system_info', {})
        for key, value in info.items():
            print(f"\n   {key.upper()}:")
            print(f"   {value[:100]}..." if len(value) > 100 else f"   {value}")


async def demo_agent_card(agent: ComputerControlAgent):
    """Demo: Agent card generation."""
    print("\n" + "=" * 80)
    print("DEMO: Agent Card (ERC-8004)")
    print("=" * 80)

    card = await agent._create_agent_card()

    print(f"\n📋 Name: {card['name']}")
    print(f"📝 Description: {card['description'][:100]}...")
    print(f"\n✨ Capabilities:")
    for cap in card.get('capabilities', []):
        print(f"   • {cap['name']}: {cap['description']}")

    print(f"\n🔒 Trust Models:")
    for tm in card.get('trustModels', []):
        print(f"   • {tm['type']}: {tm.get('provider', 'N/A')}")

    print(f"\n🖥️  Infrastructure:")
    infra = card.get('infrastructure', {})
    for key, value in infra.items():
        print(f"   • {key}: {value}")


async def main():
    """Run computer control demo."""
    print("=" * 80)
    print("TEE COMPUTER CONTROL AGENT - DEMO")
    print("=" * 80)

    # Configuration
    domain = os.getenv("AGENT_DOMAIN", "demo.localhost:8000")
    salt = os.getenv("AGENT_SALT", "demo-computer-control")
    sandbox_url = os.getenv("SANDBOX_URL", "http://localhost:8080")

    print(f"\n📍 Domain: {domain}")
    print(f"🔐 Salt: {salt}")
    print(f"🖥️  Sandbox: {sandbox_url}")

    # Check TEE availability
    print("\n🔍 Checking TEE environment...")
    use_tee = os.path.exists("/var/run/dstack.sock") or os.getenv("DSTACK_SIMULATOR_ENDPOINT")
    if not use_tee:
        print("⚠️  No TEE detected. Using standard key derivation.")
    else:
        print("✅ TEE environment detected")

    # Initialize TEE auth
    print("\n🔑 Initializing TEE authentication...")
    tee_auth = TEEAuthenticator(
        domain=domain,
        salt=salt,
        use_tee=use_tee
    )

    address = await tee_auth.derive_address()
    print(f"✅ Agent Address: {address}")

    # Create agent
    print("\n🤖 Initializing computer control agent...")
    config = AgentConfig(
        domain=domain,
        chain_id=84532,
        rpc_url="https://sepolia.base.org",
        private_key=tee_auth.private_key
    )

    registries = RegistryAddresses(
        identity_registry="0x000c5A70B7269c5eD4238DcC6576e598614d3f70",
        reputation_registry=None,
        validation_registry=None
    )

    agent = ComputerControlAgent(config, registries, sandbox_url=sandbox_url)
    await agent.initialize()

    if not agent.sandbox_client:
        print("\n⚠️  Sandbox client not available!")
        print("   Install with: pip install aio-sandbox")
        print("   Start sandbox at: {}".format(sandbox_url))
        return

    print("✅ Agent initialized successfully")

    # Run demos
    try:
        await demo_agent_card(agent)
        await demo_shell_execution(agent)
        await demo_file_operations(agent)
        await demo_code_execution(agent)
        await demo_system_info(agent)

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Start the computer control server:")
    print("     python deployment/computer_control_server.py")
    print("  2. Test via HTTP API:")
    print("     curl http://localhost:8000/api/control \\")
    print("       -X POST -H 'Content-Type: application/json' \\")
    print("       -d '{\"task_id\":\"test\",\"type\":\"shell\",\"command\":\"pwd\"}'")
    print("  3. View API docs at http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(main())
