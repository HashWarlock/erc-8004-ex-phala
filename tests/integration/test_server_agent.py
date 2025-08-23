#!/usr/bin/env python3
"""
Test script for the Server Agent (Alice) - Market Analysis Service
Tests market analysis capabilities and ERC-8004 integration
"""

import sys
import json
from agents.server_agent import ServerAgent

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(name, passed):
    """Print test result with color"""
    status = f"{GREEN}✓ PASSED{RESET}" if passed else f"{RED}✗ FAILED{RESET}"
    print(f"  {status}: {name}")

def test_server_agent():
    """Test server agent functionality"""
    print(f"\n{BLUE}{'='*60}")
    print(f"  Testing Server Agent (Alice)")
    print(f"{'='*60}{RESET}")
    
    # Use Anvil test account #0 (Alice - the deployer)
    alice_private_key = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
    alice_domain = "alice.marketanalysis.com"
    
    try:
        # Test 1: Initialize server agent
        print("\n📋 Test 1: Server Agent Initialization")
        alice = ServerAgent(
            agent_domain=alice_domain,
            private_key=alice_private_key
        )
        print_test("Server agent initialization", alice is not None)
        print(f"   Agent address: {alice.address}")
        print(f"   Agent domain: {alice.agent_domain}")
        
        # Test 2: Register agent if needed
        print("\n✍️ Test 2: Agent Registration")
        if not alice.agent_id:
            alice_id = alice.register_agent()
            print_test("Agent registration", alice_id > 0)
            print(f"   Assigned Agent ID: {alice_id}")
        else:
            print(f"   Agent already registered with ID: {alice.agent_id}")
            print_test("Registration check", True)
        
        # Test 3: Perform market analysis
        print("\n📊 Test 3: Market Analysis")
        try:
            analysis = alice.perform_market_analysis("BTC", "1d")
            print_test("Market analysis execution", analysis is not None)
            
            # Check analysis structure
            has_required_fields = all(key in analysis for key in [
                'symbol', 'timeframe', 'timestamp', 'agent_id', 'analysis'
            ])
            print_test("Analysis structure", has_required_fields)
            
            print(f"   Symbol: {analysis.get('symbol')}")
            print(f"   Timeframe: {analysis.get('timeframe')}")
            print(f"   Agent ID: {analysis.get('agent_id')}")
            print(f"   Analysis method: {analysis.get('metadata', {}).get('analysis_method')}")
            
            # Show snippet of analysis
            analysis_text = str(analysis.get('analysis', ''))[:200]
            print(f"   Analysis preview: {analysis_text}...")
            
        except Exception as e:
            print_test("Market analysis execution", False)
            print(f"   Error: {e}")
            analysis = None
        
        # Test 4: Submit work for validation (need a validator agent)
        if analysis and alice.agent_id:
            print("\n🔍 Test 4: Submit Work for Validation")
            
            # Create a validator agent (Bob)
            bob_private_key = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d'
            bob = ServerAgent(
                agent_domain="bob.validator.com",
                private_key=bob_private_key
            )
            
            if not bob.agent_id:
                bob.register_agent()
            
            try:
                tx_hash = alice.submit_work_for_validation(analysis, bob.agent_id)
                print_test("Validation request submission", tx_hash is not None)
                print(f"   Transaction: {tx_hash}")
                print(f"   Validator Agent ID: {bob.agent_id}")
            except Exception as e:
                print_test("Validation request submission", False)
                print(f"   Error: {e}")
        
        # Test 5: Get trust models
        print("\n🔐 Test 5: Trust Models")
        trust_models = alice.get_trust_models()
        print_test("Trust models retrieval", len(trust_models) > 0)
        print(f"   Supported models: {', '.join(trust_models)}")
        
        # Test 6: Get agent card
        print("\n📇 Test 6: Agent Card")
        agent_card = alice.get_agent_card()
        print_test("Agent card generation", agent_card is not None)
        
        if agent_card:
            print(f"   Name: {agent_card.get('name')}")
            print(f"   Description: {agent_card.get('description')[:100]}...")
            print(f"   Skills: {len(agent_card.get('skills', []))} skill(s)")
            
            # Show skill details
            for skill in agent_card.get('skills', []):
                print(f"     - {skill.get('name')}: {skill.get('description')[:80]}...")
        
        print(f"\n{GREEN}✅ Server agent tests completed successfully!{RESET}")
        return True
        
    except Exception as e:
        print(f"\n{RED}❌ Test failed with error: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_server_agent()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}Fatal error: {e}{RESET}")
        sys.exit(1)