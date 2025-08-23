"""
Pytest configuration and shared fixtures for all tests

This module provides common fixtures and configuration for the test suite.
"""

import pytest
import json
import os
from web3 import Web3
from typing import Dict, Any

# Test configuration
TEST_RPC_URL = os.getenv('TEST_RPC_URL', 'http://127.0.0.1:8545')

# Anvil test accounts (deterministic)
TEST_ACCOUNTS = [
    {
        'address': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
        'private_key': '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80',
        'name': 'Deployer'
    },
    {
        'address': '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
        'private_key': '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d',
        'name': 'Alice'
    },
    {
        'address': '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
        'private_key': '0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a',
        'name': 'Bob'
    },
    {
        'address': '0x90F79bf6EB2c4f870365E785982E1f101E93b906',
        'private_key': '0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6',
        'name': 'Charlie'
    }
]


@pytest.fixture(scope="session")
def w3():
    """Web3 instance connected to test blockchain"""
    web3 = Web3(Web3.HTTPProvider(TEST_RPC_URL))
    
    if not web3.is_connected():
        pytest.skip(f"Cannot connect to test blockchain at {TEST_RPC_URL}")
    
    return web3


@pytest.fixture(scope="session")
def deployed_contracts():
    """Load deployed contract addresses"""
    contracts_file = 'deployed_contracts.json'
    
    if not os.path.exists(contracts_file):
        pytest.skip(f"Contracts not deployed. Run 'make deploy' first.")
    
    with open(contracts_file, 'r') as f:
        return json.load(f)['contracts']


@pytest.fixture(scope="session")
def contract_abis():
    """Load contract ABIs from compiled artifacts"""
    abis = {}
    contracts = ['IdentityRegistry', 'ReputationRegistry', 'ValidationRegistry']
    
    for contract_name in contracts:
        abi_path = f'contracts/out/{contract_name}.sol/{contract_name}.json'
        
        if not os.path.exists(abi_path):
            pytest.skip(f"Contract ABIs not found. Run 'make build' first.")
        
        with open(abi_path, 'r') as f:
            abis[contract_name] = json.load(f)['abi']
    
    return abis


@pytest.fixture
def test_accounts():
    """Test accounts with private keys"""
    return TEST_ACCOUNTS


@pytest.fixture
def alice_account():
    """Alice test account"""
    return TEST_ACCOUNTS[1]


@pytest.fixture
def bob_account():
    """Bob test account"""
    return TEST_ACCOUNTS[2]


@pytest.fixture
def charlie_account():
    """Charlie test account"""
    return TEST_ACCOUNTS[3]


@pytest.fixture
def sample_market_analysis():
    """Sample market analysis data for testing"""
    return {
        "symbol": "ETH",
        "timeframe": "4h",
        "timestamp": 1234567890,
        "agent_id": 999,
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


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Ensure test environment is properly set up"""
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("validations", exist_ok=True)
    
    yield
    
    # Cleanup can be added here if needed


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests that don't require blockchain"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests requiring blockchain"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests for complete workflows"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take more than 5 seconds"
    )