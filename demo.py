#!/usr/bin/env python3
"""
ERC-8004 Trustless Agents Demo

This script demonstrates the complete ERC-8004 workflow with AI agents:
1. Deploy registry contracts
2. Register Server and Validator agents
3. Server agent performs market analysis 
4. Server agent requests validation
5. Validator agent validates the work 
6. Validator agent submits validation response
7. Client agent authorizes feedback
8. Display complete audit trail

Usage:
    python demo.py
"""

import os
import sys
import time
import subprocess
from dotenv import load_dotenv

# Add agents directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from agents.server_agent import ServerAgent
from agents.validator_agent import ValidatorAgent
from agents.base_agent import ERC8004BaseAgent

# Load environment variables
load_dotenv()

def print_banner():
    """Print demo banner"""
    print("=" * 80)
    print("ERC-8004 TRUSTLESS AGENTS DEMO")
    print("=" * 80)
    print()
    print("This demo showcases:")
    print("✅ ERC-8004 registry contracts deployment")
    print("✅ AI agents for market analysis")
    print("✅ Trustless validation through blockchain")
    print("✅ Complete audit trail and feedback system")
    print()
    print("=" * 80)
    print()

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check if contracts are compiled
    contracts_dir = "contracts/out"
    required_contracts = ["IdentityRegistry.sol", "ReputationRegistry.sol", "ValidationRegistry.sol"]
    
    for contract in required_contracts:
        contract_path = os.path.join(contracts_dir, contract, f"{contract.replace('.sol', '')}.json")
        if not os.path.exists(contract_path):
            print(f"❌ Contract artifact not found: {contract_path}")
            print("Please compile contracts first:")
            print("   cd contracts && forge build")
            return False
    
    # Check environment variables
    required_vars = ["RPC_URL", "PRIVATE_KEY"]
    for var in required_vars:
        if not os.getenv(var):
            print(f"❌ Environment variable not set: {var}")
            print("Please copy .env.example to .env and configure it")
            return False
    
    print("✅ All prerequisites met!")
    return True

