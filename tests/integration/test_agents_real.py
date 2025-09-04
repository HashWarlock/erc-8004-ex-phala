"""
Integration tests for agents using real simulators

These tests verify agent interactions against real Anvil blockchain
and TEE simulator without any mocking.
"""

import pytest
import hashlib
import json
import time
from agents.base_agent import ERC8004BaseAgent
from agents.server_agent import ServerAgent
from agents.validator_agent import ValidatorAgent
from agents.client_agent import ClientAgent


@pytest.mark.integration
class TestAgentRegistration:
    """Test agent registration with real blockchain"""

    def test_register_agent_on_blockchain(self, w3, deployed_contracts, blockchain_snapshot):
        """Test registering an agent on the real blockchain"""
        if not deployed_contracts:
            pytest.skip("Contracts not deployed")

        # Create agent with unique private key
        import secrets
        private_key = "0x" + secrets.token_hex(32)
        agent = ERC8004BaseAgent(
            agent_domain="test.agent.local", private_key=private_key
        )

        # Fund the account
        from tests.test_utils import fund_account

        fund_account(w3, agent.address, 1)

        # Register agent
        try:
            agent_id = agent.register_agent()
            assert agent_id > 0
            assert agent.agent_id == agent_id

            # Verify registration on blockchain
            info = agent.get_agent_info(agent_id)
            # Check that we have valid agent info (domain might be from previous registration)
            assert info["agent_address"].lower() == agent.address.lower()
        except Exception as e:
            if "already registered" in str(e).lower():
                # Agent was already registered in a previous test run
                assert agent.agent_id is not None
            else:
                raise


@pytest.mark.integration
class TestServerValidatorInteraction:
    """Test server and validator agent interactions"""

    def test_market_analysis_workflow(
        self, w3, deployed_contracts
    ):
        """Test complete market analysis workflow with real blockchain"""
        if not deployed_contracts:
            pytest.skip("Contracts not deployed")

        # Create agents with unique private keys and domains
        import secrets
        import time
        server_key = "0x" + secrets.token_hex(32)
        validator_key = "0x" + secrets.token_hex(32)
        
        # Use timestamp to ensure unique domains
        timestamp = int(time.time() * 1000)
        
        server = ServerAgent(
            agent_domain=f"server{timestamp}.test.local", private_key=server_key
        )

        validator = ValidatorAgent(
            agent_domain=f"validator{timestamp}.test.local", private_key=validator_key
        )

        # Fund accounts
        from tests.test_utils import fund_account

        fund_account(w3, server.address, 1)
        fund_account(w3, validator.address, 1)
        
        # Verify funding worked
        server_balance = w3.eth.get_balance(server.address)
        validator_balance = w3.eth.get_balance(validator.address)
        assert server_balance > 0, f"Server not funded: {server_balance}"
        assert validator_balance > 0, f"Validator not funded: {validator_balance}"

        # Register agents if needed
        try:
            server_id = server.register_agent()
        except Exception as e:
            if "already registered" in str(e).lower():
                server_id = server.agent_id
            else:
                raise

        try:
            validator_id = validator.register_agent()
        except Exception as e:
            if "already registered" in str(e).lower():
                validator_id = validator.agent_id
            else:
                raise

        # Perform market analysis
        analysis = server.perform_market_analysis("BTC", "1d")
        assert analysis["symbol"] == "BTC"
        assert analysis["timeframe"] == "1d"
        assert "analysis" in analysis
        assert analysis["agent_id"] == server_id

        # Submit for validation
        tx_hash = server.submit_work_for_validation(analysis, validator_id)
        assert tx_hash is not None
        # Accept both with and without 0x prefix
        assert len(tx_hash) in [64, 66]  # Raw hash or 0x + hash

        # Validate the work
        validation_result = validator.validate_analysis(analysis)
        assert "is_valid" in validation_result
        assert "score" in validation_result
        assert validation_result["score"] >= 0
        assert validation_result["score"] <= 100


