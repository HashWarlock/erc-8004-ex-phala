"""
Integration tests for dstack TEE simulator using Python SDK

These tests verify TEE functionality including key generation
and remote attestation using the local simulator via the dstack SDK.
"""

import os
import pytest
from typing import Dict, Any

# Import dstack SDK
try:
    from dstack_sdk import DstackClient
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False


@pytest.fixture(scope="module")
def tee_client():
    """Create TEE client connected to simulator"""
    if not SDK_AVAILABLE:
        pytest.skip("dstack-sdk not installed. Run: pip install dstack-sdk")
    
    # Get socket path from environment or use default
    socket_path = os.environ.get('DSTACK_SIMULATOR_ENDPOINT')
    if not socket_path:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        socket_path = os.path.join(project_root, '.dstack', 'sdk', 'simulator', 'tappd.sock')
    
    # Check if socket exists
    if not os.path.exists(socket_path):
        pytest.skip(f"TEE simulator socket not found at {socket_path}. Run 'make tee-start' first.")
    
    try:
        # DstackClient handles Unix sockets directly
        client = DstackClient(endpoint=socket_path)
        # Test connection with info call
        client.info()
        return client
    except Exception as e:
        pytest.skip(f"Cannot connect to TEE simulator: {e}")


@pytest.mark.integration
class TestTEESimulator:
    """Test TEE simulator functionality using dstack SDK"""
    
    def test_tee_info(self, tee_client):
        """Test retrieving TEE base image information"""
        info = tee_client.info()
        
        assert info is not None
        assert hasattr(info, 'app_id')
        assert hasattr(info, 'instance_id')
        
        # Verify TCB info exists
        assert hasattr(info, 'tcb_info')
        if info.tcb_info:
            assert hasattr(info.tcb_info, 'mrtd')
    
    def test_ecdsa_key_derivation(self, tee_client):
        """Test secp256k1 key derivation for blockchain applications"""
        unique_id = "test-key-integration"
        
        # Get key (returns deterministic secp256k1 key)
        key_result = tee_client.get_key(unique_id)
        
        assert key_result is not None
        assert hasattr(key_result, 'key')
        assert hasattr(key_result, 'signature_chain')
        
        # Verify key is a hex string (32-byte secp256k1 private key)
        assert isinstance(key_result.key, str)
        assert len(key_result.key) == 64  # 32 bytes as hex = 64 chars
        
        # Verify signature chain exists for authenticity
        assert key_result.signature_chain
        assert isinstance(key_result.signature_chain, list)
        assert len(key_result.signature_chain) > 0
    
    def test_multiple_key_derivation(self, tee_client):
        """Test that different IDs produce different keys"""
        keys = []
        
        for i in range(3):
            unique_id = f"test-multi-key-{i}"
            key_result = tee_client.get_key(unique_id)
            
            assert key_result is not None
            assert hasattr(key_result, 'key')
            
            # Store key for comparison
            keys.append(key_result.key)
        
        # Verify all keys are unique
        assert len(set(keys)) == len(keys), "Keys should be unique for different IDs"
    
    def test_tdx_quote_generation(self, tee_client):
        """Test TDX quote generation for remote attestation"""
        # Data to be attested (must be bytes, max 64 bytes)
        attestation_data = b"test-attestation-data"
        
        # Generate TDX quote
        quote_result = tee_client.get_quote(attestation_data)
        
        assert quote_result is not None
        assert hasattr(quote_result, 'quote')
        
        # Verify quote is in hex format and has expected length
        assert isinstance(quote_result.quote, str)
        assert len(quote_result.quote) > 100  # TDX quotes are typically large
        
        # Verify it's valid hex
        try:
            bytes.fromhex(quote_result.quote)
        except ValueError:
            pytest.fail("Quote is not valid hex format")
    
    def test_quote_with_different_data(self, tee_client):
        """Test that different data produces different quotes"""
        quotes = []
        test_data = [
            "data1",
            "data2",
            "completely-different"
        ]
        
        for data in test_data:
            quote_result = tee_client.get_quote(data.encode())
            assert quote_result is not None
            quotes.append(quote_result.quote)
        
        # Verify quotes are different for different input data
        assert len(set(quotes)) == len(quotes), "Quotes should differ for different data"
    
    def test_key_derivation_consistency(self, tee_client):
        """Test that same ID produces same key (deterministic)"""
        unique_id = "test-consistency"
        
        # Derive key twice with same ID
        key1 = tee_client.get_key(unique_id)
        key2 = tee_client.get_key(unique_id)
        
        # The private key should be deterministic for the same ID
        assert key1.key == key2.key, "Same ID should produce same key"
        
        # Signature chains should also be consistent for the same key
        assert key1.signature_chain == key2.signature_chain, "Same ID should produce same signatures"
    
    def test_quote_with_public_key_attestation(self, tee_client):
        """Test remote attestation with public key as report data"""
        # First derive a key
        unique_id = "test-attestation-key"
        key_result = tee_client.get_key(unique_id)
        
        # Extract public key from certificate (in real scenario)
        # For now, use the unique_id as attestation data
        attestation_data = f"pubkey:{unique_id}"
        
        # Generate quote with public key data
        quote_result = tee_client.get_quote(attestation_data.encode())
        
        assert quote_result is not None
        assert hasattr(quote_result, 'quote')
        assert len(quote_result.quote) > 0
        
        # In production, this quote would be sent to a verifier
        # who can verify the TEE's authenticity and the attested public key