"""
Unit tests for the ERC8004BaseAgent class

These tests verify the base agent functionality without requiring
blockchain connectivity.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from agents.base_agent import ERC8004BaseAgent


@pytest.mark.unit
class TestBaseAgentInitialization:
    """Test base agent initialization and configuration"""
    
    @patch('agents.base_agent.Web3')
    def test_agent_initialization(self, mock_web3):
        """Test that agent initializes with correct parameters"""
        # Setup mock
        mock_w3_instance = MagicMock()
        mock_w3_instance.is_connected.return_value = True
        mock_w3_instance.eth.account.from_key.return_value = MagicMock(
            address='0x1234567890abcdef'
        )
        mock_web3.HTTPProvider.return_value = MagicMock()
        mock_web3.return_value = mock_w3_instance
        
        # Mock contract loading
        with patch.object(ERC8004BaseAgent, '_load_contract_addresses'), \
             patch.object(ERC8004BaseAgent, '_init_contracts'), \
             patch.object(ERC8004BaseAgent, '_check_registration'):
            
            agent = ERC8004BaseAgent(
                agent_domain="test.domain.com",
                private_key="0x" + "1" * 64
            )
            
            assert agent.agent_domain == "test.domain.com"
            assert agent.private_key == "0x" + "1" * 64
            assert agent.address == '0x1234567890abcdef'
    
    @patch('agents.base_agent.Web3')
    def test_agent_fails_without_connection(self, mock_web3):
        """Test that agent raises error when blockchain is not connected"""
        # Setup mock
        mock_w3_instance = MagicMock()
        mock_w3_instance.is_connected.return_value = False
        mock_web3.HTTPProvider.return_value = MagicMock()
        mock_web3.return_value = mock_w3_instance
        
        with pytest.raises(ConnectionError, match="Failed to connect"):
            agent = ERC8004BaseAgent(
                agent_domain="test.domain.com",
                private_key="0x" + "1" * 64
            )


@pytest.mark.unit
class TestBaseAgentMethods:
    """Test base agent methods that don't require blockchain"""
    
    @patch('agents.base_agent.Web3')
    def test_get_agent_info_structure(self, mock_web3):
        """Test that get_agent_info returns correct structure"""
        # Setup mock
        mock_w3_instance = MagicMock()
        mock_w3_instance.is_connected.return_value = True
        mock_web3.return_value = mock_w3_instance
        
        with patch.object(ERC8004BaseAgent, '_load_contract_addresses'), \
             patch.object(ERC8004BaseAgent, '_init_contracts'), \
             patch.object(ERC8004BaseAgent, '_check_registration'):
            
            agent = ERC8004BaseAgent(
                agent_domain="test.domain.com",
                private_key="0x" + "1" * 64
            )
            
            # Mock the contract call
            agent.identity_registry = MagicMock()
            agent.identity_registry.functions.getAgent.return_value.call.return_value = (
                1,  # agent_id
                "test.domain.com",  # domain
                "0x1234567890abcdef"  # address
            )
            
            info = agent.get_agent_info(1)
            
            assert info['agent_id'] == 1
            assert info['agent_domain'] == "test.domain.com"
            assert info['agent_address'] == "0x1234567890abcdef"
    
    def test_contract_address_loading(self):
        """Test contract address loading from deployment file"""
        import tempfile
        import json
        
        deployment_data = {
            "contracts": {
                "IdentityRegistry": "0x111",
                "ReputationRegistry": "0x222",
                "ValidationRegistry": "0x333"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(deployment_data, f)
            temp_file = f.name
        
        # Test loading with mock agent
        with patch('agents.base_agent.Web3'), \
             patch.object(ERC8004BaseAgent, '_init_contracts'), \
             patch.object(ERC8004BaseAgent, '_check_registration'), \
             patch('builtins.open', create=True) as mock_open:
            
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(deployment_data)
            
            mock_w3 = MagicMock()
            mock_w3.is_connected.return_value = True
            
            agent = ERC8004BaseAgent.__new__(ERC8004BaseAgent)
            agent.w3 = mock_w3
            agent._load_contract_addresses()
            
            assert agent.identity_registry_address == "0x111"
            assert agent.reputation_registry_address == "0x222"
            assert agent.validation_registry_address == "0x333"