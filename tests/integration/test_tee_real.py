"""
TEE integration tests using real TEE simulator

These tests verify TEE functionality against the actual dstack simulator
without any mocking.
"""

import pytest
import os
from agents.tee_base_agent import ERC8004TEEAgent
from agents.tee_server_agent import TEEServerAgent
from agents.tee_validator_agent import TEEValidatorAgent
from agents.tee_client_agent import TEEClientAgent


@pytest.mark.integration
class TestTEEKeyDerivation:
    """Test TEE key derivation with real simulator"""

    def test_deterministic_key_derivation(self, tee_client, blockchain_snapshot):
        """Test that TEE derives keys deterministically"""
        # Derive key twice with same parameters
        path1 = "test/agent/path"
        purpose1 = "test-purpose"

        key1 = tee_client.get_key(path1, purpose1)
        key2 = tee_client.get_key(path1, purpose1)

        # Keys should be identical
        if hasattr(key1, "key"):
            assert key1.key == key2.key
        else:
            assert key1 == key2

        # Different path should give different key
        path2 = "test/agent/different"
        key3 = tee_client.get_key(path2, purpose1)

        if hasattr(key3, "key"):
            assert key3.key != key1.key
        else:
            assert key3 != key1

    def test_tee_attestation_generation(self, tee_client, blockchain_snapshot):
        """Test TEE attestation quote generation"""
        test_data = b"test attestation data"

        # Get attestation quote
        quote = tee_client.get_quote(test_data[:64])  # Max 64 bytes

        # Verify quote structure
        assert quote is not None
        if hasattr(quote, "quote"):
            assert quote.quote is not None
            # Quote should be non-empty
            assert len(str(quote.quote)) > 0


@pytest.mark.integration
class TestTEEAgentInitialization:
    """Test TEE agent initialization with real simulator"""

    def test_tee_agent_creation(self, w3, deployed_contracts, tee_client, blockchain_snapshot):
        """Test creating a TEE-enabled agent"""
        if not deployed_contracts:
            pytest.skip("Contracts not deployed")

        # Create TEE agent
        agent = ERC8004TEEAgent(
            agent_domain="tee.test.local",
            salt="unique-salt-123",
            tee_endpoint=os.getenv("DSTACK_SIMULATOR_ENDPOINT"),
        )

        # Verify agent properties
        assert agent.agent_domain == "tee.test.local"
        assert agent.salt == "unique-salt-123"
        assert agent.address is not None
        assert agent.private_key is not None

        # Verify TEE client is connected
        assert agent.tee_client is not None

        # Test attestation
        attestation = agent.get_attestation()
        assert attestation is not None
        assert "attestation_data" in attestation
        assert attestation["attestation_data"]["agent_domain"] == "tee.test.local"

    def test_tee_derived_keys_are_deterministic(self, w3, deployed_contracts, blockchain_snapshot):
        """Test that TEE agents derive same key from same salt"""
        if not deployed_contracts:
            pytest.skip("Contracts not deployed")

        # Create two agents with same domain and salt
        agent1 = ERC8004TEEAgent(
            agent_domain="deterministic.test.local",
            salt="same-salt-456",
            tee_endpoint=os.getenv("DSTACK_SIMULATOR_ENDPOINT"),
        )

        agent2 = ERC8004TEEAgent(
            agent_domain="deterministic.test.local",
            salt="same-salt-456",
            tee_endpoint=os.getenv("DSTACK_SIMULATOR_ENDPOINT"),
        )

        # They should have the same address
        assert agent1.address == agent2.address
        assert agent1.private_key == agent2.private_key

        # Different salt should give different address
        agent3 = ERC8004TEEAgent(
            agent_domain="deterministic.test.local",
            salt="different-salt-789",
            tee_endpoint=os.getenv("DSTACK_SIMULATOR_ENDPOINT"),
        )

        assert agent3.address != agent1.address
        assert agent3.private_key != agent1.private_key


@pytest.mark.integration
class TestTEEServerAgent:
    """Test TEE-enabled server agent"""

    def test_tee_server_with_attestation(self, w3, deployed_contracts, blockchain_snapshot):
        """Test TEE server agent provides attestation with analysis"""
        if not deployed_contracts:
            pytest.skip("Contracts not deployed")

        # Create TEE server agent with unique domain
        import time
        timestamp = str(int(time.time() * 1000))[-6:]
        server = TEEServerAgent(
            agent_domain=f"tee.server.{timestamp}.local",
            salt="server-salt-001",
            tee_endpoint=os.getenv("DSTACK_SIMULATOR_ENDPOINT"),
        )

        # Fund account
        from tests.test_utils import fund_account

        fund_account(w3, server.address, 1)

        # Register if needed
        try:
            server.register_agent()
        except Exception as e:
            if "already registered" not in str(e).lower():
                raise

        # Perform analysis
        analysis = server.perform_market_analysis("BTC", "1h")

        # Check for TEE metadata
        assert "metadata" in analysis
        metadata = analysis["metadata"]
        assert metadata.get("tee_enabled") is True

        # Get attestation
        attestation = server.get_attestation()
        assert attestation is not None
        assert "attestation_data" in attestation


