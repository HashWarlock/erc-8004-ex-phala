"""
ERC-8004 Registry Client

Handles all interactions with the ERC-8004 registry contracts.
"""

import json
from typing import Dict, Any, Optional, List
from web3 import Web3
from eth_account import Account


class RegistryClient:
    """
    Client for interacting with ERC-8004 registry contracts.

    Manages connections to:
    - Identity Registry
    - Reputation Registry
    - Validation Registry
    """

    def __init__(
        self,
        rpc_url: str,
        chain_id: int,
        registries: Dict[str, str],
        account: Optional[Account] = None
    ):
        """
        Initialize registry client.

        Args:
            rpc_url: Blockchain RPC endpoint
            chain_id: Chain ID for the network
            registries: Dictionary with registry addresses
            account: Account for signing transactions
        """
        self.rpc_url = rpc_url
        self.chain_id = chain_id
        self.registries = registries
        self.account = account

        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to {rpc_url}")

        # Load contract ABIs
        self._load_abis()

        # Initialize contract instances
        self._init_contracts()

    def _load_abis(self):
        """Load contract ABIs."""
        # For now, define minimal ABIs inline
        # In production, load from JSON files

        self.identity_abi = [
            {
                "inputs": [
                    {"name": "agentDomain", "type": "string"},
                    {"name": "agentAddress", "type": "address"},
                    {"name": "agentCard", "type": "string"}
                ],
                "name": "registerAgent",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            },
            {
                "inputs": [{"name": "agentId", "type": "uint256"}],
                "name": "getAgent",
                "outputs": [
                    {"name": "domain", "type": "string"},
                    {"name": "agentAddress", "type": "address"},
                    {"name": "agentCard", "type": "string"},
                    {"name": "isActive", "type": "bool"}
                ],
                "type": "function"
            },
            {
                "inputs": [{"name": "domain", "type": "string"}],
                "name": "getAgentByDomain",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            }
        ]

        self.reputation_abi = [
            {
                "inputs": [
                    {"name": "targetAgentId", "type": "uint256"},
                    {"name": "rating", "type": "uint8"},
                    {"name": "data", "type": "string"}
                ],
                "name": "submitFeedback",
                "outputs": [],
                "type": "function"
            },
            {
                "inputs": [{"name": "agentId", "type": "uint256"}],
                "name": "getReputation",
                "outputs": [
                    {"name": "totalFeedback", "type": "uint256"},
                    {"name": "averageRating", "type": "uint256"}
                ],
                "type": "function"
            }
        ]

        self.validation_abi = [
            {
                "inputs": [
                    {"name": "validatorAgentId", "type": "uint256"},
                    {"name": "dataHash", "type": "bytes32"}
                ],
                "name": "requestValidation",
                "outputs": [],
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "dataHash", "type": "bytes32"},
                    {"name": "response", "type": "uint8"}
                ],
                "name": "submitValidationResponse",
                "outputs": [],
                "type": "function"
            },
            {
                "inputs": [{"name": "dataHash", "type": "bytes32"}],
                "name": "getValidationStatus",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]

    def _init_contracts(self):
        """Initialize contract instances."""
        self.identity_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.registries['identity']),
            abi=self.identity_abi
        )

        self.reputation_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.registries['reputation']),
            abi=self.reputation_abi
        )

        self.validation_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.registries['validation']),
            abi=self.validation_abi
        )

    async def register_agent(
        self,
        domain: str,
        agent_address: str,
        agent_card: Dict[str, Any]
    ) -> int:
        """
        Register a new agent in the Identity Registry.

        Args:
            domain: Agent's domain
            agent_address: Agent's Ethereum address
            agent_card: Agent card with capabilities

        Returns:
            Agent ID assigned by the registry
        """
        if not self.account:
            raise ValueError("Account required for registration")

        # Convert agent card to JSON string
        agent_card_json = json.dumps(agent_card)

        # Build transaction
        tx = self.identity_contract.functions.registerAgent(
            domain,
            Web3.to_checksum_address(agent_address),
            agent_card_json
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 500000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address)
        })

        # Sign and send transaction
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # Wait for receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status != 1:
            raise RuntimeError(f"Registration failed: {receipt}")

        # Extract agent ID from events (simplified)
        # In production, parse the AgentRegistered event
        agent_id = self.identity_contract.functions.getAgentByDomain(domain).call()

        return agent_id

    async def submit_feedback(
        self,
        target_agent_id: int,
        rating: int,
        data: Dict[str, Any]
    ) -> str:
        """
        Submit feedback to the Reputation Registry.

        Args:
            target_agent_id: ID of agent being rated
            rating: Rating value (1-5)
            data: Additional feedback data

        Returns:
            Transaction hash
        """
        if not self.account:
            raise ValueError("Account required for feedback submission")

        # Convert data to JSON
        data_json = json.dumps(data)

        # Build transaction
        tx = self.reputation_contract.functions.submitFeedback(
            target_agent_id,
            rating,
            data_json
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address)
        })

        # Sign and send
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash.hex()

    async def request_validation(
        self,
        validator_agent_id: int,
        data_hash: str
    ) -> str:
        """
        Request validation from a validator agent.

        Args:
            validator_agent_id: ID of validator agent
            data_hash: Hash of data to validate

        Returns:
            Transaction hash
        """
        if not self.account:
            raise ValueError("Account required for validation request")

        # Convert data hash to bytes32
        if data_hash.startswith('0x'):
            data_hash_bytes = bytes.fromhex(data_hash[2:])
        else:
            data_hash_bytes = bytes.fromhex(data_hash)

        # Build transaction
        tx = self.validation_contract.functions.requestValidation(
            validator_agent_id,
            data_hash_bytes
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 150000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address)
        })

        # Sign and send
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash.hex()

    async def submit_validation_response(
        self,
        data_hash: str,
        response: int
    ) -> str:
        """
        Submit a validation response.

        Args:
            data_hash: Hash of validated data
            response: Validation response (0=invalid, 1=valid, 2=uncertain)

        Returns:
            Transaction hash
        """
        if not self.account:
            raise ValueError("Account required for validation response")

        # Convert data hash to bytes32
        if data_hash.startswith('0x'):
            data_hash_bytes = bytes.fromhex(data_hash[2:])
        else:
            data_hash_bytes = bytes.fromhex(data_hash)

        # Build transaction
        tx = self.validation_contract.functions.submitValidationResponse(
            data_hash_bytes,
            response
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 150000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address)
        })

        # Sign and send
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash.hex()

    async def get_agent_info(self, agent_id: int) -> Dict[str, Any]:
        """
        Get agent information from Identity Registry.

        Args:
            agent_id: Agent ID to lookup

        Returns:
            Agent information dictionary
        """
        result = self.identity_contract.functions.getAgent(agent_id).call()

        return {
            "domain": result[0],
            "address": result[1],
            "agentCard": json.loads(result[2]) if result[2] else {},
            "isActive": result[3]
        }

    async def get_reputation(self, agent_id: int) -> Dict[str, Any]:
        """
        Get agent reputation from Reputation Registry.

        Args:
            agent_id: Agent ID to lookup

        Returns:
            Reputation information
        """
        result = self.reputation_contract.functions.getReputation(agent_id).call()

        return {
            "totalFeedback": result[0],
            "averageRating": result[1] / 100  # Convert from basis points
        }