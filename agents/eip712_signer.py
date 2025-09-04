"""
EIP-712 Typed Data Signing for ERC-8004 Agents
Secure message signing with TEE integration via dstack
"""

from typing import Dict, Any, Optional, Tuple
from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_utils import to_hex
import json
import os


class EIP712Signer:
    """EIP-712 typed data signing with TEE security"""

    def __init__(self, chain_id: int = 31337, contract_address: Optional[str] = None):
        """
        Initialize EIP-712 signer

        Args:
            chain_id: Chain ID for the domain separator
            contract_address: Verifying contract address
        """
        self.chain_id = chain_id
        self.contract_address = (
            contract_address or "0x0000000000000000000000000000000000000000"
        )
        self.domain_name = "ERC8004-Trustless-Agents"
        self.domain_version = "1"

    def get_domain_separator(self) -> Dict[str, Any]:
        """
        Get EIP-712 domain separator

        Returns:
            Domain separator dictionary
        """
        return {
            "name": self.domain_name,
            "version": self.domain_version,
            "chainId": self.chain_id,
            "verifyingContract": self.contract_address,
        }

    def get_message_types(self) -> Dict[str, list]:
        """
        Get EIP-712 message type definitions

        Returns:
            Type definitions for agent messages
        """
        return {
            "AnalysisRequest": [
                {"name": "requester", "type": "address"},
                {"name": "topic", "type": "string"},
                {"name": "parameters", "type": "string"},
                {"name": "nonce", "type": "uint256"},
                {"name": "timestamp", "type": "uint256"},
            ],
            "ValidationResult": [
                {"name": "validator", "type": "address"},
                {"name": "analysisId", "type": "bytes32"},
                {"name": "isValid", "type": "bool"},
                {"name": "confidence", "type": "uint8"},
                {"name": "details", "type": "string"},
                {"name": "timestamp", "type": "uint256"},
            ],
            "FeedbackSubmission": [
                {"name": "submitter", "type": "address"},
                {"name": "analysisId", "type": "bytes32"},
                {"name": "rating", "type": "uint8"},
                {"name": "comment", "type": "string"},
                {"name": "timestamp", "type": "uint256"},
            ],
            "AgentRegistration": [
                {"name": "agent", "type": "address"},
                {"name": "agentType", "type": "string"},
                {"name": "capabilities", "type": "string"},
                {"name": "endpoint", "type": "string"},
                {"name": "timestamp", "type": "uint256"},
            ],
            "ServiceAuthorization": [
                {"name": "authorizer", "type": "address"},
                {"name": "service", "type": "address"},
                {"name": "permissions", "type": "uint256"},
                {"name": "expiry", "type": "uint256"},
                {"name": "nonce", "type": "uint256"},
            ],
        }

    def create_typed_data(
        self, message_type: str, message_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create EIP-712 typed data structure

        Args:
            message_type: Type of message (e.g., "AnalysisRequest")
            message_data: Message data dictionary

        Returns:
            Complete EIP-712 typed data structure
        """
        types = self.get_message_types()

        if message_type not in types:
            raise ValueError(f"Unknown message type: {message_type}")

        return {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"},
                ],
                message_type: types[message_type],
            },
            "primaryType": message_type,
            "domain": self.get_domain_separator(),
            "message": message_data,
        }

    def sign_typed_data(
        self, typed_data: Dict[str, Any], private_key: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Sign EIP-712 typed data

        Args:
            typed_data: EIP-712 typed data structure
            private_key: Private key for signing (in TEE, this would use Key Generator)

        Returns:
            Tuple of (signature_hex, signature_components)
        """
        # Encode the typed data using full_message format
        encoded = encode_typed_data(full_message=typed_data)

        # Sign the message
        account = Account.from_key(private_key)
        signed = account.sign_message(encoded)

        # Extract signature components
        signature_components = {
            "v": signed.v,
            "r": to_hex(signed.r),
            "s": to_hex(signed.s),
            "signature": signed.signature.hex(),
        }

        return signed.signature.hex(), signature_components

    def verify_signature(
        self,
        typed_data: Dict[str, Any],
        signature: str,
        expected_signer: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Verify EIP-712 signature and recover signer

        Args:
            typed_data: EIP-712 typed data that was signed
            signature: Hex signature string
            expected_signer: Optional expected signer address

        Returns:
            Tuple of (is_valid, recovered_signer_address)
        """
        try:
            # Encode the typed data using full_message format
            encoded = encode_typed_data(full_message=typed_data)

            # Recover signer from signature
            recovered = Account.recover_message(encoded, signature=signature)

            # Verify against expected signer if provided
            if expected_signer:
                is_valid = recovered.lower() == expected_signer.lower()
            else:
                is_valid = True

            return is_valid, recovered

        except Exception as e:
            print(f"Signature verification failed: {e}")
            return False, "0x0000000000000000000000000000000000000000"

    def create_analysis_request(
        self, requester: str, topic: str, parameters: Dict[str, Any], nonce: int
    ) -> Dict[str, Any]:
        """
        Create an analysis request message

        Args:
            requester: Requester address
            topic: Analysis topic
            parameters: Analysis parameters
            nonce: Request nonce

        Returns:
            EIP-712 typed data for analysis request
        """
        import time

        message_data = {
            "requester": requester,
            "topic": topic,
            "parameters": json.dumps(parameters),
            "nonce": nonce,
            "timestamp": int(time.time()),
        }

        return self.create_typed_data("AnalysisRequest", message_data)

    def create_validation_result(
        self,
        validator: str,
        analysis_id: str,
        is_valid: bool,
        confidence: int,
        details: str,
    ) -> Dict[str, Any]:
        """
        Create a validation result message

        Args:
            validator: Validator address
            analysis_id: ID of the analysis being validated
            is_valid: Validation result
            confidence: Confidence level (0-100)
            details: Validation details

        Returns:
            EIP-712 typed data for validation result
        """
        import time

        # Convert analysis_id to bytes32 format
        if not analysis_id.startswith("0x"):
            analysis_id = "0x" + analysis_id
        if len(analysis_id) < 66:
            analysis_id = analysis_id + "0" * (66 - len(analysis_id))

        message_data = {
            "validator": validator,
            "analysisId": analysis_id,
            "isValid": is_valid,
            "confidence": min(100, max(0, confidence)),
            "details": details,
            "timestamp": int(time.time()),
        }

        return self.create_typed_data("ValidationResult", message_data)

    def create_feedback_submission(
        self, submitter: str, analysis_id: str, rating: int, comment: str
    ) -> Dict[str, Any]:
        """
        Create a feedback submission message

        Args:
            submitter: Submitter address
            analysis_id: ID of the analysis being reviewed
            rating: Rating (1-5)
            comment: Feedback comment

        Returns:
            EIP-712 typed data for feedback submission
        """
        import time

        # Convert analysis_id to bytes32 format
        if not analysis_id.startswith("0x"):
            analysis_id = "0x" + analysis_id
        if len(analysis_id) < 66:
            analysis_id = analysis_id + "0" * (66 - len(analysis_id))

        message_data = {
            "submitter": submitter,
            "analysisId": analysis_id,
            "rating": min(5, max(1, rating)),
            "comment": comment,
            "timestamp": int(time.time()),
        }

        return self.create_typed_data("FeedbackSubmission", message_data)


class TEESecureSigner(EIP712Signer):
    """
    TEE-secured EIP-712 signer using dstack Key Generator
    """

    def __init__(self, chain_id: int = 31337, contract_address: Optional[str] = None):
        """
        Initialize TEE-secured signer

        Args:
            chain_id: Chain ID for the domain separator
            contract_address: Verifying contract address
        """
        super().__init__(chain_id, contract_address)
        self.tee_enabled = self._check_tee_availability()

    def _check_tee_availability(self) -> bool:
        """
        Check if TEE/dstack is available

        Returns:
            True if TEE is available, False otherwise
        """
        try:
            # Check for dstack socket
            socket_path = os.environ.get(
                "DSTACK_SIMULATOR_ENDPOINT", ".dstack/sdk/simulator/dstack.sock"
            )
            return os.path.exists(socket_path)
        except:
            return False

    def sign_with_tee(
        self, typed_data: Dict[str, Any], key_id: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Sign typed data using TEE Key Generator

        Args:
            typed_data: EIP-712 typed data structure
            key_id: Key identifier in TEE Key Generator

        Returns:
            Tuple of (signature_hex, signature_components)
        """
        if not self.tee_enabled:
            raise RuntimeError("TEE not available for secure signing")

        # In production, this would use dstack Key Generator
        # For now, we'll simulate with a deterministic key
        # TODO: Integrate actual dstack Key Generator when available

        # Simulate TEE signing
        import hashlib

        simulated_key = "0x" + hashlib.sha256(key_id.encode()).hexdigest()

        return self.sign_typed_data(typed_data, simulated_key)

    def get_tee_attestation(self) -> Optional[Dict[str, Any]]:
        """
        Get TEE attestation for the signing environment

        Returns:
            Attestation data if available
        """
        if not self.tee_enabled:
            return None

        # In production, this would fetch actual attestation from dstack
        return {
            "tee_type": "dstack_simulator",
            "attestation": "simulated_attestation_data",
            "timestamp": int(__import__("time").time()),
            "verified": True,
        }
