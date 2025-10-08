"""
TEE Authentication Module for ERC-8004 Agents

Provides secure key derivation and attestation using dstack SDK.
Uses DstackClient for TEE operations including deterministic key generation
and remote attestation via get_quote.
"""

import os
import hashlib
from typing import Dict, Any, Optional
from dstack_sdk import DstackClient, AsyncDstackClient
from eth_account import Account
from eth_utils import keccak


class TEEAuthenticator:
    """
    TEE Authentication handler for secure agent operations.

    Provides:
    - Deterministic key derivation using TEE
    - Attestation generation
    - Secure signing operations
    """

    def __init__(
        self,
        domain: str,
        salt: str,
        use_tee: bool = True,
        tee_endpoint: Optional[str] = None,
        private_key: Optional[str] = None
    ):
        """
        Initialize TEE authenticator.

        Args:
            domain: Agent's domain identifier
            salt: Unique salt for key derivation
            use_tee: Whether to use TEE (True) or fallback to private key
            tee_endpoint: Custom TEE endpoint (defaults to env or production)
            private_key: Fallback private key for non-TEE mode
        """
        self.domain = domain
        self.salt = salt
        self.use_tee = use_tee

        if use_tee:
            # Initialize TEE client
            if tee_endpoint:
                self.tee_endpoint = tee_endpoint
            else:
                # Check for simulator endpoint (development)
                self.tee_endpoint = os.getenv("DSTACK_SIMULATOR_ENDPOINT")
                if not self.tee_endpoint:
                    # Default to production socket
                    self.tee_endpoint = "/var/run/dstack.sock"

            print(f"🔐 Initializing TEE client at: {self.tee_endpoint}")
            # DstackClient takes the endpoint directly (URL for simulator, default for socket)
            if self.tee_endpoint.startswith("http"):
                # Simulator endpoint
                self.tee_client = DstackClient(self.tee_endpoint)
            else:
                # Socket endpoint (default)
                self.tee_client = DstackClient()

            # Derive key using TEE
            self._derive_tee_key()
        else:
            # Use provided private key
            if not private_key:
                raise ValueError("Private key required when TEE is disabled")
            self.private_key = private_key
            self.account = Account.from_key(private_key)
            self.address = self.account.address
            print(f"🔑 Using private key mode, address: {self.address}")

    def _derive_tee_key(self):
        """Derive private key using TEE's secure key derivation."""
        # Create unique path for deterministic key derivation
        # Format: category/subcategory for wallet keys
        # Include salt in path for truly unique keys
        path = f"wallet/erc8004-{self.salt}"
        # Purpose uses domain for context
        purpose = self.domain

        print(f"🔑 Deriving key for agent with path: {path[:30]}...")

        try:
            # Use TEE's get_key function for deterministic key derivation
            # get_key(path, purpose) returns a key object
            key_result = self.tee_client.get_key(path, purpose)

            # Decode the key to get the raw private key
            private_key_bytes = key_result.decode_key()

            # Convert to hex string for eth_account
            if isinstance(private_key_bytes, bytes):
                key_hex = "0x" + private_key_bytes.hex()
            else:
                # Already a hex string
                key_hex = private_key_bytes
                if not key_hex.startswith("0x"):
                    key_hex = "0x" + key_hex

            self.private_key = key_hex
            self.account = Account.from_key(key_hex)
            self.address = self.account.address

            print(f"✅ Key derived successfully")
            print(f"   Address: {self.address}")
            print(f"   Address length: {len(self.address)}")
            print(f"   Address (no 0x): {self.address.lstrip('0x')} (len: {len(self.address.lstrip('0x'))})")

        except Exception as e:
            raise RuntimeError(f"Failed to derive key from TEE: {e}")

    async def derive_address(self) -> str:
        """
        Get the agent's Ethereum address.

        Returns:
            Ethereum address as hex string
        """
        return self.address

    async def get_attestation(self) -> Dict[str, Any]:
        """
        Get TEE attestation for the agent.

        Returns:
            Attestation data including quote and measurements
        """
        if not self.use_tee:
            return {
                "mode": "development",
                "attestation": None,
                "note": "TEE disabled, using private key mode"
            }

        try:
            # Get attestation from TEE using get_quote

            import binascii
            # Ensure address is properly formatted (40 hex chars after 0x)
            address_hex = self.address.lstrip('0x')

            # Pad with leading zero if odd length
            if len(address_hex) % 2 != 0:
                address_hex = '0' + address_hex

            print(f"🔍 Converting address to bytes: {address_hex} (length: {len(address_hex)})")
            raw_address = binascii.a2b_hex(address_hex)
            application_data = self._create_attestation_data(raw_address)
            quote_result = self.tee_client.get_quote(application_data)

            # Format attestation data
            attestation_data = {
                "quote": quote_result.quote,
                "event_log": quote_result.event_log,
                "application_data": {
                    "raw": application_data.hex(),
                    "domain": self.domain,
                    "address": self.address,
                    "size": len(application_data),
                    "method": "hash"
                },
                "endpoint": self.tee_endpoint,
                "agent_address": self.address
            }

            return attestation_data

        except Exception as e:
            print(f"⚠️ Failed to get attestation: {e}")
            return {
                "error": str(e),
                "mode": "degraded",
                "agent_address": self.address
            }

    async def sign_with_tee(self, message: bytes) -> bytes:
        """
        Sign a message using the TEE-derived key.

        Args:
            message: Message bytes (32-byte hash) to sign

        Returns:
            Signature bytes
        """
        if self.use_tee:
            # In production, use TEE's signing with the derived key
            signed = self.account.unsafe_sign_hash(message)
            return signed.signature
        else:
            # Use private key directly
            signed = self.account.unsafe_sign_hash(message)
            return signed.signature

    def _create_attestation_data(self, report_data) -> bytes:
        """
        Create 64-byte attestation data for TEE quote.
        """
        assert len(report_data) <= 64
        return report_data.ljust(64, b'\x00')

    def get_private_key(self) -> str:
        """
        Get the private key (for development/testing only).

        Returns:
            Private key as hex string
        """
        if not os.getenv("DEBUG", "false").lower() == "true":
            raise PermissionError("Private key access disabled in production")
        return self.private_key