def deploy_contracts():
    """Deploy the registry contracts"""
    print("\n📦 STEP 1: Deploying Registry Contracts")
    print("-" * 50)
    
    # Check if already deployed
    if os.path.exists("deployment.json"):
        print("ℹ️  Contracts already deployed (deployment.json exists)")
        print("   Delete deployment.json to redeploy")
        return True
    
    try:
        # Run deployment script
        result = subprocess.run([
            sys.executable, "scripts/deploy.py"
        ], capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print("✅ Contracts deployed successfully!")
            return True
        else:
            print(f"❌ Deployment failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False

def initialize_agents():
    """Initialize the demo agents"""
    print("\n🤖 STEP 2: Initializing AI Agents")
    print("-" * 50)
    
    # Use different private keys for different agents (in production, these would be separate entities)
    server_key = os.getenv('PRIVATE_KEY')
    # Generate a different key for validator (simplified for demo)
    validator_key = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"  # Anvil account #1
    client_key = "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a"    # Anvil account #2
    
    try:
        # Initialize Server Agent (Alice)
        print("🔧 Initializing Server Agent (Alice)...")
        alice = ServerAgent(
            agent_domain=os.getenv('AGENT_DOMAIN_ALICE', 'alice.example.com'),
            private_key=server_key
        )
        
        # Initialize Validator Agent (Bob)
        print("🔧 Initializing Validator Agent (Bob)...")
        bob = ValidatorAgent(
            agent_domain=os.getenv('AGENT_DOMAIN_BOB', 'bob.example.com'),
            private_key=validator_key
        )
        
        # Initialize Client Agent (Charlie) - for feedback
        print("🔧 Initializing Client Agent (Charlie)...")
        charlie = ERC8004BaseAgent(
            agent_domain="charlie.example.com",
            private_key=client_key
        )
        
        return alice, bob, charlie
        
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return None, None, None

def register_agents(alice, bob, charlie):
    """Register all agents with the registry"""
    print("\n📝 STEP 3: Registering Agents")
    print("-" * 50)
    
    try:
        # Register Alice (Server Agent)
        print("📝 Registering Alice (Server Agent)...")
        alice_id = alice.register_agent()
        
        # Register Bob (Validator Agent)
        print("📝 Registering Bob (Validator Agent)...")
        bob_id = bob.register_agent()
        
        # Register Charlie (Client Agent)
        print("📝 Registering Charlie (Client Agent)...")
        charlie_id = charlie.register_agent()
        
        print(f"✅ All agents registered successfully!")
        print(f"   Alice (Server): ID {alice_id}")
        print(f"   Bob (Validator): ID {bob_id}")
        print(f"   Charlie (Client): ID {charlie_id}")
        
        return alice_id, bob_id, charlie_id
        
    except Exception as e:
        print(f"❌ Agent registration failed: {e}")
        return None, None, None

def demonstrate_market_analysis(alice, bob_id):
    """Demonstrate market analysis and validation workflow"""
    print("\n📊 STEP 4: Market Analysis & Validation Workflow")
    print("-" * 50)
    
    try:
        # Alice performs market analysis
        print("🔍 Alice performing market analysis for BTC...")
        analysis_package = alice.perform_market_analysis("BTC", "1d")
        
        print(f"✅ Analysis completed!")
        print(f"   Symbol: {analysis_package['symbol']}")
        print(f"   Timestamp: {analysis_package['timestamp']}")
        print(f"   Method: {analysis_package['metadata']['analysis_method']}")
        
        # Alice submits work for validation
        print(f"\n📤 Alice requesting validation from Bob (Agent {bob_id})...")
        validation_tx = alice.submit_work_for_validation(analysis_package, bob_id)
        
        print(f"✅ Validation request submitted!")
        print(f"   Transaction: {validation_tx}")
        
        return analysis_package
        
    except Exception as e:
        print(f"❌ Market analysis failed: {e}")
        return None

def demonstrate_validation(bob, analysis_package):
    """Demonstrate validation workflow"""
    print("\n🔍 STEP 5: AI-Powered Validation")
    print("-" * 50)
    
    try:
        # Extract data hash from the analysis package
        import hashlib
        import json
        
        analysis_json = json.dumps(analysis_package, sort_keys=True)
        data_hash = hashlib.sha256(analysis_json.encode()).hexdigest()
        
        print(f"🔍 Bob validating analysis (hash: {data_hash[:16]}...)...")
        
        # Bob validates the analysis
        validation_package = bob.validate_analysis(data_hash)
        
        if validation_package.get("error"):
            print(f"❌ Validation failed: {validation_package['error']}")
            return None
        
        print(f"✅ Validation completed!")
        print(f"   Score: {validation_package['validation_score']}/100")
        print(f"   Method: {validation_package['metadata']['validation_method']}")
        
        # Bob submits validation response
        print(f"\n📤 Bob submitting validation response...")
        response_tx = bob.submit_validation_response(validation_package)
        
        print(f"✅ Validation response submitted!")
        print(f"   Transaction: {response_tx}")
        
        return validation_package
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return None

def demonstrate_feedback(alice, charlie_id):
    """Demonstrate feedback authorization"""
    print("\n💬 STEP 6: Feedback Authorization")
    print("-" * 50)
    
    try:
        print(f"🔐 Alice authorizing feedback from Charlie (Agent {charlie_id})...")
        
        # Alice (server) authorizes feedback from Charlie (client)
        feedback_tx = alice.authorize_feedback(charlie_id)
        
        print(f"✅ Feedback authorization successful!")
        print(f"   Transaction: {feedback_tx}")
        
        return True
        
    except Exception as e:
        print(f"❌ Feedback authorization failed: {e}")
        return False

def display_audit_trail(alice, bob, charlie, analysis_package, validation_package):
    """Display the complete audit trail"""
    print("\n📋 STEP 7: Complete Audit Trail")
    print("-" * 50)
    
    print("🔗 BLOCKCHAIN AUDIT TRAIL:")
    print(f"   Chain ID: {alice.w3.eth.chain_id}")
    print(f"   Identity Registry: {alice.identity_registry_address}")
    print(f"   Reputation Registry: {alice.reputation_registry_address}")
    print(f"   Validation Registry: {alice.validation_registry_address}")
    print()
    
    print("👥 REGISTERED AGENTS:")
    print(f"   Alice (Server): ID {alice.agent_id} - {alice.address}")
    print(f"   Bob (Validator): ID {bob.agent_id} - {bob.address}")
    print(f"   Charlie (Client): ID {charlie.agent_id} - {charlie.address}")
    print()
    
    print("📊 ANALYSIS WORK:")
    print(f"   Symbol: {analysis_package['symbol']}")
    print(f"   Agent: {analysis_package['agent_domain']} (ID {analysis_package['agent_id']})")
    print(f"   Timestamp: {analysis_package['timestamp']}")
    print(f"   AI Method: {analysis_package['metadata']['analysis_method']}")
    print()
    
    print("✅ VALIDATION RESULTS:")
    print(f"   Validator: {validation_package['validator_domain']} (ID {validation_package['validator_agent_id']})")
    print(f"   Score: {validation_package['validation_score']}/100")
    print(f"   Timestamp: {validation_package['timestamp']}")
    print(f"   AI Method: {validation_package['metadata']['validation_method']}")
    print()
    
    print("🎯 TRUST MODELS DEMONSTRATED:")
    print("   ✅ Identity Registry - Sovereign agent identities")
    print("   ✅ Reputation Registry - Feedback authorization")
    print("   ✅ Validation Registry - Cryptoeconomic validation")
    print("   ✅ AI-Powered Analysis - CrewAI multi-agent workflows")
    print("   ✅ Trustless Verification - Blockchain-based audit trail")

def main():
    """Main demo function"""
    print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        return 1
    
    # Deploy contracts
    if not deploy_contracts():
        return 1
    
    # Initialize agents
    alice, bob, charlie = initialize_agents()
    if not alice or not bob or not charlie:
        return 1
    
    # Register agents
    alice_id, bob_id, charlie_id = register_agents(alice, bob, charlie)
    if not alice_id or not bob_id or not charlie_id:
        return 1
    
    # Demonstrate market analysis workflow
    analysis_package = demonstrate_market_analysis(alice, bob_id)
    if not analysis_package:
        return 1
    
    # Wait a moment for blockchain confirmation
    print("\n⏳ Waiting for blockchain confirmation...")
    time.sleep(2)
    
    # Demonstrate validation workflow
    validation_package = demonstrate_validation(bob, analysis_package)
    if not validation_package:
        return 1
    
    # Demonstrate feedback authorization
    if not demonstrate_feedback(alice, charlie_id):
        return 1
    
    # Display complete audit trail
    display_audit_trail(alice, bob, charlie, analysis_package, validation_package)
    
    print("\n" + "=" * 80)
    print("🎉 ERC-8004 DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print()
    print("What you just saw:")
    print("• AI agents using CrewAI for sophisticated analysis and validation")
    print("• Trustless interactions through ERC-8004 registries")
    print("• Complete blockchain audit trail for accountability")
    print("• Decentralized reputation and validation systems")
    print()
    print("This demonstrates the foundation for a trustless agent economy!")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 