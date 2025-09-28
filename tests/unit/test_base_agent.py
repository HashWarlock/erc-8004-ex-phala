"""Unit tests for BaseAgent class."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.agent.base import BaseAgent, AgentConfig, AgentRole, RegistryAddresses


class TestAgent(BaseAgent):
    """Test implementation of BaseAgent."""

    async def process_task(self, task_data):
        """Simple task processing for testing."""
        return {
            'status': 'completed',
            'data': task_data,
            'processed_at': datetime.utcnow().isoformat()
        }


class TestBaseAgent:
    """Test suite for BaseAgent functionality."""

    @pytest.fixture
    def agent_config(self):
        """Create test agent configuration."""
        return AgentConfig(
            domain="test.example.com",
            salt="test-salt-123",
            role=AgentRole.SERVER,
            rpc_url="https://sepolia.base.org",
            chain_id=84532,
            use_tee_auth=False,
            private_key="0x" + "1" * 64
        )

    @pytest.fixture
    def registry_addresses(self):
        """Create test registry addresses."""
        return RegistryAddresses(
            identity="0x000c5A70B7269c5eD4238DcC6576e598614d3f70",
            reputation="0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde",
            validation="0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d",
            tee_verifier="0x1b841e88ba786027f39ecf9Cd160176b22E3603c"
        )

    @pytest.fixture
    def test_agent(self, agent_config, registry_addresses):
        """Create test agent instance."""
        return TestAgent(agent_config, registry_addresses)

    def test_agent_initialization(self, test_agent, agent_config):
        """Test agent is properly initialized."""
        assert test_agent.config == agent_config
        assert test_agent.agent_id is None
        assert test_agent.plugins == {}
        assert test_agent.config.role == AgentRole.SERVER

    def test_agent_card_creation(self, test_agent):
        """Test agent card generation."""
        card = test_agent._create_agent_card()

        assert card['domain'] == "test.example.com"
        assert card['role'] == "server"
        assert 'address' in card
        assert 'metadata' in card
        assert card['metadata']['version'] == "1.0.0"

    @pytest.mark.asyncio
    async def test_process_task(self, test_agent):
        """Test task processing."""
        task_data = {
            'task_id': 'test_001',
            'query': 'test query',
            'data': {'key': 'value'}
        }

        result = await test_agent.process_task(task_data)

        assert result['status'] == 'completed'
        assert result['data'] == task_data
        assert 'processed_at' in result

    @pytest.mark.asyncio
    async def test_register_agent(self, test_agent):
        """Test agent registration."""
        # Mock registry client
        mock_registry = AsyncMock()
        mock_registry.register_agent.return_value = 42
        test_agent.registry_client = mock_registry

        # Register agent
        agent_id = await test_agent.register()

        assert agent_id == 42
        assert test_agent.agent_id == 42
        mock_registry.register_agent.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_attestation_without_tee(self, test_agent):
        """Test attestation generation without TEE."""
        test_agent.config.use_tee_auth = False

        attestation = await test_agent.get_attestation()

        assert attestation['mode'] == 'development'
        assert attestation['quote'] == b'mock_quote_development_mode'
        assert 'timestamp' in attestation

    @pytest.mark.asyncio
    async def test_get_attestation_with_tee(self, test_agent):
        """Test attestation generation with TEE."""
        test_agent.config.use_tee_auth = True

        # Mock TEE authenticator
        mock_tee = AsyncMock()
        mock_tee.get_attestation.return_value = {
            'quote': b'real_tee_quote',
            'event_log': b'event_log_data',
            'timestamp': datetime.utcnow().isoformat()
        }
        test_agent.tee_auth = mock_tee

        attestation = await test_agent.get_attestation()

        assert attestation['quote'] == b'real_tee_quote'
        assert attestation['event_log'] == b'event_log_data'
        mock_tee.get_attestation.assert_called_once()

    @pytest.mark.asyncio
    async def test_sign_message(self, test_agent):
        """Test message signing."""
        # Mock signer
        mock_signer = Mock()
        mock_signer.sign_typed_data.return_value = "0xsignature123"
        test_agent.signer = mock_signer

        message = {'type': 'TestMessage', 'content': 'Hello World'}
        signature = await test_agent.sign_message(message)

        assert signature == "0xsignature123"
        mock_signer.sign_typed_data.assert_called_once_with(message, test_agent.private_key)

    def test_plugin_management(self, test_agent):
        """Test plugin add/get functionality."""
        # Add plugin
        mock_plugin = Mock()
        test_agent.add_plugin('test_plugin', mock_plugin)

        assert 'test_plugin' in test_agent.plugins
        assert test_agent.get_plugin('test_plugin') == mock_plugin

        # Get non-existent plugin
        assert test_agent.get_plugin('non_existent') is None

    @pytest.mark.asyncio
    async def test_error_handling_in_registration(self, test_agent):
        """Test error handling during registration."""
        # Mock registry client to raise error
        mock_registry = AsyncMock()
        mock_registry.register_agent.side_effect = Exception("Registration failed")
        test_agent.registry_client = mock_registry

        with pytest.raises(Exception) as exc_info:
            await test_agent.register()

        assert "Registration failed" in str(exc_info.value)

    def test_agent_role_validation(self, agent_config, registry_addresses):
        """Test different agent roles."""
        # Test SERVER role
        server_config = agent_config
        server_config.role = AgentRole.SERVER
        server_agent = TestAgent(server_config, registry_addresses)
        assert server_agent.config.role == AgentRole.SERVER

        # Test VALIDATOR role
        validator_config = agent_config
        validator_config.role = AgentRole.VALIDATOR
        validator_agent = TestAgent(validator_config, registry_addresses)
        assert validator_agent.config.role == AgentRole.VALIDATOR

        # Test CLIENT role
        client_config = agent_config
        client_config.role = AgentRole.CLIENT
        client_agent = TestAgent(client_config, registry_addresses)
        assert client_agent.config.role == AgentRole.CLIENT

    @pytest.mark.asyncio
    async def test_concurrent_task_processing(self, test_agent):
        """Test concurrent task processing."""
        tasks = [
            {'task_id': f'task_{i}', 'data': i}
            for i in range(10)
        ]

        # Process tasks concurrently
        results = await asyncio.gather(*[
            test_agent.process_task(task) for task in tasks
        ])

        assert len(results) == 10
        for i, result in enumerate(results):
            assert result['status'] == 'completed'
            assert result['data']['task_id'] == f'task_{i}'

    def test_config_validation(self):
        """Test configuration validation."""
        # Test missing required fields
        with pytest.raises(TypeError):
            AgentConfig()  # Missing required fields

        # Test valid configuration
        config = AgentConfig(
            domain="test.com",
            salt="salt",
            role=AgentRole.SERVER,
            rpc_url="https://rpc.url",
            chain_id=1
        )
        assert config.domain == "test.com"
        assert config.use_tee_auth is False  # Default value

    @pytest.mark.asyncio
    async def test_lifecycle_methods(self, test_agent):
        """Test agent lifecycle methods."""
        # Mock dependencies
        mock_registry = AsyncMock()
        mock_registry.register_agent.return_value = 1
        test_agent.registry_client = mock_registry

        # Full lifecycle
        # 1. Register
        await test_agent.register()
        assert test_agent.agent_id == 1

        # 2. Process tasks
        task_result = await test_agent.process_task({'data': 'test'})
        assert task_result['status'] == 'completed'

        # 3. Get attestation
        attestation = await test_agent.get_attestation()
        assert 'quote' in attestation

        # 4. Sign message
        mock_signer = Mock()
        mock_signer.sign_typed_data.return_value = "0xsig"
        test_agent.signer = mock_signer
        signature = await test_agent.sign_message({'msg': 'test'})
        assert signature == "0xsig"


class TestAgentFactory:
    """Test agent factory functionality."""

    @pytest.mark.asyncio
    async def test_create_agent_from_config(self):
        """Test creating agent from configuration."""
        config = AgentConfig(
            domain="factory.test",
            salt="factory-salt",
            role=AgentRole.SERVER,
            rpc_url="https://test.rpc",
            chain_id=1,
            use_tee_auth=False
        )

        registries = RegistryAddresses(
            identity="0x1234",
            reputation="0x5678",
            validation="0x9abc",
            tee_verifier="0xdef0"
        )

        agent = TestAgent(config, registries)
        assert agent.config.domain == "factory.test"
        assert isinstance(agent, BaseAgent)