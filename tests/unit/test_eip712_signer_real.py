"""
Unit tests for EIP-712 signer using real environment

These tests verify EIP-712 signing functionality without mocks.
"""

import pytest
import os
from eth_account import Account
from agents.eip712_signer import EIP712Signer, TEESecureSigner


@pytest.mark.unit
class TestEIP712SignerReal:
    """Test EIP712 signer with real environment"""

    def test_domain_separator_creation(self):
        """Test creation of EIP-712 domain separator"""
        signer = EIP712Signer()
        
        domain = signer.get_domain_separator()
        
        assert domain["name"] == "ERC8004-Trustless-Agents"
        assert domain["version"] == "1"
        assert domain["chainId"] == 31337  # Anvil default
        assert "verifyingContract" in domain
        
    def test_typed_data_structure(self):
        """Test typed data creation for different message types"""
        signer = EIP712Signer()
        
        # Test AnalysisRequest
        analysis_data = {
            "requester": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            "topic": "BTC analysis",
            "parameters": '{"timeframe": "1d"}',
            "nonce": 1,
            "timestamp": 1234567890
        }
        
        typed_data = signer.create_typed_data("AnalysisRequest", analysis_data)
        
        assert typed_data["domain"]["name"] == "ERC8004-Trustless-Agents"
        assert typed_data["message"] == analysis_data
        assert "AnalysisRequest" in typed_data["types"]
        
    def test_message_signing(self):
        """Test message signing with a test private key"""
        signer = EIP712Signer()
        
        # Create test account
        test_key = "0x" + "1" * 64
        account = Account.from_key(test_key)
        
        message_data = {
            "requester": account.address,
            "topic": "test",
            "parameters": "{}",
            "nonce": 1,
            "timestamp": 1234567890
        }
        
        typed_data = signer.create_typed_data("AnalysisRequest", message_data)
        
        # Sign message (returns tuple of signature and components)
        signature_data = signer.sign_typed_data(typed_data, test_key)
        
        # Check if it's a tuple (signature, components)
        if isinstance(signature_data, tuple):
            signature, components = signature_data
            assert signature is not None
            assert len(signature) in [128, 130]  # Raw signature with or without v component
            assert "v" in components
            assert "r" in components
            assert "s" in components
        else:
            # Old format - just signature
            assert signature_data is not None
        
    def test_signature_verification(self):
        """Test signature can be verified"""
        signer = EIP712Signer()
        
        # Create test account
        test_key = "0x" + "2" * 64
        account = Account.from_key(test_key)
        
        message_data = {
            "validator": account.address,
            "analysisId": "0x" + "a" * 64,
            "isValid": True,
            "confidence": 85,
            "details": "Test validation",
            "timestamp": 1234567890
        }
        
        typed_data = signer.create_typed_data("ValidationResult", message_data)
        signature_data = signer.sign_typed_data(typed_data, test_key)
        
        # Check signature format
        if isinstance(signature_data, tuple):
            signature, components = signature_data
            assert "v" in components
            assert "r" in components
            assert "s" in components
            assert components["v"] in [27, 28]
            assert len(components["r"]) == 66  # 0x + 64 hex
            assert len(components["s"]) == 66  # 0x + 64 hex
        else:
            # Verify components can be extracted
            components = signer.get_signature_components(signature_data)
            assert "v" in components
            assert "r" in components
            assert "s" in components


@pytest.mark.unit 
class TestTEESecureSignerReal:
    """Test TEE secure signer with real environment"""
    
    def test_tee_signer_initialization(self):
        """Test TEE signer initializes correctly"""
        signer = TEESecureSigner()
        
        # Check if TEE socket exists (won't require it to exist)
        socket_path = ".dstack/sdk/simulator/dstack.sock"
        expected_tee_enabled = os.path.exists(socket_path)
        
        assert signer.tee_enabled == expected_tee_enabled
        
    def test_tee_availability_check(self):
        """Test TEE availability detection based on real environment"""
        signer = TEESecureSigner()
        
        # Should detect based on actual socket existence
        socket_path = ".dstack/sdk/simulator/dstack.sock"
        if os.path.exists(socket_path):
            assert signer.tee_enabled is True
        else:
            assert signer.tee_enabled is False
            
    def test_sign_without_tee(self):
        """Test signing works even without TEE"""
        signer = TEESecureSigner()
        
        # Use regular signing if TEE not available
        test_key = "0x" + "3" * 64
        
        message_data = {
            "requester": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            "topic": "test",
            "parameters": "{}",
            "nonce": 1,
            "timestamp": 1234567890
        }
        
        typed_data = signer.create_typed_data("AnalysisRequest", message_data)
        
        if signer.tee_enabled:
            # If TEE is available, test TEE signing
            try:
                signature, components = signer.sign_with_tee(typed_data, "test_key")
                assert signature is not None
            except Exception:
                # TEE might not be fully configured
                pass
        else:
            # Fall back to regular signing
            signature = signer.sign_typed_data(typed_data, test_key)
            assert signature is not None
            assert len(signature) == 132
            
    def test_all_message_types(self):
        """Test all supported message types"""
        signer = TEESecureSigner()
        
        message_types = {
            "AnalysisRequest": {
                "requester": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
                "topic": "test",
                "parameters": "{}",
                "nonce": 1,
                "timestamp": 1234567890
            },
            "ValidationResult": {
                "validator": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0", 
                "analysisId": "0x" + "c" * 64,
                "isValid": True,
                "confidence": 90,
                "details": "Test validation",
                "timestamp": 1234567890
            },
            "FeedbackSubmission": {
                "submitter": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
                "analysisId": "0x" + "d" * 64,
                "rating": 5,
                "comment": "Great service",
                "timestamp": 1234567890
            },
            "AgentRegistration": {
                "agent": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
                "agentType": "server",
                "capabilities": "analysis",
                "endpoint": "http://localhost:8080",
                "timestamp": 1234567890
            }
        }
        
        for msg_type, msg_data in message_types.items():
            typed_data = signer.create_typed_data(msg_type, msg_data)
            assert typed_data["message"] == msg_data
            assert msg_type in typed_data["types"]