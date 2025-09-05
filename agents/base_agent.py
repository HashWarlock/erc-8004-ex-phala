"""
Base Agent for ERC-8004 Registry Interactions

This module provides the foundational class for agents that interact with
the ERC-8004 registry contracts.
"""

import json
import os
from typing import Dict, Optional, Any
from web3 import Web3
from web3.contract import Contract
from dotenv import load_dotenv

load_dotenv()

class ERC8004BaseAgent:
    """Base class for agents interacting with ERC-8004 registries"""
    
    def __init__(self, agent_domain: str, private_key: str):
        """
        Initialize the base agent
        
        Args:
            agent_domain: The domain where this agent's AgentCard is hosted
            private_key: Private key for signing transactions
        """
        self.agent_domain = agent_domain
        self.private_key = private_key
        
        # Initialize Web3 connection
        rpc_url = os.getenv('RPC_URL', 'http://127.0.0.1:8545')
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to {rpc_url}")
        
        # Load account from private key
        self.account = self.w3.eth.account.from_key(private_key)
        self.address = self.account.address
        
        # Load contract addresses from deployment
        self._load_contract_addresses()
        
        # Initialize contract instances
        self._init_contracts()
        
        # Agent registry info
        self.agent_id: Optional[int] = None
        self._check_registration()
    
    def _load_contract_addresses(self):
        """Load contract addresses from deployment.json"""
        try:
            with open('deployment.json', 'r') as f:
                deployment = json.load(f)
                contracts = deployment['contracts']
                
                self.identity_registry_address = contracts['identity_registry']
                self.reputation_registry_address = contracts['reputation_registry']
                self.validation_registry_address = contracts['validation_registry']
        except FileNotFoundError:
            raise FileNotFoundError(
                "deployment.json not found. Please run 'python scripts/deploy.py' first."
            )
    
    def _load_contract_abi(self, contract_name: str) -> list:
        """Load contract ABI from compiled artifacts"""
        abi_path = f"contracts/out/{contract_name}.sol/{contract_name}.json"
        
        with open(abi_path, 'r') as f:
            artifact = json.load(f)
            return artifact['abi']
    
    def _init_contracts(self):
        """Initialize contract instances"""
        # Load ABIs
        identity_abi = self._load_contract_abi('IdentityRegistry')
        reputation_abi = self._load_contract_abi('ReputationRegistry')
        validation_abi = self._load_contract_abi('ValidationRegistry')
        
        # Create contract instances
        self.identity_registry = self.w3.eth.contract(
            address=self.identity_registry_address,
            abi=identity_abi
        )
        
        self.reputation_registry = self.w3.eth.contract(
            address=self.reputation_registry_address,
            abi=reputation_abi
        )
        
        self.validation_registry = self.w3.eth.contract(
            address=self.validation_registry_address,
            abi=validation_abi
        )
    
    def _check_registration(self):
        """Check if this agent is already registered"""
        try:
            result = self.identity_registry.functions.resolveByAddress(self.address).call()
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
            self.agent_domain,
            self.address
        )
        
        # Estimate gas
        gas_estimate = function.estimate_gas({'from': self.address})
        
        # Build transaction
        transaction = function.build_transaction({
            'from': self.address,
            'gas': int(gas_estimate * 1.2),
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.address),
        })
        
        # Sign and send
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        print(f"   Transaction hash: {tx_hash.hex()}")
        
        # Wait for confirmation
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt.status == 1:
            # Try multiple approaches to get the agent ID
            agent_id = None
            
            # Approach 1: Parse event logs
            try:
                logs = self.identity_registry.events.AgentRegistered().process_receipt(receipt)
                if logs and len(logs) > 0:
                    agent_id = logs[0]['args']['agentId']
                    print(f"✅ Agent registered successfully with ID: {agent_id} (from events)")
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
                        
                        agent_info = self.identity_registry.functions.resolveByAddress(self.address).call()
                        if agent_info[0] > 0:  # agentId > 0 means found
                            agent_id = agent_info[0]
                            print(f"✅ Agent registered successfully with ID: {agent_id} (from query)")
                            break
                    except Exception as e:
                        if attempt == 2:  # Last attempt
                            print(f"⚠️  Could not resolve agent by address: {e}")
            
            if agent_id is not None:
                self.agent_id = agent_id
                return self.agent_id
            else:
                raise Exception("Registration succeeded but couldn't determine agent ID")
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
            client_agent_id,
            self.agent_id
        )
        
        # Build and send transaction
        transaction = function.build_transaction({
            'from': self.address,
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.address),
        })
        
        try:
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            print(f"   Transaction hash: {tx_hash.hex()}")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                print(f"✅ Feedback authorization successful")
                return tx_hash.hex()
            else:
                print(f"❌ Transaction failed with status: {receipt.status}")
                raise Exception(f"Feedback authorization transaction failed with status {receipt.status}")
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
            validator_agent_id,
            self.agent_id,
            data_hash
        )
        
        # Build and send transaction
        transaction = function.build_transaction({
            'from': self.address,
            'gas': 150000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.address),
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
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
            data_hash,
            response
        )
        
        # Build and send transaction
        transaction = function.build_transaction({
            'from': self.address,
            'gas': 120000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.address),
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
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
            'agent_id': result[0],
            'agent_domain': result[1],
            'agent_address': result[2]
        } 