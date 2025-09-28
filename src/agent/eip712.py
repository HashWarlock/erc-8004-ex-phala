"""
EIP-712 Typed Data Signer

Implements EIP-712 structured data signing for secure off-chain messages.
"""

import json
from typing import Dict, Any, Optional
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3


class EIP712Signer:
    """
    EIP-712 signer for typed data.

    Provides secure, standardized message signing that can be verified on-chain.
    """

    def __init__(
        self,
        domain_name: str,
        domain_version: str,
        chain_id: int,
        account: Optional[Account] = None,
        verifying_contract: Optional[str] = None
    ):
        """
        Initialize EIP-712 signer.

        Args:
            domain_name: Name of the signing domain
            domain_version: Version of the signing domain
            chain_id: Chain ID for the network
            account: Account for signing (optional)
            verifying_contract: Contract address for verification (optional)
        """
        self.domain_name = domain_name
        self.domain_version = domain_version
        self.chain_id = chain_id
        self.account = account
        self.verifying_contract = verifying_contract

        # Build domain separator
        self.domain = self._build_domain()

    def _build_domain(self) -> Dict[str, Any]:
        """
        Build EIP-712 domain separator.

        Returns:
            Domain configuration
        """
        domain = {
            "name": self.domain_name,
            "version": self.domain_version,
            "chainId": self.chain_id
        }

        if self.verifying_contract:
            domain["verifyingContract"] = self.verifying_contract

        return domain

    async def sign_typed_data(self, message: Dict[str, Any]) -> str:
        """
        Sign typed data using EIP-712 standard.

        Args:
            message: Message data to sign

        Returns:
            Signature as hex string

        Raises:
            ValueError: If no account is available for signing
        """
        if not self.account:
            raise ValueError("No account available for signing")

        # Structure the typed data
        typed_data = self._create_typed_data(message)

        # Encode the structured data
        encoded = encode_structured_data(typed_data)

        # Sign the encoded message
        signed = self.account.sign_message(encoded)

        return signed.signature.hex()

    def _create_typed_data(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create EIP-712 typed data structure.

        Args:
            message: Message to structure

        Returns:
            Typed data structure
        """
        # Default message types
        default_types = {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"}
            ],
            "Message": []
        }

        # Add verifying contract if present
        if self.verifying_contract:
            default_types["EIP712Domain"].append({
                "name": "verifyingContract",
                "type": "address"
            })

        # Infer message types from the message data
        message_types = []
        for key, value in message.items():
            if isinstance(value, str):
                if Web3.is_address(value):
                    message_types.append({"name": key, "type": "address"})
                elif value.startswith("0x") and len(value) == 66:
                    message_types.append({"name": key, "type": "bytes32"})
                else:
                    message_types.append({"name": key, "type": "string"})
            elif isinstance(value, int):
                message_types.append({"name": key, "type": "uint256"})
            elif isinstance(value, bool):
                message_types.append({"name": key, "type": "bool"})
            elif isinstance(value, bytes):
                message_types.append({"name": key, "type": "bytes"})
            else:
                # Default to string for complex types
                message_types.append({"name": key, "type": "string"})

        default_types["Message"] = message_types

        # Create the typed data structure
        typed_data = {
            "types": default_types,
            "primaryType": "Message",
            "domain": self.domain,
            "message": message
        }

        return typed_data

    def verify_signature(
        self,
        message: Dict[str, Any],
        signature: str
    ) -> str:
        """
        Verify a signature and recover the signer address.

        Args:
            message: Original message that was signed
            signature: Signature to verify

        Returns:
            Recovered signer address

        Raises:
            ValueError: If signature is invalid
        """
        # Create typed data structure
        typed_data = self._create_typed_data(message)

        # Encode the structured data
        encoded = encode_structured_data(typed_data)

        # Recover address from signature
        recovered = Account.recover_message(encoded, signature=signature)

        return recovered

    def create_agent_message_types(self) -> Dict[str, list]:
        """
        Create standard message types for agent communications.

        Returns:
            Type definitions for common agent messages
        """
        return {
            "AgentRegistration": [
                {"name": "agentId", "type": "uint256"},
                {"name": "domain", "type": "string"},
                {"name": "address", "type": "address"},
                {"name": "timestamp", "type": "uint256"},
                {"name": "nonce", "type": "uint256"}
            ],
            "ValidationRequest": [
                {"name": "requestId", "type": "bytes32"},
                {"name": "dataHash", "type": "bytes32"},
                {"name": "requester", "type": "address"},
                {"name": "validator", "type": "address"},
                {"name": "timestamp", "type": "uint256"}
            ],
            "ValidationResponse": [
                {"name": "requestId", "type": "bytes32"},
                {"name": "dataHash", "type": "bytes32"},
                {"name": "isValid", "type": "bool"},
                {"name": "confidence", "type": "uint8"},
                {"name": "validator", "type": "address"},
                {"name": "timestamp", "type": "uint256"}
            ],
            "ReputationFeedback": [
                {"name": "targetAgentId", "type": "uint256"},
                {"name": "rating", "type": "uint8"},
                {"name": "comment", "type": "string"},
                {"name": "rater", "type": "address"},
                {"name": "timestamp", "type": "uint256"}
            ]
        }

    def set_account(self, account: Account):
        """
        Set the signing account.

        Args:
            account: Account to use for signing
        """
        self.account = account

    def get_domain_separator(self) -> bytes:
        """
        Get the EIP-712 domain separator hash.

        Returns:
            Domain separator as bytes
        """
        # Create a dummy message to get the domain separator
        dummy_message = {"dummy": "value"}
        typed_data = self._create_typed_data(dummy_message)

        # Encode and hash the domain
        from eth_utils import keccak
        domain_bytes = json.dumps(self.domain, sort_keys=True).encode()
        return keccak(domain_bytes)