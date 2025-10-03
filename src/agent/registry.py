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
                    {"name": "agentAddress", "type": "address"}
                ],
                "name": "newAgent",
                "outputs": [{"name": "agentId", "type": "uint256"}],
                "type": "function",
                "stateMutability": "payable"  # Changed from nonpayable - contract requires 0.005 ETH fee
            },
            {
                "inputs": [{"name": "domain", "type": "string"}],
                "name": "resolveByDomain",
                "outputs": [
                    {"name": "agentId", "type": "uint256"},
                    {"name": "agentDomain", "type": "string"},
                    {"name": "agentAddress", "type": "address"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "agentAddress", "type": "address"}],
                "name": "resolveByAddress",
                "outputs": [
                    {"name": "agentId", "type": "uint256"},
                    {"name": "agentDomain", "type": "string"},
                    {"name": "agentAddress", "type": "address"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "agentId", "type": "uint256"}],
                "name": "getAgent",
                "outputs": [
                    {"name": "agentId", "type": "uint256"},
                    {"name": "agentAddress", "type": "address"},
                    {"name": "domain", "type": "string"},
                    {"name": "timestamp", "type": "uint256"}
                ],
                "stateMutability": "view",
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

    async def check_agent_registration(
        self,
        domain: str = None,
        agent_address: str = None
    ) -> Dict[str, Any]:
        """
        Check if agent is already registered by domain or address.

        Args:
            domain: Agent's domain
            agent_address: Agent's Ethereum address

        Returns:
            Dict with registration info or {"registered": False} if not registered
        """
        try:
            if domain:
                # resolveByDomain returns (agentId, agentDomain, agentAddress)
                result = self.identity_contract.functions.resolveByDomain(domain).call()
                if result[0] > 0:
                    return {
                        "registered": True,
                        "agent_id": result[0],
                        "domain": result[1],
                        "agent_address": result[2]
                    }

            if agent_address:
                # resolveByAddress returns (agentId, agentDomain, agentAddress)
                result = self.identity_contract.functions.resolveByAddress(
                    Web3.to_checksum_address(agent_address)
                ).call()
                if result[0] > 0:
                    return {
                        "registered": True,
                        "agent_id": result[0],
                        "domain": result[1],
                        "agent_address": result[2]
                    }
        except Exception as e:
            print(f"⚠️  Registration check: {e}")

        return {"registered": False}

    async def register_agent(
        self,
        domain: str,
        agent_address: str,
        agent_card: Dict[str, Any] = None
    ) -> int:
        """
        Register a new agent in the Identity Registry using newAgent().

        Note: Requires 0.005 ETH registration fee.
        Agent card is stored off-chain.

        Args:
            domain: Agent's domain
            agent_address: Agent's Ethereum address
            agent_card: Agent card (unused in reference implementation)

        Returns:
            Agent ID assigned by the registry

        Raises:
            RuntimeError: If registration fails (e.g., already registered, insufficient fee)
        """
        if not self.account:
            raise ValueError("Account required for registration")

        # Check if already registered - need to check BOTH domain and address match
        domain_check = await self.check_agent_registration(domain=domain)
        address_check = await self.check_agent_registration(agent_address=agent_address)

        # If domain and address both registered AND match each other, agent is already registered
        if (domain_check["registered"] and address_check["registered"] and
            domain_check["agent_id"] == address_check["agent_id"]):
            print(f"✅ Agent already registered with ID: {domain_check['agent_id']}")
            return domain_check["agent_id"]

        # If domain registered but to different address, or address registered to different domain - conflict
        if domain_check["registered"] or address_check["registered"]:
            if domain_check["registered"] and domain_check["agent_address"].lower() != agent_address.lower():
                raise ValueError(f"Domain '{domain}' already registered to different address: {domain_check['agent_address']}")
            if address_check["registered"] and address_check["domain"] != domain:
                raise ValueError(f"Address already registered to different domain: {address_check['domain']}")

        # Use newAgent function with 0.005 ETH fee
        registration_fee = self.w3.to_wei(0.005, 'ether')

        tx = self.identity_contract.functions.newAgent(
            domain,
            Web3.to_checksum_address(agent_address)
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'value': registration_fee  # 0.005 ETH registration fee
        })

        # Sign and send transaction
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        print(f"📤 Transaction sent: {tx_hash.hex()} (fee: 0.005 ETH)")

        # Wait for receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status != 1:
            error_msg = "Registration failed - check: sufficient balance (0.005 ETH + gas), valid domain, unique address"
            raise RuntimeError(f"{error_msg}: tx={tx_hash.hex()}")

        # Get agent ID from logs
        agent_id = receipt['logs'][0]['topics'][1].hex() if receipt['logs'] else None

        if not agent_id:
            # Fallback: query by domain
            result = self.identity_contract.functions.resolveByDomain(domain).call()
            agent_id = result[0]

        return int(agent_id, 16) if isinstance(agent_id, str) else agent_id

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
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

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
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

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
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

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