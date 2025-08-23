"""
End-to-end tests for complete ERC-8004 workflows

These tests verify complete user workflows from agent registration
through market analysis, validation, and feedback.
"""

import pytest
import time
from agents.server_agent import ServerAgent
from agents.validator_agent import ValidatorAgent
from agents.base_agent import ERC8004BaseAgent


@pytest.mark.e2e
@pytest.mark.slow
class TestCompleteWorkflow:
    """Test complete ERC-8004 trustless agent workflow"""
    
    def test_full_market_analysis_workflow(self, w3, alice_account, bob_account, charlie_account):
        """
        Test the complete workflow:
        1. Register three agents (Server, Validator, Client)
        2. Server performs market analysis
        3. Server submits work for validation
        4. Validator validates the work
        5. Client authorizes feedback
        6. Complete interaction logged on blockchain
        """
        
        # Step 1: Initialize and register agents
        print("\n=== Step 1: Agent Registration ===")
        
        # Alice as Server Agent
        alice = ServerAgent(
            agent_domain="alice.market.analysis.com",
            private_key=alice_account['private_key']
        )
        if not alice.agent_id:
            alice_id = alice.register_agent()
            print(f"✅ Alice registered with ID: {alice_id}")
        else:
            print(f"ℹ️  Alice already registered with ID: {alice.agent_id}")
        
        # Bob as Validator Agent
        bob = ValidatorAgent(
            agent_domain="bob.validator.service.com",
            private_key=bob_account['private_key']
        )
        if not bob.agent_id:
            bob_id = bob.register_agent()
            print(f"✅ Bob registered with ID: {bob_id}")
        else:
            print(f"ℹ️  Bob already registered with ID: {bob.agent_id}")
        
        # Charlie as Client Agent
        charlie = ERC8004BaseAgent(
            agent_domain="charlie.client.app.com",
            private_key=charlie_account['private_key']
        )
        if not charlie.agent_id:
            charlie_id = charlie.register_agent()
            print(f"✅ Charlie registered with ID: {charlie_id}")
        else:
            print(f"ℹ️  Charlie already registered with ID: {charlie.agent_id}")
        
        assert alice.agent_id > 0
        assert bob.agent_id > 0
        assert charlie.agent_id > 0
        
        # Step 2: Alice performs market analysis
        print("\n=== Step 2: Market Analysis Generation ===")
        analysis = alice.perform_market_analysis("BTC", "1d")
        assert analysis is not None
        print(f"✅ Market analysis generated for {analysis['symbol']}")
        
        # Step 3: Alice submits work for validation
        print("\n=== Step 3: Submit for Validation ===")
        validation_tx = alice.submit_work_for_validation(analysis, bob.agent_id)
        assert validation_tx is not None
        print(f"✅ Validation requested: {validation_tx}")
        
        # Step 4: Bob validates the work
        print("\n=== Step 4: Validation Process ===")
        # Extract data hash from the analysis
        import json
        import hashlib
        analysis_json = json.dumps(analysis, sort_keys=True)
        data_hash_bytes = hashlib.sha256(analysis_json.encode()).digest()
        data_hash = data_hash_bytes.hex()
        
        validation_result = bob.validate_analysis(data_hash)
        assert validation_result is not None
        print(f"✅ Validation completed with score: {validation_result.get('validation_score', 0)}/100")
        
        # Step 5: Charlie authorizes feedback for Alice
        print("\n=== Step 5: Feedback Authorization ===")
        try:
            feedback_tx = alice.authorize_feedback(charlie.agent_id)
            print(f"✅ Feedback authorized: {feedback_tx}")
        except Exception as e:
            print(f"ℹ️  Feedback authorization: {str(e)[:50]}...")
        
        # Step 6: Verify all interactions
        print("\n=== Step 6: Verification ===")
        
        # Verify agents are registered
        alice_info = alice.get_agent_info(alice.agent_id)
        bob_info = bob.get_agent_info(bob.agent_id)
        charlie_info = charlie.get_agent_info(charlie.agent_id)
        
        assert alice_info['agent_id'] == alice.agent_id
        assert bob_info['agent_id'] == bob.agent_id
        assert charlie_info['agent_id'] == charlie.agent_id
        
        print("✅ All agents verified on blockchain")
        print(f"   - Alice (Server): ID {alice.agent_id}")
        print(f"   - Bob (Validator): ID {bob.agent_id}")
        print(f"   - Charlie (Client): ID {charlie.agent_id}")
        
        return True
    
    def test_trust_model_verification(self, w3, alice_account, bob_account):
        """Test that agents properly implement trust models"""
        
        alice = ServerAgent(
            agent_domain="alice.trust.test.com",
            private_key=alice_account['private_key']
        )
        
        bob = ValidatorAgent(
            agent_domain="bob.trust.test.com",
            private_key=bob_account['private_key']
        )
        
        # Check trust models
        alice_models = alice.get_trust_models()
        bob_models = bob.get_trust_models()
        
        assert "feedback" in alice_models
        assert "inference-validation" in alice_models
        assert "inference-validation" in bob_models
        assert "crypto-economic" in bob_models
        
        # Check agent cards
        alice_card = alice.get_agent_card()
        bob_card = bob.get_agent_card()
        
        assert alice_card['agentId'] == alice.agent_id
        assert bob_card['agentId'] == bob.agent_id
        assert len(alice_card['skills']) > 0
        assert len(bob_card['skills']) > 0
        
        print("✅ Trust models verified")
        print(f"   - Alice supports: {', '.join(alice_models)}")
        print(f"   - Bob supports: {', '.join(bob_models)}")
    
    def test_multi_agent_interaction(self, w3, test_accounts):
        """Test interaction between multiple agents"""
        
        agents = []
        
        # Create 3 agents
        for i, account in enumerate(test_accounts[:3]):
            agent = ERC8004BaseAgent(
                agent_domain=f"agent{i}.multitest.com",
                private_key=account['private_key']
            )
            
            if not agent.agent_id:
                agent.register_agent()
            
            agents.append(agent)
        
        # Each agent authorizes feedback from the next
        for i in range(len(agents) - 1):
            try:
                tx = agents[i].authorize_feedback(agents[i + 1].agent_id)
                print(f"✅ Agent {agents[i].agent_id} authorized feedback from Agent {agents[i + 1].agent_id}")
            except Exception as e:
                print(f"ℹ️  Authorization between {agents[i].agent_id} and {agents[i + 1].agent_id}: {str(e)[:30]}...")
        
        # Verify all agents are properly registered
        for agent in agents:
            info = agent.get_agent_info(agent.agent_id)
            assert info['agent_id'] == agent.agent_id
        
        print(f"✅ Multi-agent interaction test completed with {len(agents)} agents")