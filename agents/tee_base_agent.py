"""
TEE-Enabled Base Agent for ERC-8004 Registry Interactions

This module provides a TEE-enabled version of the base agent that derives
its private key using the TEE's deterministic key derivation function.
"""

import json
import os
from typing import Dict, Optional, Any
from web3 import Web3
from dstack_sdk import DstackClient
from eth_account import Account
from dotenv import load_dotenv

load_dotenv()


class ERC8004TEEAgent:
    """TEE-enabled agent that derives keys using TEE's secure key derivation"""

    def __init__(
        self, agent_domain: str, salt: str, tee_endpoint: Optional[str] = None
    ):
        """
        Initialize the TEE-enabled agent

        Args:
            agent_domain: The domain where this agent's AgentCard is hosted
            salt: Secret salt for deterministic key derivation (unique per agent)
            tee_endpoint: TEE endpoint (defaults to DSTACK_SIMULATOR_ENDPOINT or production socket)
        """
        self.agent_domain = agent_domain
        self.salt = salt

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
        self.tee_client = DstackClient(endpoint=self.tee_endpoint)

        # Derive private key using TEE's deterministic key derivation
        self._derive_key()

        # Initialize Web3 connection
        rpc_url = os.getenv("RPC_URL", "http://127.0.0.1:8545")
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to {rpc_url}")

        # Load account from derived private key
        self.account = Account.from_key(self.private_key)
        self.address = self.account.address

        print(f"📍 Agent address: {self.address}")

        # Load contract addresses from deployment
        self._load_contract_addresses()

        # Initialize contract instances
        self._init_contracts()

        # Agent registry info
        self.agent_id: Optional[int] = None
        self._check_registration()

    def _derive_key(self):
        """Derive private key using TEE's secure key derivation"""
        # Create a unique identifier by combining agent domain and salt
        # This ensures each agent gets a unique, deterministic key
        # Include salt in the path to ensure different salts produce different keys
        path = f"erc8004-agent/{self.agent_domain}/{self.salt}"
        purpose = "key-derivation"  # Fixed purpose

        print(f"🔑 Deriving key for agent with path: {path[:30]}...")

        try:
            # Use TEE's get_key function for deterministic key derivation
            # This returns a GetKeyResponse with secp256k1 private key
            key_result = self.tee_client.get_key(path, purpose)

            # Get the key from the response
            # The key is a hex string of 32-byte secp256k1 private key
            if hasattr(key_result, "key"):
                key_hex = key_result.key
            else:
                # Fallback for dict response
                key_hex = key_result["key"]

            # decode_key() returns the raw bytes if needed
            if hasattr(key_result, "decode_key"):
                key_bytes = key_result.decode_key()
                self.private_key = "0x" + key_bytes.hex()
            else:
                # Already hex string, ensure 0x prefix
                self.private_key = (
                    key_hex if key_hex.startswith("0x") else "0x" + key_hex
                )

            print(f"✅ Key derived successfully")

        except Exception as e:
            print(f"❌ Failed to derive key from TEE: {e}")
            # Fallback for testing: derive key from salt directly (NOT for production!)
            if os.getenv("DEVELOPMENT_MODE") == "true":
                import hashlib

                print("⚠️  DEVELOPMENT MODE: Using fallback key derivation")
                fallback_seed = f"{path}:{purpose}"
                key_bytes = hashlib.sha256(fallback_seed.encode()).digest()
                self.private_key = "0x" + key_bytes.hex()
            else:
                raise

    def get_attestation(self) -> Dict[str, Any]:
        """
        Get TEE attestation quote for the agent's current state

        Returns:
            Attestation data including quote and supporting information
        """
        # Create attestation data that includes agent identity
        attestation_data = {
            "agent_domain": self.agent_domain,
            "agent_address": self.address,
            "agent_id": self.agent_id,
        }

        # Convert to JSON and encode (max 64 bytes for report_data)
        attestation_json = json.dumps(attestation_data)
        # Truncate if needed to fit in 64 bytes
        attestation_bytes = attestation_json.encode()[:64]

        try:
            # get_quote returns GetQuoteResponse with quote and event_log
            quote_result = self.tee_client.get_quote(attestation_bytes)

            return {
                "quote": quote_result.quote
                if hasattr(quote_result, "quote")
                else str(quote_result),
                "event_log": quote_result.event_log
                if hasattr(quote_result, "event_log")
                else None,
                "attestation_data": attestation_data,
                "tee_endpoint": self.tee_endpoint,
            }
        except Exception as e:
            print(f"⚠️  Failed to get attestation: {e}")
            return {"error": str(e), "attestation_data": attestation_data}

    def _load_contract_addresses(self):
        """Load contract addresses from deployed_contracts.json"""
        try:
            with open("deployed_contracts.json", "r") as f:
                deployment = json.load(f)
                contracts = deployment["contracts"]

                self.identity_registry_address = contracts["IdentityRegistry"]
                self.reputation_registry_address = contracts["ReputationRegistry"]
                self.validation_registry_address = contracts["ValidationRegistry"]
        except FileNotFoundError:
            raise FileNotFoundError(
                "deployed_contracts.json not found. Please run 'forge script Deploy.s.sol' first."
            )

    def _load_contract_abi(self, contract_name: str) -> list:
        """Load contract ABI from compiled artifacts"""
        abi_path = f"contracts/out/{contract_name}.sol/{contract_name}.json"

        with open(abi_path, "r") as f:
            artifact = json.load(f)
            return artifact["abi"]

    def _init_contracts(self):
        """Initialize contract instances"""
        # Load ABIs
        identity_abi = self._load_contract_abi("IdentityRegistry")
        reputation_abi = self._load_contract_abi("ReputationRegistry")
        validation_abi = self._load_contract_abi("ValidationRegistry")

        # Create contract instances
        self.identity_registry = self.w3.eth.contract(
            address=self.identity_registry_address, abi=identity_abi
        )

        self.reputation_registry = self.w3.eth.contract(
            address=self.reputation_registry_address, abi=reputation_abi
        )

        self.validation_registry = self.w3.eth.contract(
            address=self.validation_registry_address, abi=validation_abi
        )

    def _check_registration(self):
        """Check if this agent is already registered"""
        try:
            result = self.identity_registry.functions.resolveByAddress(
                self.address
            ).call()
            if result[0] > 0:  # AgentID > 0 means registered
                self.agent_id = result[0]
                print(f"✅ Agent already registered with ID: {self.agent_id}")
            else:
                print("ℹ️  Agent not yet registered")
        except Exception as e:
            print(f"ℹ️  Agent not yet registered: {e}")

    def register_agent(self) -> int:
        """
        Register this agent with the IdentityRegistry

        Returns:
            Agent ID assigned by the registry
        """
        if self.agent_id:
            print(f"Agent already registered with ID: {self.agent_id}")
            return self.agent_id

        print(f"📝 Registering agent with domain: {self.agent_domain}")

        # Build transaction
        function = self.identity_registry.functions.newAgent(
            self.agent_domain, self.address
        )

        # Estimate gas
        try:
            gas_estimate = function.estimate_gas(
                {"from": self.address, "value": self.w3.to_wei(0.005, "ether")}
            )
        except Exception as e:
            # If gas estimation fails, use a default value
            print(f"⚠️  Gas estimation failed: {e}")
            gas_estimate = 200000  # Default gas limit

        # Build transaction
        transaction = function.build_transaction(
            {
                "from": self.address,
                "gas": int(gas_estimate * 1.2),
                "gasPrice": self.w3.eth.gas_price,
                "nonce": self.w3.eth.get_transaction_count(self.address),
                "value": self.w3.to_wei(0.005, "ether"),  # Registration fee
            }
        )

        # Sign and send
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction, private_key=self.private_key
        )
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        print(f"   Transaction hash: {tx_hash.hex()}")

        # Wait for confirmation
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            # Try multiple approaches to get the agent ID
            agent_id = None

            # Approach 1: Parse event logs
            try:
                logs = self.identity_registry.events.AgentRegistered().process_receipt(
                    receipt
                )
                if logs and len(logs) > 0:
                    agent_id = logs[0]["args"]["agentId"]
                    print(
                        f"✅ Agent registered successfully with ID: {agent_id} (from events)"
                    )
            except Exception as e:
                print(f"⚠️  Could not parse event logs: {e}")

            # Approach 2: Query by address (fallback with retry)
            if agent_id is None:
                import time

                for attempt in range(3):  # Retry up to 3 times
                    try:
                        # Small delay to allow blockchain state to settle
                        if attempt > 0:
                            time.sleep(0.5)

                        agent_info = self.identity_registry.functions.resolveByAddress(
                            self.address
                        ).call()
                        if agent_info[0] > 0:  # agentId > 0 means found
                            agent_id = agent_info[0]
                            print(
                                f"✅ Agent registered successfully with ID: {agent_id} (from query)"
                            )
                            break
                    except Exception as e:
                        if attempt == 2:  # Last attempt
                            print(f"⚠️  Could not resolve agent by address: {e}")

            if agent_id is not None:
                self.agent_id = agent_id
                return self.agent_id
            else:
                raise Exception(
                    "Registration succeeded but couldn't determine agent ID"
                )
        else:
            raise Exception("Agent registration failed")

    def authorize_feedback(self, client_agent_id: int) -> str:
        """
        Authorize a client agent to provide feedback to this server agent

        Args:
            client_agent_id: ID of the client agent to authorize

        Returns:
            Transaction hash
        """
        if not self.agent_id:
            raise ValueError("Agent must be registered first")

        print(f"🔐 Authorizing feedback from client agent {client_agent_id}")

        function = self.reputation_registry.functions.acceptFeedback(
            client_agent_id, self.agent_id
        )

        # Build and send transaction
        transaction = function.build_transaction(
            {
                "from": self.address,
                "gas": 100000,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": self.w3.eth.get_transaction_count(self.address),
            }
        )

        try:
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, private_key=self.private_key
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)

            print(f"   Transaction hash: {tx_hash.hex()}")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt.status == 1:
                print(f"✅ Feedback authorization successful")
                return tx_hash.hex()
            else:
                print(f"❌ Transaction failed with status: {receipt.status}")
                raise Exception(
                    f"Feedback authorization transaction failed with status {receipt.status}"
                )
        except Exception as e:
            print(f"❌ Feedback authorization error: {str(e)}")
            raise Exception(f"Feedback authorization failed: {str(e)}")

    def request_validation(self, validator_agent_id: int, data_hash: bytes) -> str:
        """
        Request validation from a validator agent

        Args:
            validator_agent_id: ID of the validator agent
            data_hash: Hash of the data to be validated

        Returns:
            Transaction hash
        """
        if not self.agent_id:
            raise ValueError("Agent must be registered first")

        print(f"🔍 Requesting validation from agent {validator_agent_id}")

        function = self.validation_registry.functions.validationRequest(
            validator_agent_id, self.agent_id, data_hash
        )

        # Build and send transaction
        transaction = function.build_transaction(
            {
                "from": self.address,
                "gas": 150000,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": self.w3.eth.get_transaction_count(self.address),
            }
        )

        signed_txn = self.w3.eth.account.sign_transaction(
            transaction, private_key=self.private_key
        )
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            print(f"✅ Validation request successful")
            return tx_hash.hex()
        else:
            raise Exception("Validation request failed")

    def submit_validation_response(self, data_hash: bytes, response: int) -> str:
        """
        Submit a validation response (for validator agents)

        Args:
            data_hash: Hash of the validated data
            response: Validation score (0-100)

        Returns:
            Transaction hash
        """
        if not self.agent_id:
            raise ValueError("Agent must be registered first")

        print(f"📊 Submitting validation response: {response}/100")

        function = self.validation_registry.functions.validationResponse(
            data_hash, response
        )

        # Build and send transaction
        transaction = function.build_transaction(
            {
                "from": self.address,
                "gas": 120000,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": self.w3.eth.get_transaction_count(self.address),
            }
        )

        signed_txn = self.w3.eth.account.sign_transaction(
            transaction, private_key=self.private_key
        )
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            print(f"✅ Validation response submitted successfully")
            return tx_hash.hex()
        else:
            raise Exception("Validation response submission failed")

    def get_agent_info(self, agent_id: int) -> Dict[str, Any]:
        """Get information about an agent from the registry"""
        result = self.identity_registry.functions.getAgent(agent_id).call()
        return {
            "agent_id": result[0],
            "agent_domain": result[1],
            "agent_address": result[2],
        }
