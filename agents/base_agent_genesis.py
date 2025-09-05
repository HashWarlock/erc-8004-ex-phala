"""
Genesis Studio - Base Agent for ERC-8004 Registry Interactions

This module provides the foundational class for agents that interact with
the ERC-8004 registry contracts using Coinbase AgentKit wallets.
"""

import json
import os
import time
from typing import Dict, Optional, Any, Tuple
from web3 import Web3
from web3.contract import Contract
from dotenv import load_dotenv
from rich import print as rprint

load_dotenv()

class GenesisBaseAgent:
    """Base class for Genesis Studio agents interacting with ERC-8004 registries"""
    
    def __init__(self, agent_domain: str, wallet_address: str, wallet_manager=None):
        """
        Initialize the Genesis base agent
        
        Args:
            agent_domain: The domain where this agent's AgentCard is hosted
            wallet_address: The agent's wallet address (from Coinbase AgentKit)
            wallet_manager: Reference to the GenesisWalletManager instance
        """
        self.agent_domain = agent_domain
        self.address = wallet_address
        self.wallet_manager = wallet_manager
        self.agent_id = None
        
        # Initialize Web3 connection based on network
        self.network = os.getenv('NETWORK', 'base-sepolia')
        self._setup_web3_connection()
        
        # Load contract addresses and ABIs
        self._load_contract_addresses()
        self._load_contracts()
    
    def _setup_web3_connection(self):
        """Setup Web3 connection based on configured network"""
        
        if self.network == 'sepolia':
            rpc_url = os.getenv('SEPOLIA_RPC_URL')
            self.chain_id = int(os.getenv('SEPOLIA_CHAIN_ID', 11155111))
        elif self.network == 'base-sepolia':
            rpc_url = os.getenv('BASE_SEPOLIA_RPC_URL')
            self.chain_id = int(os.getenv('BASE_SEPOLIA_CHAIN_ID', 84532))
        elif self.network == 'optimism-sepolia':
            rpc_url = os.getenv('OPTIMISM_SEPOLIA_RPC_URL')
            self.chain_id = int(os.getenv('OPTIMISM_SEPOLIA_CHAIN_ID', 11155420))
        else:  # local
            rpc_url = os.getenv('LOCAL_RPC_URL', 'http://127.0.0.1:8545')
            self.chain_id = int(os.getenv('LOCAL_CHAIN_ID', 31337))
        
        if not rpc_url:
            raise ValueError(f"RPC URL not configured for network: {self.network}")
        
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to {rpc_url}")
        
        rprint(f"[green]🌐 Connected to {self.network} (Chain ID: {self.chain_id})[/green]")
    
    def _load_contract_addresses(self):
        """Load contract addresses from deployment files"""
        
        # Map network names to deployment files
        deployment_files = {
            'local': 'deployment.json',
            'sepolia': 'deployments/sepolia.json',
            'base-sepolia': 'deployments/base-sepolia.json',
            'optimism-sepolia': 'deployments/optimism-sepolia.json'
        }
        
        deployment_file = deployment_files.get(self.network)
        if not deployment_file:
            raise ValueError(f"No deployment file configured for network: {self.network}")
        
        deployment_path = os.path.join(os.path.dirname(__file__), '..', deployment_file)
        
        try:
            with open(deployment_path, 'r') as f:
                deployment_data = json.load(f)
            
            contracts = deployment_data.get('contracts', {})
            self.identity_registry_address = contracts.get('identity_registry')
            self.reputation_registry_address = contracts.get('reputation_registry')
            self.validation_registry_address = contracts.get('validation_registry')
            
            if not all([self.identity_registry_address, self.reputation_registry_address, self.validation_registry_address]):
                raise ValueError("Missing contract addresses in deployment file")
                
        except FileNotFoundError:
            raise FileNotFoundError(f"Deployment file not found: {deployment_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in deployment file: {deployment_path}")
    
    def _load_contracts(self):
        """Load contract instances with ABIs"""
        
        # Load ABIs from compiled contracts
        contracts_dir = os.path.join(os.path.dirname(__file__), '..', 'contracts', 'out')
        
        # Load Identity Registry
        identity_abi_path = os.path.join(contracts_dir, 'IdentityRegistry.sol', 'IdentityRegistry.json')
        with open(identity_abi_path, 'r') as f:
            identity_artifact = json.load(f)
        
        self.identity_registry = self.w3.eth.contract(
            address=self.identity_registry_address,
            abi=identity_artifact['abi']
        )
        
        # Load Reputation Registry
        reputation_abi_path = os.path.join(contracts_dir, 'ReputationRegistry.sol', 'ReputationRegistry.json')
        with open(reputation_abi_path, 'r') as f:
            reputation_artifact = json.load(f)
        
        self.reputation_registry = self.w3.eth.contract(
            address=self.reputation_registry_address,
            abi=reputation_artifact['abi']
        )
        
        # Load Validation Registry
        validation_abi_path = os.path.join(contracts_dir, 'ValidationRegistry.sol', 'ValidationRegistry.json')
        with open(validation_abi_path, 'r') as f:
            validation_artifact = json.load(f)
        
        self.validation_registry = self.w3.eth.contract(
            address=self.validation_registry_address,
            abi=validation_artifact['abi']
        )
        
        rprint(f"[blue]📋 Contracts loaded for {self.network}[/blue]")
    
    def register_agent(self) -> Tuple[int, str]:
        """
        Register this agent on the IdentityRegistry
        
        Returns:
            Tuple of (agent_id, transaction_hash)
        """
        
        rprint(f"[yellow]🔧 Registering agent: {self.agent_domain}[/yellow]")
        
        # Check if already registered
        try:
            existing_agent = self.identity_registry.functions.resolveByAddress(self.address).call()
            if existing_agent[0] > 0:  # agentId > 0 means already registered
                self.agent_id = existing_agent[0]
                rprint(f"[green]✅ Agent already registered with ID: {self.agent_id}[/green]")
                return self.agent_id, "already_registered"
        except Exception as e:
            # Agent not found, proceed with registration
            rprint(f"[blue]🔍 Agent not yet registered (expected): {e}[/blue]")
            pass
        
        # Use wallet manager to execute the transaction
        if not self.wallet_manager:
            raise ValueError("Wallet manager not available for transaction signing")
        
        # Get the agent's wallet
        agent_name = self._get_agent_name_from_domain()
        wallet = self.wallet_manager.wallets.get(agent_name)
        
        if not wallet:
            raise ValueError(f"Wallet not found for agent: {agent_name}")
        
        try:
            # Prepare contract call data
            contract_call = self.identity_registry.functions.newAgent(
                self.agent_domain,
                self.address
            )
            
            # Execute via Coinbase AgentKit wallet
            rprint(f"[blue]📝 Executing registration transaction...[/blue]")
            
            # Estimate gas first
            gas_estimate = contract_call.estimate_gas({'from': self.address})
            gas_limit = int(gas_estimate * 1.2)  # Add 20% buffer
            
            rprint(f"[blue]⛽ Gas estimate: {gas_estimate}, using limit: {gas_limit}[/blue]")
            
            # Build transaction
            transaction = contract_call.build_transaction({
                'from': self.address,
                'gas': gas_limit,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'chainId': self.chain_id
            })
            
            # Sign and send via wallet manager
            # Note: This is a simplified approach - in practice, we'd use the AgentKit's transaction methods
            signed_txn = wallet.sign_transaction(transaction)
            # Handle different Web3.py versions
            raw_transaction = signed_txn.raw_transaction if hasattr(signed_txn, 'raw_transaction') else signed_txn.rawTransaction
            tx_hash = self.w3.eth.send_raw_transaction(raw_transaction)
            
            # Wait for confirmation
            rprint(f"[blue]⏳ Waiting for transaction confirmation...[/blue]")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                # Parse the agent ID from events
                agent_id = self._parse_agent_id_from_receipt(receipt)
                
                if agent_id:
                    self.agent_id = agent_id
                    rprint(f"[green]✅ Agent registered successfully with ID: {agent_id}[/green]")
                    return agent_id, tx_hash.hex()
                else:
                    raise Exception("Registration succeeded but couldn't determine agent ID")
            else:
                rprint(f"[red]❌ Transaction failed with status: {receipt.status}[/red]")
                rprint(f"[red]   Gas used: {receipt.gasUsed}[/red]")
                rprint(f"[red]   Transaction hash: {tx_hash.hex()}[/red]")
                raise Exception(f"Registration transaction failed with status {receipt.status}")
                
        except Exception as e:
            rprint(f"[red]❌ Registration failed: {e}[/red]")
            raise
    
    def _get_agent_name_from_domain(self) -> str:
        """Extract agent name from domain"""
        # Simple extraction: alice.chaoschain-genesis-studio.com -> Alice
        if "alice" in self.agent_domain.lower():
            return "Alice"
        elif "bob" in self.agent_domain.lower():
            return "Bob"
        elif "charlie" in self.agent_domain.lower():
            return "Charlie"
        else:
            return "Unknown"
    
    def _parse_agent_id_from_receipt(self, receipt) -> Optional[int]:
        """Parse agent ID from transaction receipt"""
        
        try:
            # Process AgentRegistered events
            logs = self.identity_registry.events.AgentRegistered().process_receipt(receipt)
            if logs and len(logs) > 0:
                return logs[0]['args']['agentId']
        except Exception as e:
            rprint(f"[yellow]⚠️  Could not parse event logs: {e}[/yellow]")
        
        # Fallback: query by address with retry
        for attempt in range(3):
            try:
                time.sleep(1)  # Wait for state to update
                agent_info = self.identity_registry.functions.resolveByAddress(self.address).call()
                if agent_info[0] > 0:
                    return agent_info[0]
            except Exception as e:
                rprint(f"[yellow]⚠️  Retry {attempt + 1}: {e}[/yellow]")
                continue
        
        return None
    
    def request_validation(self, validator_agent_id: int, data_hash: str) -> str:
        """
        Request validation from another agent
        
        Args:
            validator_agent_id: The ID of the validator agent
            data_hash: Hash of the data to be validated
            
        Returns:
            Transaction hash
        """
        
        rprint(f"[blue]🔍 Requesting validation from agent {validator_agent_id}[/blue]")
        
        if not self.wallet_manager:
            raise ValueError("Wallet manager not available")
        
        agent_name = self._get_agent_name_from_domain()
        wallet = self.wallet_manager.wallets.get(agent_name)
        
        if not wallet:
            raise ValueError(f"Wallet not found for agent: {agent_name}")
        
        try:
            # Prepare validation request
            contract_call = self.validation_registry.functions.validationRequest(
                validator_agent_id,
                self.agent_id,
                data_hash
            )
            
            # Build and execute transaction (simplified)
            transaction = contract_call.build_transaction({
                'from': self.address,
                'gas': 150000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'chainId': self.chain_id
            })
            
            signed_txn = wallet.sign_transaction(transaction)
            # Handle different Web3.py versions
            raw_transaction = signed_txn.raw_transaction if hasattr(signed_txn, 'raw_transaction') else signed_txn.rawTransaction
            tx_hash = self.w3.eth.send_raw_transaction(raw_transaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                rprint(f"[green]✅ Validation request submitted[/green]")
                return tx_hash.hex()
            else:
                raise Exception("Validation request transaction failed")
                
        except Exception as e:
            rprint(f"[red]❌ Validation request failed: {e}[/red]")
            raise
    
    def submit_validation_response(self, data_hash: str, response: int) -> str:
        """
        Submit a validation response
        
        Args:
            data_hash: Hash of the validated data
            response: Validation score (0-100)
            
        Returns:
            Transaction hash
        """
        
        rprint(f"[blue]📊 Submitting validation response: {response}/100[/blue]")
        
        if not self.wallet_manager:
            raise ValueError("Wallet manager not available")
        
        agent_name = self._get_agent_name_from_domain()
        wallet = self.wallet_manager.wallets.get(agent_name)
        
        if not wallet:
            raise ValueError(f"Wallet not found for agent: {agent_name}")
        
        try:
            # Prepare validation response
            contract_call = self.validation_registry.functions.validationResponse(
                data_hash,
                response
            )
            
            # Build and execute transaction (simplified)
            transaction = contract_call.build_transaction({
                'from': self.address,
                'gas': 150000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'chainId': self.chain_id
            })
            
            signed_txn = wallet.sign_transaction(transaction)
            # Handle different Web3.py versions
            raw_transaction = signed_txn.raw_transaction if hasattr(signed_txn, 'raw_transaction') else signed_txn.rawTransaction
            tx_hash = self.w3.eth.send_raw_transaction(raw_transaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                rprint(f"[green]✅ Validation response submitted[/green]")
                return tx_hash.hex()
            else:
                raise Exception("Validation response transaction failed")
                
        except Exception as e:
            rprint(f"[red]❌ Validation response failed: {e}[/red]")
            raise
    
    def get_agent_info(self) -> Optional[Dict[str, Any]]:
        """Get agent information from the registry"""
        
        try:
            if self.agent_id:
                agent_info = self.identity_registry.functions.getAgent(self.agent_id).call()
                return {
                    "agent_id": self.agent_id,
                    "domain": agent_info[1],
                    "address": agent_info[2],
                    "is_active": agent_info[3]
                }
        except Exception as e:
            rprint(f"[yellow]⚠️  Could not retrieve agent info: {e}[/yellow]")
        
        return None
