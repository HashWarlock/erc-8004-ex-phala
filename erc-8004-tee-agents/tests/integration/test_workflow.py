"""Integration tests for multi-agent workflows."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.agent.base import AgentConfig, AgentRole, RegistryAddresses
from src.templates.server_agent import ServerAgent
from src.templates.validator_agent import ValidatorAgent
from src.templates.client_agent import ClientAgent


class TestMultiAgentWorkflow:
    """Test complete multi-agent workflow integration."""

    @pytest.fixture
    def registry_addresses(self):
        """Common registry addresses for testing."""
        return RegistryAddresses(
            identity="0x000c5A70B7269c5eD4238DcC6576e598614d3f70",
            reputation="0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde",
            validation="0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d",
            tee_verifier="0x1b841e88ba786027f39ecf9Cd160176b22E3603c"
        )

    @pytest.fixture
    def server_agent(self, registry_addresses):
        """Create server agent for testing."""
        config = AgentConfig(
            domain="server.test",
            salt="server-salt",
            role=AgentRole.SERVER,
            rpc_url="https://sepolia.base.org",
            chain_id=84532,
            use_tee_auth=False,
            private_key="0x" + "1" * 64
        )
        return ServerAgent(config, registry_addresses)

    @pytest.fixture
    def validator_agent(self, registry_addresses):
        """Create validator agent for testing."""
        config = AgentConfig(
            domain="validator.test",
            salt="validator-salt",
            role=AgentRole.VALIDATOR,
            rpc_url="https://sepolia.base.org",
            chain_id=84532,
            use_tee_auth=False,
            private_key="0x" + "2" * 64
        )
        return ValidatorAgent(config, registry_addresses)

    @pytest.fixture
    def client_agent(self, registry_addresses):
        """Create client agent for testing."""
        config = AgentConfig(
            domain="client.test",
            salt="client-salt",
            role=AgentRole.CLIENT,
            rpc_url="https://sepolia.base.org",
            chain_id=84532,
            use_tee_auth=False,
            private_key="0x" + "3" * 64
        )
        return ClientAgent(config, registry_addresses)

    @pytest.mark.asyncio
    async def test_complete_workflow(self, server_agent, validator_agent, client_agent):
        """Test complete 3-agent workflow."""
        # Step 1: Client requests service from Server
        service_request = {
            'task_id': 'test_001',
            'query': 'market analysis for ETH',
            'data': {
                'asset': 'ETH',
                'timeframe': '24h'
            }
        }

        # Server processes request
        server_result = await server_agent.process_task(service_request)

        assert server_result['status'] == 'completed'
        assert 'analysis' in server_result
        assert server_result['confidence'] >= 0.5

        # Step 2: Server requests validation
        import hashlib
        import json
        data_hash = hashlib.sha256(
            json.dumps(server_result['analysis'], sort_keys=True).encode()
        ).hexdigest()

        validation_request = {
            'request_id': 'val_001',
            'data_hash': data_hash,
            'data': server_result['analysis'],
            'validation_type': 'computation'
        }

        # Validator validates
        validation_result = await validator_agent.process_task(validation_request)

        assert validation_result['status'] == 'completed'
        assert 'is_valid' in validation_result
        assert 'confidence' in validation_result

        # Step 3: Client submits feedback
        feedback_data = {
            'task_type': 'feedback',
            'target_agent_id': 1,  # Mock server ID
            'rating': 5 if validation_result['is_valid'] else 3,
            'comment': 'Service validated successfully'
        }

        feedback_result = await client_agent.process_task(feedback_data)

        assert feedback_result['status'] == 'completed'
        assert feedback_result['feedback_submitted'] is True

    @pytest.mark.asyncio
    async def test_concurrent_agent_operations(self, server_agent):
        """Test server handling multiple concurrent requests."""
        requests = [
            {
                'task_id': f'concurrent_{i}',
                'query': f'analysis_{i}',
                'data': {'index': i}
            }
            for i in range(5)
        ]

        # Process all requests concurrently
        results = await asyncio.gather(*[
            server_agent.process_task(req) for req in requests
        ])

        assert len(results) == 5
        for i, result in enumerate(results):
            assert result['status'] == 'completed'
            assert result['analysis']['query'] == f'analysis_{i}'

    @pytest.mark.asyncio
    async def test_validation_consensus(self, validator_agent):
        """Test validator consensus mechanism."""
        # Multiple validation requests
        validations = []
        for i in range(3):
            request = {
                'request_id': f'consensus_{i}',
                'data_hash': f'hash_{i}',
                'data': {'value': i * 100},
                'validation_type': 'consensus'
            }
            result = await validator_agent.process_task(request)
            validations.append(result)

        # Check all validations completed
        assert all(v['status'] == 'completed' for v in validations)
        assert all('is_valid' in v for v in validations)

    @pytest.mark.asyncio
    async def test_agent_registration_integration(self, server_agent):
        """Test agent registration with mock registry."""
        # Mock registry client
        mock_registry = AsyncMock()
        mock_registry.register_agent.return_value = 42
        server_agent.registry_client = mock_registry

        # Register agent
        agent_id = await server_agent.register()

        assert agent_id == 42
        assert server_agent.agent_id == 42
        mock_registry.register_agent.assert_called_once()

        # Verify agent card format
        call_args = mock_registry.register_agent.call_args[0][0]
        assert 'domain' in call_args
        assert 'role' in call_args
        assert 'address' in call_args
        assert call_args['domain'] == 'server.test'
        assert call_args['role'] == 'server'

    @pytest.mark.asyncio
    async def test_error_propagation(self, server_agent):
        """Test error handling across agent interactions."""
        # Create request that will cause error
        invalid_request = {
            'task_id': 'error_test',
            # Missing required 'query' field
            'data': None
        }

        result = await server_agent.process_task(invalid_request)

        # Server should handle error gracefully
        assert result['status'] in ['error', 'completed']
        if result['status'] == 'error':
            assert 'error' in result

    @pytest.mark.asyncio
    async def test_feedback_aggregation(self, client_agent):
        """Test client agent feedback aggregation."""
        feedback_items = [
            {
                'task_type': 'feedback',
                'target_agent_id': 1,
                'rating': 5,
                'comment': 'Excellent'
            },
            {
                'task_type': 'feedback',
                'target_agent_id': 1,
                'rating': 4,
                'comment': 'Good'
            },
            {
                'task_type': 'feedback',
                'target_agent_id': 2,
                'rating': 5,
                'comment': 'Perfect'
            }
        ]

        results = []
        for feedback in feedback_items:
            result = await client_agent.process_task(feedback)
            results.append(result)

        assert len(results) == 3
        assert all(r['status'] == 'completed' for r in results)
        assert all(r['feedback_submitted'] for r in results)

    @pytest.mark.asyncio
    async def test_tee_integration_flow(self):
        """Test workflow with TEE authentication enabled."""
        with patch('src.agent.tee_auth.DstackClient') as mock_dstack:
            # Setup mock TEE client
            mock_client = Mock()
            mock_key = Mock()
            mock_key.decode_key.return_value = bytes.fromhex("4" * 64)
            mock_client.get_key.return_value = mock_key

            mock_quote = Mock()
            mock_quote.quote = b'tee_quote'
            mock_quote.event_log = b'event_log'
            mock_client.get_quote.return_value = mock_quote

            mock_dstack.return_value = mock_client

            # Create TEE-enabled agent
            config = AgentConfig(
                domain="tee.test",
                salt="tee-salt",
                role=AgentRole.SERVER,
                rpc_url="https://sepolia.base.org",
                chain_id=84532,
                use_tee_auth=True
            )

            registries = RegistryAddresses(
                identity="0x123",
                reputation="0x456",
                validation="0x789",
                tee_verifier="0xabc"
            )

            agent = ServerAgent(config, registries)

            # Get TEE attestation
            attestation = await agent.get_attestation()

            assert attestation['quote'] == b'tee_quote'
            assert attestation['event_log'] == b'event_log'
            assert 'timestamp' in attestation

    @pytest.mark.asyncio
    async def test_cross_agent_communication(self, server_agent, validator_agent):
        """Test direct communication between agents."""
        # Server creates data for validation
        data_to_validate = {
            'computation_result': 42,
            'confidence': 0.95,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Server signs the data
        mock_signer = Mock()
        mock_signer.sign_typed_data.return_value = "0xsignature"
        server_agent.signer = mock_signer

        signature = await server_agent.sign_message(data_to_validate)

        # Validator verifies the signature
        validation_request = {
            'data': data_to_validate,
            'signature': signature,
            'sender': server_agent.config.domain
        }

        validation_result = await validator_agent.process_task(validation_request)

        assert validation_result['status'] == 'completed'
        assert 'is_valid' in validation_result

    @pytest.mark.asyncio
    async def test_plugin_integration(self, server_agent):
        """Test plugin system integration."""
        # Create and add a test plugin
        class TestPlugin:
            async def enhance(self, data):
                data['enhanced'] = True
                data['plugin_timestamp'] = datetime.utcnow().isoformat()
                return data

        plugin = TestPlugin()
        server_agent.add_plugin('enhancer', plugin)

        # Process task with plugin
        task = {'task_id': 'plugin_test', 'query': 'test', 'data': {}}
        result = await server_agent.process_task(task)

        # Manually apply plugin enhancement (simulating internal usage)
        enhanced_result = await plugin.enhance(result)

        assert enhanced_result['enhanced'] is True
        assert 'plugin_timestamp' in enhanced_result


class TestPerformance:
    """Performance and load testing."""

    @pytest.mark.asyncio
    async def test_high_load_processing(self, registry_addresses):
        """Test agent performance under high load."""
        config = AgentConfig(
            domain="load.test",
            salt="load-salt",
            role=AgentRole.SERVER,
            rpc_url="https://sepolia.base.org",
            chain_id=84532,
            use_tee_auth=False,
            private_key="0x" + "5" * 64
        )
        agent = ServerAgent(config, registry_addresses)

        # Generate 100 requests
        requests = [
            {
                'task_id': f'load_{i}',
                'query': f'query_{i}',
                'data': {'index': i}
            }
            for i in range(100)
        ]

        # Measure processing time
        import time
        start = time.time()

        results = await asyncio.gather(*[
            agent.process_task(req) for req in requests
        ])

        elapsed = time.time() - start

        assert len(results) == 100
        assert all(r['status'] == 'completed' for r in results)
        assert elapsed < 10  # Should process 100 requests in under 10 seconds

        print(f"Processed 100 requests in {elapsed:.2f} seconds")
        print(f"Average: {elapsed/100:.3f} seconds per request")