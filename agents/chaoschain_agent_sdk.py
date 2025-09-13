"""
ChaosChain Agent SDK

This SDK provides a unified interface for developers to build agents that integrate
with the ChaosChain protocol, including ERC-8004 identity, x402 payments, IPFS storage,
and the Genesis Studio ecosystem.
"""

import json
import os
from typing import Dict, Any, Optional, Tuple, Union
from datetime import datetime
from rich import print as rprint

from .base_agent_genesis import GenesisBaseAgent
from .server_agent_genesis import GenesisServerAgent
from .validator_agent_genesis import GenesisValidatorAgent
from .simple_wallet_manager import GenesisWalletManager
from .ipfs_storage import GenesisIPFSManager
from .x402_payment_manager import GenesisX402PaymentManager


class ChaosChainAgentSDK:
    """
    ChaosChain Agent SDK - The complete toolkit for building agents on ChaosChain
    
    This SDK abstracts away the complexity of:
    - ERC-8004 identity management
    - x402 payment processing
    - IPFS evidence storage
    - Agent-to-agent communication
    - Genesis Studio integration
    """
    
    def __init__(
        self, 
        agent_name: str,
        agent_domain: str,
        agent_role: str = "client",  # "client", "server", "validator"
        network: str = "base-sepolia"
    ):
        """
        Initialize the ChaosChain Agent SDK
        
        Args:
            agent_name: Human-readable name (Alice, Bob, Charlie, etc.)
            agent_domain: Domain where AgentCard is hosted
            agent_role: Role of the agent (client, server, validator)
            network: Blockchain network to operate on
        """
        self.agent_name = agent_name
        self.agent_domain = agent_domain
        self.agent_role = agent_role
        self.network = network
        
        # Initialize core components
        self._initialize_components()
        
        # Initialize the appropriate agent type
        self._initialize_agent()
        
        rprint(f"[green]🚀 ChaosChain Agent SDK initialized for {agent_name} ({agent_role})[/green]")
        rprint(f"[blue]   Domain: {agent_domain}[/blue]")
        rprint(f"[blue]   Network: {network}[/blue]")
    
    def _initialize_components(self):
        """Initialize all SDK components"""
        
        # Core wallet management
        self.wallet_manager = GenesisWalletManager()
        
        # IPFS storage for evidence
        self.ipfs_manager = GenesisIPFSManager()
        
        # x402 payment processing
        self.payment_manager = GenesisX402PaymentManager(
            wallet_manager=self.wallet_manager,
            network=self.network
        )
        
        # Create or load wallet for this agent
        self.wallet = self.wallet_manager.create_or_load_wallet(self.agent_name)
        self.wallet_address = self.wallet_manager.get_wallet_address(self.agent_name)
    
    def _initialize_agent(self):
        """Initialize the appropriate agent type based on role"""
        
        if self.agent_role == "server":
            self.agent = GenesisServerAgent(
                agent_domain=self.agent_domain,
                wallet_address=self.wallet_address,
                wallet_manager=self.wallet_manager
            )
        elif self.agent_role == "validator":
            self.agent = GenesisValidatorAgent(
                agent_domain=self.agent_domain,
                wallet_address=self.wallet_address,
                wallet_manager=self.wallet_manager
            )
        else:  # client or generic
            self.agent = GenesisBaseAgent(
                agent_domain=self.agent_domain,
                wallet_address=self.wallet_address,
                wallet_manager=self.wallet_manager
            )
    
    # === ERC-8004 Registry Management ===
    
    def register_identity(self) -> Tuple[int, str]:
        """
        Register agent identity on ERC-8004 IdentityRegistry
        
        Returns:
            Tuple of (agent_id, transaction_hash)
        """
        rprint(f"[blue]🆔 Registering {self.agent_name} on ERC-8004 IdentityRegistry[/blue]")
        return self.agent.register_agent()
    
    def get_agent_id(self) -> Optional[int]:
        """Get the agent's on-chain ID"""
        return self.agent.agent_id
    
    def get_agent_info(self) -> Optional[Dict[str, Any]]:
        """Get complete agent information"""
        return self.agent.get_agent_info()
    
    def submit_feedback(self, server_agent_id: int) -> str:
        """
        Submit feedback to ERC-8004 ReputationRegistry
        
        Args:
            server_agent_id: ID of the server agent to provide feedback for
            
        Returns:
            Transaction hash
        """
        rprint(f"[blue]📝 Submitting feedback for agent {server_agent_id} to ReputationRegistry[/blue]")
        
        # Use the reputation registry from the base agent
        if not self.agent.wallet_manager:
            raise ValueError("Wallet manager not available")
        
        agent_name = self.agent._get_agent_name_from_domain()
        wallet = self.agent.wallet_manager.wallets.get(agent_name)
        
        if not wallet:
            raise ValueError(f"Wallet not found for agent: {agent_name}")
        
        try:
            # Prepare feedback submission
            contract_call = self.agent.reputation_registry.functions.acceptFeedback(
                self.agent.agent_id,
                server_agent_id
            )
            
            # Build and execute transaction
            transaction = contract_call.build_transaction({
                'from': self.agent.address,
                'gas': 150000,
                'gasPrice': self.agent.w3.eth.gas_price,
                'nonce': self.agent.w3.eth.get_transaction_count(self.agent.address),
                'chainId': self.agent.chain_id
            })
            
            signed_txn = wallet.sign_transaction(transaction)
            raw_transaction = signed_txn.raw_transaction if hasattr(signed_txn, 'raw_transaction') else signed_txn.rawTransaction
            tx_hash = self.agent.w3.eth.send_raw_transaction(raw_transaction)
            
            # Wait for confirmation
            receipt = self.agent.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                rprint(f"[green]✅ Feedback submitted successfully[/green]")
                return tx_hash.hex()
            else:
                raise Exception("Feedback submission transaction failed")
                
        except Exception as e:
            rprint(f"[red]❌ Feedback submission failed: {e}[/red]")
            raise
    
    # === Payment Management ===
    
    def create_payment_request(
        self,
        to_agent: str,
        amount_usdc: float,
        service_description: str,
        evidence_cid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an x402 payment request
        
        Args:
            to_agent: Name of the receiving agent
            amount_usdc: Amount in USDC
            service_description: Description of service being paid for
            evidence_cid: Optional IPFS CID of related evidence
            
        Returns:
            Payment request data
        """
        return self.payment_manager.create_payment_request(
            from_agent=self.agent_name,
            to_agent=to_agent,
            amount_usdc=amount_usdc,
            service_description=service_description,
            evidence_cid=evidence_cid
        )
    
    def execute_payment(self, payment_request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an x402 payment"""
        return self.payment_manager.execute_payment(payment_request_data)
    
    def pay_for_service(
        self,
        service_provider: str,
        service_type: str,
        base_amount: float,
        quality_multiplier: float = 1.0,
        evidence_cid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Pay for a service using the complete x402 flow
        
        Args:
            service_provider: Agent providing the service
            service_type: Type of service (market_analysis, validation, etc.)
            base_amount: Base payment amount
            quality_multiplier: Quality-based payment multiplier
            evidence_cid: IPFS CID of service evidence
            
        Returns:
            Complete payment flow result
        """
        return self.payment_manager.create_service_payment_flow(
            client_agent=self.agent_name,
            server_agent=service_provider,
            service_type=service_type,
            base_amount=base_amount,
            quality_multiplier=quality_multiplier,
            evidence_cid=evidence_cid
        )
    
    def get_payment_history(self) -> list[Dict[str, Any]]:
        """Get payment history for this agent"""
        return self.payment_manager.get_payment_history(self.agent_name)
    
    # === Evidence & Storage Management ===
    
    def store_evidence(
        self,
        evidence_data: Dict[str, Any],
        evidence_type: str = "analysis"
    ) -> Optional[str]:
        """
        Store evidence on IPFS
        
        Args:
            evidence_data: The evidence data to store
            evidence_type: Type of evidence (analysis, validation, etc.)
            
        Returns:
            IPFS CID if successful
        """
        if evidence_type == "analysis":
            return self.ipfs_manager.store_analysis_report(evidence_data, self.agent.agent_id)
        elif evidence_type == "validation":
            return self.ipfs_manager.store_validation_report(
                evidence_data, 
                self.agent.agent_id, 
                evidence_data.get("data_hash", "0x0")
            )
        else:
            # Generic evidence storage
            return self.ipfs_manager.store_generic_evidence(evidence_data, self.agent.agent_id, evidence_type)
    
    def retrieve_evidence(self, cid: str, evidence_type: str = "analysis") -> Optional[Dict[str, Any]]:
        """
        Retrieve evidence from IPFS
        
        Args:
            cid: IPFS CID to retrieve
            evidence_type: Type of evidence
            
        Returns:
            Evidence data if found
        """
        if evidence_type == "analysis":
            return self.ipfs_manager.retrieve_analysis_report(cid)
        elif evidence_type == "validation":
            return self.ipfs_manager.retrieve_validation_report(cid)
        else:
            return self.ipfs_manager.retrieve_generic_evidence(cid)
    
    def create_evidence_package(
        self,
        work_data: Dict[str, Any],
        payment_receipts: Optional[list[Dict[str, Any]]] = None,
        related_evidence: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive evidence package for PoA verification
        
        Args:
            work_data: The core work/analysis data
            payment_receipts: List of x402 payment receipts
            related_evidence: List of related IPFS CIDs
            
        Returns:
            Complete evidence package
        """
        evidence_package = {
            "chaoschain_evidence_package": {
                "version": "1.0.0",
                "agent_id": self.agent.agent_id,
                "agent_name": self.agent_name,
                "agent_domain": self.agent_domain,
                "created_at": datetime.now().isoformat(),
                "network": self.network
            },
            "work_data": work_data,
            "payment_proofs": payment_receipts or [],
            "related_evidence_cids": related_evidence or [],
            "metadata": {
                "evidence_type": "comprehensive_package",
                "contains_payment_proofs": len(payment_receipts or []) > 0,
                "related_evidence_count": len(related_evidence or [])
            }
        }
        
        return evidence_package
    
    # === Service-Specific Methods ===
    
    def generate_market_analysis(self, symbol: str, timeframe: str = "1d") -> Dict[str, Any]:
        """
        Generate market analysis (for server agents)
        
        Args:
            symbol: Trading symbol to analyze
            timeframe: Analysis timeframe
            
        Returns:
            Market analysis data
        """
        if not isinstance(self.agent, GenesisServerAgent):
            raise ValueError("Market analysis only available for server agents")
        
        return self.agent.generate_market_analysis(symbol, timeframe)
    
    def validate_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate analysis data (for validator agents)
        
        Args:
            analysis_data: Analysis data to validate
            
        Returns:
            Validation result
        """
        if not isinstance(self.agent, GenesisValidatorAgent):
            raise ValueError("Analysis validation only available for validator agents")
        
        return self.agent.validate_analysis(analysis_data)
    
    def request_validation(self, validator_agent_id: int, data_hash: str) -> str:
        """
        Request validation from another agent
        
        Args:
            validator_agent_id: ID of the validator agent
            data_hash: Hash of data to validate
            
        Returns:
            Transaction hash
        """
        return self.agent.request_validation(validator_agent_id, data_hash)
    
    def submit_validation_response(self, data_hash: str, score: int) -> str:
        """
        Submit validation response
        
        Args:
            data_hash: Hash of validated data
            score: Validation score (0-100)
            
        Returns:
            Transaction hash
        """
        return self.agent.submit_validation_response(data_hash, score)
    
    # === Complete Service Workflows ===
    
    def execute_paid_analysis_workflow(
        self,
        client_agent: str,
        symbol: str,
        base_payment: float = 1.0
    ) -> Dict[str, Any]:
        """
        Execute a complete paid analysis workflow
        
        This method demonstrates the full ChaosChain flow:
        1. Generate analysis
        2. Store evidence on IPFS
        3. Receive payment via x402
        4. Create comprehensive evidence package
        
        Args:
            client_agent: Name of the client requesting analysis
            symbol: Trading symbol to analyze
            base_payment: Base payment amount in USDC
            
        Returns:
            Complete workflow result
        """
        if self.agent_role != "server":
            raise ValueError("Paid analysis workflow only available for server agents")
        
        rprint(f"[blue]🔄 Executing paid analysis workflow for {symbol}[/blue]")
        
        # Step 1: Generate analysis
        analysis_data = self.generate_market_analysis(symbol)
        
        # Step 2: Store analysis on IPFS
        analysis_cid = self.store_evidence(analysis_data, "analysis")
        
        # Step 3: Create payment request
        payment_request = self.create_payment_request(
            to_agent=self.agent_name,
            amount_usdc=base_payment,
            service_description=f"Market Analysis - {symbol}",
            evidence_cid=analysis_cid
        )
        
        # Step 4: Wait for payment (in real scenario, this would be event-driven)
        # For demo, we'll simulate the client paying
        
        workflow_result = {
            "workflow_type": "paid_analysis",
            "symbol": symbol,
            "analysis_data": analysis_data,
            "analysis_cid": analysis_cid,
            "payment_request": payment_request,
            "server_agent": self.agent_name,
            "client_agent": client_agent,
            "base_payment": base_payment,
            "completed_at": datetime.now().isoformat()
        }
        
        rprint(f"[green]✅ Paid analysis workflow completed[/green]")
        return workflow_result
    
    def execute_validation_workflow(
        self,
        analysis_cid: str,
        server_agent_id: int,
        validation_payment: float = 0.5
    ) -> Dict[str, Any]:
        """
        Execute a complete validation workflow
        
        Args:
            analysis_cid: IPFS CID of analysis to validate
            server_agent_id: ID of the server agent who created the analysis
            validation_payment: Payment for validation service
            
        Returns:
            Complete validation workflow result
        """
        if self.agent_role != "validator":
            raise ValueError("Validation workflow only available for validator agents")
        
        rprint(f"[blue]🔍 Executing validation workflow for {analysis_cid}[/blue]")
        
        # Step 1: Retrieve analysis from IPFS
        analysis_data = self.retrieve_evidence(analysis_cid, "analysis")
        if not analysis_data:
            raise ValueError(f"Could not retrieve analysis from IPFS: {analysis_cid}")
        
        # Step 2: Perform validation
        validation_result = self.validate_analysis(analysis_data["analysis"])
        
        # Step 3: Store validation report on IPFS
        validation_cid = self.store_evidence(validation_result, "validation")
        
        # Step 4: Submit validation response on-chain
        data_hash = self.agent.calculate_cid_hash(analysis_cid)
        validation_tx = self.submit_validation_response(data_hash, validation_result["overall_score"])
        
        workflow_result = {
            "workflow_type": "validation",
            "analysis_cid": analysis_cid,
            "validation_result": validation_result,
            "validation_cid": validation_cid,
            "validation_tx": validation_tx,
            "validator_agent": self.agent_name,
            "server_agent_id": server_agent_id,
            "validation_payment": validation_payment,
            "completed_at": datetime.now().isoformat()
        }
        
        rprint(f"[green]✅ Validation workflow completed[/green]")
        return workflow_result
    
    # === SDK Utilities ===
    
    def get_sdk_status(self) -> Dict[str, Any]:
        """Get comprehensive SDK status"""
        return {
            "agent_info": {
                "name": self.agent_name,
                "domain": self.agent_domain,
                "role": self.agent_role,
                "agent_id": self.agent.agent_id,
                "wallet_address": self.wallet_address
            },
            "network_info": {
                "network": self.network,
                "connected": True  # Simplified check
            },
            "component_status": {
                "wallet_manager": bool(self.wallet_manager),
                "ipfs_manager": bool(self.ipfs_manager),
                "payment_manager": bool(self.payment_manager),
                "agent": bool(self.agent)
            },
            "payment_stats": self.payment_manager.generate_payment_summary(),
            "sdk_version": "1.0.0",
            "generated_at": datetime.now().isoformat()
        }


# === SDK Factory Functions ===

def create_client_agent(agent_name: str, agent_domain: str, network: str = "base-sepolia") -> ChaosChainAgentSDK:
    """Create a client agent SDK instance"""
    return ChaosChainAgentSDK(agent_name, agent_domain, "client", network)

def create_server_agent(agent_name: str, agent_domain: str, network: str = "base-sepolia") -> ChaosChainAgentSDK:
    """Create a server agent SDK instance"""
    return ChaosChainAgentSDK(agent_name, agent_domain, "server", network)

def create_validator_agent(agent_name: str, agent_domain: str, network: str = "base-sepolia") -> ChaosChainAgentSDK:
    """Create a validator agent SDK instance"""
    return ChaosChainAgentSDK(agent_name, agent_domain, "validator", network)


# === Example Usage ===

if __name__ == "__main__":
    # Example: Create a server agent
    alice_sdk = create_server_agent(
        agent_name="Alice",
        agent_domain="alice.chaoschain-genesis-studio.com"
    )
    
    # Register identity
    agent_id, tx_hash = alice_sdk.register_identity()
    print(f"Alice registered with ID: {agent_id}")
    
    # Generate analysis
    analysis = alice_sdk.generate_market_analysis("BTC")
    print(f"Analysis confidence: {analysis.get('genesis_studio_metadata', {}).get('confidence_score', 'N/A')}%")
    
    # Store evidence
    cid = alice_sdk.store_evidence(analysis, "analysis")
    print(f"Analysis stored at: {cid}")
    
    print("ChaosChain Agent SDK example completed!")