@pytest.mark.integration
class TestTEEValidatorAgent:
    """Test TEE-enabled validator agent"""

    def test_tee_validator_attestation(self, w3, deployed_contracts, blockchain_snapshot):
        """Test TEE validator provides attested validation"""
        if not deployed_contracts:
            pytest.skip("Contracts not deployed")

        # Create TEE validator
        # Use unique domain to avoid conflicts
        import time
        timestamp = str(int(time.time() * 1000))[-6:]
        validator = TEEValidatorAgent(
            agent_domain=f"tee.validator.{timestamp}.local",
            salt="validator-salt-001",
            tee_endpoint=os.getenv("DSTACK_SIMULATOR_ENDPOINT"),
        )

        # Fund account
        from tests.test_utils import fund_account

        fund_account(w3, validator.address, 1)

        # Register if needed
        try:
            validator.register_agent()
        except Exception as e:
            if "already registered" not in str(e).lower():
                raise

        # Create sample analysis to validate
        analysis = {
            "symbol": "ETH",
            "timeframe": "1d",
            "analysis": "Test analysis",
            "metadata": {"tee_enabled": True},
        }

        # Validate with TEE
        validation = validator.validate_analysis(analysis)

        # Check TEE validation
        assert "validation_package" in validation
        package = validation["validation_package"]
        assert "metadata" in package
        assert package["metadata"].get("tee_validated") is True
        assert package["metadata"].get("attestation_available") is True


@pytest.mark.integration
class TestTEEClientAgent:
    """Test TEE-enabled client agent"""

    def test_tee_client_feedback_with_attestation(self, w3, deployed_contracts, blockchain_snapshot):
        """Test TEE client provides attested feedback"""
        if not deployed_contracts:
            pytest.skip("Contracts not deployed")

        # Create TEE client with unique domain
        import time
        timestamp = str(int(time.time() * 1000))[-6:]
        client = TEEClientAgent(
            agent_domain=f"tee.client.{timestamp}.local",
            salt="client-salt-001",
            tee_endpoint=os.getenv("DSTACK_SIMULATOR_ENDPOINT"),
        )

        # Fund account
        from tests.test_utils import fund_account

        fund_account(w3, client.address, 1)

        # Register if needed
        try:
            client.register_agent()
        except Exception as e:
            if "already registered" not in str(e).lower():
                raise

        # Submit feedback (to mock server ID 1)
        feedback = client.submit_feedback(1, 90, "Excellent service with TEE")

        # Check TEE attestation in feedback
        assert "tee_attestation" in feedback
        tee_info = feedback["tee_attestation"]
        assert tee_info["has_attestation"] is True
        assert tee_info["tee_endpoint"] is not None


@pytest.mark.integration
@pytest.mark.slow
class TestTEECompleteWorkflow:
    """Test complete workflow with all TEE agents"""

    def test_full_tee_workflow(self, w3, deployed_contracts, blockchain_snapshot):
        """Test complete TEE-enabled agent interaction"""
        if not deployed_contracts:
            pytest.skip("Contracts not deployed")

        # Create all TEE agents with unique domains
        import time
        timestamp = str(int(time.time() * 1000))[-6:]
        
        server = TEEServerAgent(
            agent_domain=f"workflow.server.{timestamp}.tee",
            salt="workflow-server-salt",
            tee_endpoint=os.getenv("DSTACK_SIMULATOR_ENDPOINT"),
        )

        validator = TEEValidatorAgent(
            agent_domain=f"workflow.validator.{timestamp}.tee",
            salt="workflow-validator-salt",
            tee_endpoint=os.getenv("DSTACK_SIMULATOR_ENDPOINT"),
        )

        client = TEEClientAgent(
            agent_domain=f"workflow.client.{timestamp}.tee",
            salt="workflow-client-salt",
            tee_endpoint=os.getenv("DSTACK_SIMULATOR_ENDPOINT"),
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

        # 1. Server performs TEE-attested analysis
        analysis = server.perform_market_analysis("BTC", "1d")
        assert analysis["metadata"]["tee_enabled"] is True

        # 2. Validator validates with TEE attestation
        validation = validator.validate_analysis(analysis)
        assert "validation_package" in validation
        assert validation["validation_package"]["metadata"]["tee_validated"] is True

        # 3. Client provides TEE-attested feedback
        feedback = client.submit_feedback(
            server.agent_id, validation.get("score", 85), "TEE-verified validation"
        )
        assert feedback["tee_attestation"]["has_attestation"] is True

        # All interactions were TEE-protected
        print("✅ Complete TEE workflow successful!")