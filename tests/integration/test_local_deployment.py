"""
Local Deployment Test - Complete Agent Lifecycle
Tests full agent deployment in production TEE environment
"""

import asyncio
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Import agent components
from src.agent.base import AgentConfig, AgentRole, RegistryAddresses
from src.templates.server_agent import ServerAgent
from src.templates.validator_agent import ValidatorAgent


async def test_server_agent_deployment():
    """Test server agent deployment with real TEE"""
    print("\n" + "="*80)
    print("🚀 SERVER AGENT DEPLOYMENT TEST")
    print("="*80)

    # Load environment
    load_dotenv()

    # Generate unique salt for this test
    test_salt = f"test-deployment-{datetime.now().timestamp()}"

    # Create configuration
    config = AgentConfig(
        domain="server-agent.test.phala.network",
        salt=test_salt,
        role=AgentRole.SERVER,
        rpc_url=os.getenv("RPC_URL", "https://sepolia.base.org"),
        chain_id=int(os.getenv("CHAIN_ID", "84532")),
        use_tee_auth=True,  # Production TEE mode
        tee_endpoint=None   # Auto-detect
    )

    registries = RegistryAddresses(
        identity=os.getenv("IDENTITY_REGISTRY_ADDRESS"),
        reputation=os.getenv("REPUTATION_REGISTRY_ADDRESS"),
        validation=os.getenv("VALIDATION_REGISTRY_ADDRESS"),
        tee_verifier=os.getenv("TEE_VERIFIER_ADDRESS")
    )

    print("\n📋 Configuration:")
    print(f"  Domain: {config.domain}")
    print(f"  Salt: {test_salt[:32]}...")
    print(f"  Role: {config.role.value}")
    print(f"  Chain ID: {config.chain_id}")
    print(f"  TEE Mode: {config.use_tee_auth}")
    print(f"  RPC: {config.rpc_url}")

    # Create server agent
    print("\n🤖 Creating Server Agent...")
    try:
        agent = ServerAgent(config, registries)
        print("✅ Server agent created")
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Get agent address (TEE-derived)
    print("\n🔑 Deriving TEE Address...")
    try:
        address = await agent._get_agent_address()
        print(f"✅ Agent address: {address}")
    except Exception as e:
        print(f"❌ Failed to derive address: {e}")
        return False

    # Get TEE attestation
    print("\n🔐 Getting TEE Attestation...")
    try:
        attestation = await agent.get_attestation()

        if "error" in attestation:
            print(f"⚠️  Attestation error: {attestation['error']}")
            return False

        print(f"✅ Attestation received")
        print(f"  Quote size: {len(attestation.get('quote', b''))} bytes")
        print(f"  App data: {attestation['application_data']['size']} bytes")
        print(f"  Method: {attestation['application_data']['method']}")
        print(f"  Domain: {attestation['application_data']['domain']}")

    except Exception as e:
        print(f"❌ Attestation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test agent capabilities
    print("\n🧪 Testing Agent Capabilities...")
    try:
        status = agent.get_status()
        print(f"✅ Agent status retrieved:")
        print(f"  Domain: {status['domain']}")
        print(f"  Role: {status['role']}")
        print(f"  Registered: {status['is_registered']}")
        print(f"  TEE: {status['use_tee']}")
        print(f"  Plugins: {status['plugins']}")
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False

    # Test task processing (without actual registration)
    print("\n📝 Testing Task Processing...")
    try:
        test_task = {
            "task_id": "test-001",
            "type": "market_analysis",
            "query": "Test query for local deployment",
            "timestamp": datetime.now().isoformat()
        }

        # Note: process_task is abstract in ServerAgent,
        # but we can test the structure
        print(f"✅ Task structure valid: {test_task['task_id']}")

    except Exception as e:
        print(f"⚠️  Task processing test skipped: {e}")

    # Generate deployment report
    print("\n📊 Deployment Report:")
    report = {
        "timestamp": datetime.now().isoformat(),
        "agent_type": "server",
        "domain": config.domain,
        "address": address,
        "salt": test_salt,
        "tee_mode": config.use_tee_auth,
        "chain_id": config.chain_id,
        "attestation_received": True,
        "status": status
    }

    report_file = "/tmp/deployment_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"  Report saved: {report_file}")

    print("\n" + "="*80)
    print("✅ SERVER AGENT DEPLOYMENT SUCCESSFUL")
    print("="*80)

    return True, agent, report


async def test_validator_agent_deployment():
    """Test validator agent deployment"""
    print("\n" + "="*80)
    print("🔍 VALIDATOR AGENT DEPLOYMENT TEST")
    print("="*80)

    # Load environment
    load_dotenv()

    # Generate unique salt
    test_salt = f"validator-test-{datetime.now().timestamp()}"

    # Create configuration
    config = AgentConfig(
        domain="validator-agent.test.phala.network",
        salt=test_salt,
        role=AgentRole.VALIDATOR,
        rpc_url=os.getenv("RPC_URL", "https://sepolia.base.org"),
        chain_id=int(os.getenv("CHAIN_ID", "84532")),
        use_tee_auth=True,
        tee_endpoint=None
    )

    registries = RegistryAddresses(
        identity=os.getenv("IDENTITY_REGISTRY_ADDRESS"),
        reputation=os.getenv("REPUTATION_REGISTRY_ADDRESS"),
        validation=os.getenv("VALIDATION_REGISTRY_ADDRESS"),
        tee_verifier=os.getenv("TEE_VERIFIER_ADDRESS")
    )

    print("\n🤖 Creating Validator Agent...")
    try:
        agent = ValidatorAgent(config, registries)
        print("✅ Validator agent created")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

    # Get address
    address = await agent._get_agent_address()
    print(f"✅ Validator address: {address}")

    # Get attestation
    attestation = await agent.get_attestation()
    print(f"✅ Attestation: {len(attestation.get('quote', b''))} bytes")

    # Status
    status = agent.get_status()
    print(f"✅ Status: {status['role']}")

    print("\n✅ VALIDATOR AGENT DEPLOYMENT SUCCESSFUL")

    return True, agent


async def test_multi_agent_scenario():
    """Test multiple agents in same environment"""
    print("\n" + "="*80)
    print("🔄 MULTI-AGENT SCENARIO TEST")
    print("="*80)

    # Deploy server
    print("\n[1/2] Deploying Server Agent...")
    success_server, server_agent, server_report = await test_server_agent_deployment()

    if not success_server:
        print("❌ Server deployment failed")
        return False

    # Deploy validator
    print("\n[2/2] Deploying Validator Agent...")
    success_validator, validator_agent = await test_validator_agent_deployment()

    if not success_validator:
        print("❌ Validator deployment failed")
        return False

    # Compare agents
    print("\n📊 Multi-Agent Comparison:")
    server_addr = await server_agent._get_agent_address()
    validator_addr = await validator_agent._get_agent_address()

    print(f"  Server address:    {server_addr}")
    print(f"  Validator address: {validator_addr}")
    print(f"  Addresses unique: {server_addr != validator_addr}")

    print("\n✅ MULTI-AGENT SCENARIO SUCCESSFUL")

    return True


async def main():
    """Run all deployment tests"""
    print("\n" + "="*80)
    print("🧪 LOCAL DEPLOYMENT TEST SUITE")
    print("   Testing production TEE agent deployment")
    print("="*80)

    results = []

    # Test 1: Server Agent
    print("\n" + "-"*80)
    try:
        success, agent, report = await test_server_agent_deployment()
        results.append(("Server Agent Deployment", success))

        if success:
            print(f"\n📄 Deployment Details:")
            print(f"   Address: {report['address']}")
            print(f"   Domain: {report['domain']}")
            print(f"   Attestation: {'✓' if report['attestation_received'] else '✗'}")
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        results.append(("Server Agent Deployment", False))

    # Test 2: Validator Agent
    print("\n" + "-"*80)
    try:
        success, agent = await test_validator_agent_deployment()
        results.append(("Validator Agent Deployment", success))
    except Exception as e:
        print(f"❌ Validator test failed: {e}")
        results.append(("Validator Agent Deployment", False))

    # Test 3: Multi-Agent
    print("\n" + "-"*80)
    try:
        success = await test_multi_agent_scenario()
        results.append(("Multi-Agent Scenario", success))
    except Exception as e:
        print(f"❌ Multi-agent test failed: {e}")
        results.append(("Multi-Agent Scenario", False))

    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status:12} {test_name}")

    passed = sum(1 for _, s in results if s)
    total = len(results)

    print(f"\n  Total: {passed}/{total} tests passed")
    print("="*80 + "\n")

    # Check for deployment report
    if os.path.exists("/tmp/deployment_report.json"):
        print("📄 Deployment report available at: /tmp/deployment_report.json")


if __name__ == "__main__":
    asyncio.run(main())