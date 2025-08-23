#!/usr/bin/env python3
"""
Test script for the Validator Agent (Bob) - Validation Service
Tests validation capabilities and ERC-8004 integration
"""

import sys
import json
import os
from agents.validator_agent import ValidatorAgent
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

def test_validator_agent():
    """Test validator agent functionality"""
    print(f"\n{BLUE}{'='*60}")
    print(f"  Testing Validator Agent (Bob)")
    print(f"{'='*60}{RESET}")
    
    # Use Anvil test account #1 (Bob)
    bob_private_key = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d'
    bob_domain = "bob.validator.com"
    
    try:
        # Test 1: Initialize validator agent
        print("\n📋 Test 1: Validator Agent Initialization")
        bob = ValidatorAgent(
            agent_domain=bob_domain,
            private_key=bob_private_key
        )
        print_test("Validator agent initialization", bob is not None)
        print(f"   Agent address: {bob.address}")
        print(f"   Agent domain: {bob.agent_domain}")
        
        # Test 2: Register agent if needed
        print("\n✍️ Test 2: Agent Registration")
        if not bob.agent_id:
            bob_id = bob.register_agent()
            print_test("Agent registration", bob_id > 0)
            print(f"   Assigned Agent ID: {bob_id}")
        else:
            print(f"   Agent already registered with ID: {bob.agent_id}")
            print_test("Registration check", True)
        
        # Test 3: Create a market analysis to validate
        print("\n📊 Test 3: Prepare Analysis for Validation")
        
        # Create a sample analysis package
        sample_analysis = {
            "symbol": "ETH",
            "timeframe": "4h",
            "timestamp": 1234567890,
            "agent_id": 999,  # Dummy server agent ID
            "agent_domain": "test.server.com",
            "analysis": """
            # Market Analysis Report for ETH
            
            ## Executive Summary
            The market shows a **bullish** trend with strong momentum.
            
            ## Key Findings
            - **Current Trend**: Bullish
            - **Support Level**: $2,800
            - **Resistance Level**: $3,200
            - **Confidence Level**: 85%
            
            ## Recommendation
            **BUY** - Strong upward momentum detected
            
            ## Risk Assessment
            The market presents medium risk levels. Traders should use appropriate position sizing.
            """,
            "metadata": {
                "crew_agents": 2,
                "tasks_completed": 2,
                "analysis_method": "CrewAI Multi-Agent Analysis"
            }
        }
        
        # Save the analysis to data directory (simulating IPFS storage)
        os.makedirs("data", exist_ok=True)
        data_hash = "test_analysis_hash_123"
        with open(f"data/{data_hash}.json", 'w') as f:
            json.dump(sample_analysis, f, indent=2)
        
        print_test("Analysis preparation", True)
        print(f"   Sample analysis created for: {sample_analysis['symbol']}")
        print(f"   Data hash: {data_hash}")
        
        # Test 4: Validate the analysis
        print("\n🔍 Test 4: Analysis Validation")
        try:
            # Validate the analysis using the validator agent's method
            validation_result = bob.validate_analysis(data_hash)
            print_test("Analysis validation", validation_result is not None)
            
            if validation_result:
                print(f"   Validation score: {validation_result.get('validation_score')}/100")
                print(f"   Data hash: {validation_result.get('data_hash')}")
                print(f"   Validator ID: {validation_result.get('validator_agent_id')}")
                
                # Show validation report snippet
                report = str(validation_result.get('validation_report', ''))[:200]
                print(f"   Report preview: {report}...")
                
        except Exception as e:
            print_test("Analysis validation", False)
            print(f"   Error: {e}")
        
        # Test 5: Submit validation response
        print("\n📊 Test 5: Submit Validation Response")
        try:
            if validation_result:
                # Submit the validation response using the validation package
                tx_hash = bob.submit_validation_response(validation_result)
                print_test("Validation response submission", tx_hash is not None)
                print(f"   Transaction: {tx_hash}")
                print(f"   Score submitted: {validation_result.get('validation_score')}/100")
            else:
                print_test("Validation response submission", False)
                print("   No validation result to submit")
        except Exception as e:
            print_test("Validation response submission", False)
            print(f"   Error: {e}")
        
        # Test 6: Get trust models
        print("\n🔐 Test 6: Trust Models")
        trust_models = bob.get_trust_models()
        print_test("Trust models retrieval", len(trust_models) > 0)
        print(f"   Supported models: {', '.join(trust_models)}")
        
        # Test 7: Get agent card
        print("\n📇 Test 7: Agent Card")
        agent_card = bob.get_agent_card()
        print_test("Agent card generation", agent_card is not None)
        
        if agent_card:
            print(f"   Name: {agent_card.get('name')}")
            print(f"   Description: {agent_card.get('description')[:80]}...")
            print(f"   Skills: {len(agent_card.get('skills', []))} skill(s)")
            
            # Show skill details
            for skill in agent_card.get('skills', []):
                print(f"     - {skill.get('name')}: {skill.get('description')[:60]}...")
        
        print(f"\n{GREEN}✅ Validator agent tests completed successfully!{RESET}")
        return True
        
    except Exception as e:
        print(f"\n{RED}❌ Test failed with error: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_validator_agent()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}Fatal error: {e}{RESET}")
        sys.exit(1)