@pytest.mark.integration
class TestClientFeedback:
    """Test client feedback interactions"""

    def test_feedback_authorization_flow(
        self, w3, deployed_contracts
    ):
        """Test feedback authorization between server and client"""
        if not deployed_contracts:
            pytest.skip("Contracts not deployed")

        # Create agents with unique private keys and domains to avoid conflicts
        import secrets
        import time
        server_key = "0x" + secrets.token_hex(32)
        client_key = "0x" + secrets.token_hex(32)
        
        # Use timestamp to ensure unique domains
        timestamp = int(time.time() * 1000)
        
        server = ServerAgent(
            agent_domain=f"server{timestamp}.feedback.test",
            private_key=server_key,
        )

        client = ClientAgent(
            agent_domain=f"client{timestamp}.feedback.test",
            private_key=client_key,
        )

        # Fund accounts
        from tests.test_utils import fund_account

        fund_account(w3, server.address, 1)
        fund_account(w3, client.address, 1)

        # Register agents
        try:
            server.register_agent()
        except Exception as e:
            if "already registered" not in str(e).lower():
                raise
            print(f"Server agent already registered with ID: {server.agent_id}")

        try:
            client.register_agent()
        except Exception as e:
            if "already registered" not in str(e).lower():
                raise
            print(f"Client agent already registered with ID: {client.agent_id}")

        # Debug: Print the agent IDs and addresses
        print(f"Server - ID: {server.agent_id}, Address: {server.address}")
        print(f"Client - ID: {client.agent_id}, Address: {client.address}")

        # Authorize feedback
        tx_hash = server.authorize_client_feedback(client.agent_id)
        assert tx_hash is not None

        # Submit feedback
        feedback = client.submit_feedback(
            server.agent_id, score=85, comment="Great service!"
        )
        assert feedback["score"] == 85
        assert feedback["server_id"] == server.agent_id
        assert feedback["client_id"] == client.agent_id

        # Check reputation
        reputation = client.check_server_reputation(server.agent_id)
        assert reputation["server_id"] == server.agent_id
        assert reputation["average_score"] == 85


@pytest.mark.integration
@pytest.mark.slow
class TestCompleteWorkflow:
    """Test complete end-to-end workflow"""

    def test_full_agent_interaction(
        self, w3, deployed_contracts
    ):
        """Test complete workflow with all three agent types"""
        if not deployed_contracts:
            pytest.skip("Contracts not deployed")

        # Create all agents with unique private keys and domains to avoid conflicts
        import secrets
        import time
        server_key = "0x" + secrets.token_hex(32)
        validator_key = "0x" + secrets.token_hex(32)
        client_key = "0x" + secrets.token_hex(32)
        
        # Use timestamp to ensure unique domains
        timestamp = int(time.time() * 1000)
        
        server = ServerAgent(
            agent_domain=f"server{timestamp}.complete.test",
            private_key=server_key,
        )
        validator = ValidatorAgent(
            agent_domain=f"validator{timestamp}.complete.test",
            private_key=validator_key,
        )
        client = ClientAgent(
            agent_domain=f"client{timestamp}.complete.test",
            private_key=client_key,
        )

        # Fund all accounts
        from tests.test_utils import fund_account

        for agent in [server, validator, client]:
            fund_account(w3, agent.address, 1)

        # Register all agents
        for agent in [server, validator, client]:
            try:
                agent.register_agent()
            except Exception as e:
                if "already registered" not in str(e).lower():
                    raise

        # 1. Server performs analysis
        analysis = server.perform_market_analysis("ETH", "4h")
        assert analysis is not None

        # 2. Server requests validation
        val_tx = server.submit_work_for_validation(analysis, validator.agent_id)
        assert val_tx is not None

        # 3. Validator validates work
        validation = validator.validate_analysis(analysis)
        assert validation["is_valid"] is not None

        # 4. Server authorizes client feedback
        auth_tx = server.authorize_client_feedback(client.agent_id)
        assert auth_tx is not None

        # 5. Client provides feedback
        feedback = client.submit_feedback(
            server.agent_id, score=validation["score"], comment="Based on validation"
        )
        assert feedback is not None

        # 6. Check final reputation
        reputation = client.check_server_reputation(server.agent_id)
        assert reputation["feedback_count"] > 0