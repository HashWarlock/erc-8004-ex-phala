"""Unit tests for TEE authentication module."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.agent.tee_auth import TEEAuthenticator


class TestTEEAuthenticator:
    """Test suite for TEE authentication functionality."""

    @pytest.fixture
    def tee_auth_dev(self):
        """Create TEE authenticator in development mode."""
        return TEEAuthenticator(
            domain="test.example.com",
            salt="test-salt",
            use_tee=False,
            private_key="0x" + "1" * 64
        )

    @pytest.fixture
    def tee_auth_prod(self):
        """Create TEE authenticator in production mode."""
        return TEEAuthenticator(
            domain="test.example.com",
            salt="test-salt",
            use_tee=True
        )

    def test_initialization_dev_mode(self, tee_auth_dev):
        """Test initialization in development mode."""
        assert tee_auth_dev.domain == "test.example.com"
        assert tee_auth_dev.salt == "test-salt"
        assert tee_auth_dev.use_tee is False
        assert tee_auth_dev.private_key == "0x" + "1" * 64

    def test_initialization_prod_mode(self, tee_auth_prod):
        """Test initialization in production mode."""
        assert tee_auth_prod.domain == "test.example.com"
        assert tee_auth_prod.salt == "test-salt"
        assert tee_auth_prod.use_tee is True
        assert tee_auth_prod.private_key is None

    @pytest.mark.asyncio
    async def test_derive_address_dev_mode(self, tee_auth_dev):
        """Test address derivation in development mode."""
        address = await tee_auth_dev.derive_address()

        assert address.startswith("0x")
        assert len(address) == 42
        # Same private key should always derive same address
        address2 = await tee_auth_dev.derive_address()
        assert address == address2

    @pytest.mark.asyncio
    async def test_derive_address_prod_mode(self, tee_auth_prod):
        """Test address derivation in production mode with TEE."""
        # Mock dstack client
        mock_client = Mock()
        mock_key = Mock()
        mock_key.decode_key.return_value = bytes.fromhex("1" * 64)
        mock_client.get_key.return_value = mock_key
        tee_auth_prod.tee_client = mock_client

        address = await tee_auth_prod.derive_address()

        assert address.startswith("0x")
        assert len(address) == 42
        mock_client.get_key.assert_called_once_with(
            f"wallet/erc8004-{tee_auth_prod.domain}",
            tee_auth_prod.salt
        )

    def test_create_attestation_data(self, tee_auth_dev):
        """Test attestation data creation (64 bytes requirement)."""
        # Test hash method
        data_hash = tee_auth_dev._create_attestation_data(method="hash")
        assert len(data_hash) == 64
        assert isinstance(data_hash, bytes)

        # Test structured method
        data_structured = tee_auth_dev._create_attestation_data(method="structured")
        assert len(data_structured) == 64
        assert isinstance(data_structured, bytes)

        # Test padded method
        data_padded = tee_auth_dev._create_attestation_data(method="padded")
        assert len(data_padded) == 64
        assert isinstance(data_padded, bytes)

    @pytest.mark.asyncio
    async def test_get_attestation_dev_mode(self, tee_auth_dev):
        """Test attestation generation in development mode."""
        attestation = await tee_auth_dev.get_attestation()

        assert 'quote' in attestation
        assert 'event_log' in attestation
        assert 'timestamp' in attestation
        assert attestation['quote'] == b'mock_quote_development_mode'
        assert attestation['event_log'] == b'mock_event_log'

    @pytest.mark.asyncio
    async def test_get_attestation_prod_mode(self, tee_auth_prod):
        """Test attestation generation in production mode with TEE."""
        # Mock dstack client
        mock_client = Mock()
        mock_quote_result = Mock()
        mock_quote_result.quote = b'real_tee_quote_data'
        mock_quote_result.event_log = b'real_event_log_data'
        mock_client.get_quote.return_value = mock_quote_result
        tee_auth_prod.tee_client = mock_client

        attestation = await tee_auth_prod.get_attestation()

        assert attestation['quote'] == b'real_tee_quote_data'
        assert attestation['event_log'] == b'real_event_log_data'
        assert 'timestamp' in attestation

        # Verify 64-byte data was passed
        call_args = mock_client.get_quote.call_args[0][0]
        assert len(call_args) == 64

    @pytest.mark.asyncio
    async def test_sign_with_tee_dev_mode(self, tee_auth_dev):
        """Test signing in development mode."""
        message_hash = bytes.fromhex("a" * 64)

        signature = await tee_auth_dev.sign_with_tee(message_hash)

        assert isinstance(signature, bytes)
        assert len(signature) == 65  # r(32) + s(32) + v(1)

    @pytest.mark.asyncio
    async def test_sign_with_tee_prod_mode(self, tee_auth_prod):
        """Test signing in production mode with TEE."""
        # Mock dstack client for key derivation
        mock_client = Mock()
        mock_key = Mock()
        mock_key.decode_key.return_value = bytes.fromhex("1" * 64)
        mock_client.get_key.return_value = mock_key
        tee_auth_prod.tee_client = mock_client

        message_hash = bytes.fromhex("b" * 64)
        signature = await tee_auth_prod.sign_with_tee(message_hash)

        assert isinstance(signature, bytes)
        assert len(signature) == 65

    @pytest.mark.asyncio
    async def test_tee_client_initialization(self):
        """Test TEE client initialization with different endpoints."""
        # Test with simulator endpoint
        with patch('src.agent.tee_auth.DstackClient') as mock_dstack:
            auth = TEEAuthenticator(
                domain="test.com",
                salt="salt",
                use_tee=True,
                tee_endpoint="http://localhost:8090"
            )
            mock_dstack.assert_called_once_with("http://localhost:8090")

        # Test with socket endpoint (production)
        with patch('src.agent.tee_auth.DstackClient') as mock_dstack:
            auth = TEEAuthenticator(
                domain="test.com",
                salt="salt",
                use_tee=True,
                tee_endpoint="/var/run/dstack.sock"
            )
            mock_dstack.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_error_handling_in_tee_operations(self, tee_auth_prod):
        """Test error handling in TEE operations."""
        # Mock client to raise errors
        mock_client = Mock()
        mock_client.get_key.side_effect = Exception("TEE key derivation failed")
        tee_auth_prod.tee_client = mock_client

        with pytest.raises(Exception) as exc_info:
            await tee_auth_prod.derive_address()

        assert "TEE key derivation failed" in str(exc_info.value)

    def test_attestation_data_uniqueness(self, tee_auth_dev):
        """Test that attestation data is unique for different inputs."""
        # Change domain
        auth1 = TEEAuthenticator("domain1.com", "salt", False)
        auth2 = TEEAuthenticator("domain2.com", "salt", False)

        data1 = auth1._create_attestation_data(method="hash")
        data2 = auth2._create_attestation_data(method="hash")

        assert data1 != data2
        assert len(data1) == 64
        assert len(data2) == 64

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, tee_auth_dev):
        """Test concurrent TEE operations."""
        import asyncio

        # Run multiple operations concurrently
        results = await asyncio.gather(
            tee_auth_dev.derive_address(),
            tee_auth_dev.get_attestation(),
            tee_auth_dev.derive_address(),
            tee_auth_dev.get_attestation()
        )

        assert len(results) == 4
        # Addresses should be the same
        assert results[0] == results[2]
        # Attestations should have same quote in dev mode
        assert results[1]['quote'] == results[3]['quote']

    def test_key_path_format(self, tee_auth_prod):
        """Test key derivation path format."""
        expected_path = f"wallet/erc8004-{tee_auth_prod.domain}"

        # Mock client to capture the path
        mock_client = Mock()
        mock_key = Mock()
        mock_key.decode_key.return_value = bytes.fromhex("1" * 64)
        mock_client.get_key.return_value = mock_key
        tee_auth_prod.tee_client = mock_client

        # Trigger key derivation
        import asyncio
        asyncio.run(tee_auth_prod.derive_address())

        # Verify correct path was used
        mock_client.get_key.assert_called_with(expected_path, tee_auth_prod.salt)

    @pytest.mark.asyncio
    async def test_fallback_mechanism(self):
        """Test fallback from TEE to development mode."""
        # Start with TEE mode but no client available
        auth = TEEAuthenticator(
            domain="test.com",
            salt="salt",
            use_tee=True,
            private_key="0x" + "2" * 64  # Fallback key
        )

        # Should fall back to using private key when TEE client is None
        auth.tee_client = None
        auth.use_tee = False  # Simulate fallback

        address = await auth.derive_address()
        assert address.startswith("0x")
        assert len(address) == 42


class TestTEEIntegration:
    """Integration tests for TEE with other components."""

    @pytest.mark.asyncio
    async def test_tee_with_signing(self):
        """Test TEE integration with message signing."""
        auth = TEEAuthenticator(
            domain="signing.test",
            salt="sign-salt",
            use_tee=False,
            private_key="0x" + "3" * 64
        )

        # Create a message hash
        message = b"Hello TEE World"
        import hashlib
        message_hash = hashlib.sha256(message).digest()

        # Sign with TEE
        signature = await auth.sign_with_tee(message_hash)

        assert isinstance(signature, bytes)
        assert len(signature) == 65

        # Verify signature format (r, s, v)
        r = signature[:32]
        s = signature[32:64]
        v = signature[64]

        assert len(r) == 32
        assert len(s) == 32
        assert v in [27, 28]  # Valid v values for Ethereum

    @pytest.mark.asyncio
    async def test_attestation_data_methods_consistency(self):
        """Test all attestation data methods produce valid 64-byte data."""
        auth = TEEAuthenticator("test.com", "salt", False)

        methods = ["hash", "structured", "padded"]
        for method in methods:
            data = auth._create_attestation_data(method=method)
            assert len(data) == 64, f"Method {method} did not produce 64 bytes"
            assert isinstance(data, bytes), f"Method {method} did not produce bytes"