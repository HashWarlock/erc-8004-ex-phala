"""
Genesis Studio - Client Agent (Charlie)

This agent demonstrates a Client Agent role in the ERC-8004 ecosystem.
It uses the ChaosChain SDK to interact with server and validator agents,
make payments, and manage the complete agent-to-agent commerce workflow.
"""

import json
from datetime import datetime
from typing import Dict, Any, List
from rich import print as rprint

# Import ChaosChain SDK components
try:
    from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig
    from chaoschain_sdk.types import AgentRole
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    # Create dummy classes for type hints when SDK is not available
    class NetworkConfig:
        BASE_SEPOLIA = "base-sepolia"
    class AgentRole:
        CLIENT = "client"
    rprint("[red]❌ ChaosChain SDK not available. Please install: pip install chaoschain-sdk[/red]")

class GenesisClientAgent:
    """Enhanced Client Agent for Genesis Studio using ChaosChain SDK"""
    
    def __init__(self, agent_name: str, agent_domain: str, agent_role: AgentRole = AgentRole.CLIENT,
                 network: NetworkConfig = NetworkConfig.BASE_SEPOLIA,
                 enable_ap2: bool = True, enable_process_integrity: bool = False):
        """
        Initialize the Genesis Client Agent with ChaosChain SDK
        
        Args:
            agent_name: Name of the agent (e.g., "Charlie")
            agent_domain: Domain where agent's card is hosted
            agent_role: Role of the agent (defaults to CLIENT)
            network: Blockchain network to use
            enable_ap2: Enable AP2 integration for intent verification
            enable_process_integrity: Enable process integrity (typically False for clients)
        """
        if not SDK_AVAILABLE:
            raise ImportError("ChaosChain SDK is required for GenesisClientAgent")
        
        self.agent_name = agent_name
        self.agent_domain = agent_domain
        self.agent_role = agent_role
        self.network = network
        
        # Initialize ChaosChain SDK with AP2 enabled
        self.sdk = ChaosChainAgentSDK(
            agent_name=agent_name,
            agent_domain=agent_domain,
            agent_role=agent_role,
            network=network,
            enable_ap2=enable_ap2,
            enable_process_integrity=enable_process_integrity
        )
        
        # Store service history
        self.service_history = []
        self.payment_history = []
        
        rprint(f"[green]🤖 Genesis Client Agent ({agent_name}) initialized with ChaosChain SDK[/green]")
        rprint(f"[blue]   Domain: {agent_domain}[/blue]")
        rprint(f"[blue]   Wallet: {self.sdk.wallet_address}[/blue]")
        rprint(f"[blue]   Network: {network.value}[/blue]")
    
    def register_identity(self) -> str:
        """Register agent identity on ERC-8004 registry"""
        try:
            agent_id = self.sdk.register_identity()
            rprint(f"[green]✅ Client agent registered with ID: {agent_id}[/green]")
            return agent_id
        except Exception as e:
            rprint(f"[red]❌ Registration failed: {e}[/red]")
            raise
    
    def create_shopping_intent(self, item_type: str, color: str, budget: float, 
                             premium_tolerance: float = 0.20) -> Dict[str, Any]:
        """
        Create an AP2 intent mandate for smart shopping
        
        Args:
            item_type: Type of item to shop for
            color: Preferred color
            budget: Maximum budget
            premium_tolerance: Acceptable premium for preferred options
            
        Returns:
            Intent mandate details
        """
        try:
            # Create AP2 intent mandate
            intent_result = self.sdk.create_intent_mandate(
                user_description=f"Find me the best {item_type} in {color}, willing to pay up to {premium_tolerance*100}% premium for the right color. Price limit: ${budget}, quality threshold: good, auto-purchase enabled",
                merchants=None,  # Allow any merchant
                skus=None,       # Allow any SKU
                requires_refundability=False,
                expiry_minutes=60
            )
            
            if intent_result.success:
                rprint(f"[green]✅ Shopping intent created for {item_type}[/green]")
                rprint(f"[blue]   Budget: ${budget}, Color: {color}[/blue]")
                return {
                    "intent_mandate": intent_result.intent_mandate,
                    "item_type": item_type,
                    "color": color,
                    "budget": budget,
                    "premium_tolerance": premium_tolerance
                }
            else:
                raise Exception(f"Intent creation failed: {intent_result.error}")
                
        except Exception as e:
            rprint(f"[red]❌ Intent creation failed: {e}[/red]")
            raise
    
    def create_shopping_cart(self, intent_data: Dict[str, Any], estimated_price: float) -> Dict[str, Any]:
        """
        Create an AP2 cart mandate for the shopping intent
        
        Args:
            intent_data: Intent mandate data
            estimated_price: Estimated price for the service
            
        Returns:
            Cart mandate details
        """
        try:
            cart_id = f"cart_{intent_data['item_type'].lower()}_{int(datetime.now().timestamp())}"
            
            # Create cart items
            items = [{
                "name": f"Smart Shopping Service - {intent_data['item_type']}",
                "price": estimated_price,
                "quantity": 1,
                "description": f"AI-powered shopping for {intent_data['item_type']} in {intent_data['color']}"
            }]
            
            # Create AP2 cart mandate
            cart_result = self.sdk.create_cart_mandate(
                cart_id=cart_id,
                items=items,
                total_amount=estimated_price,
                currency="USDC",
                merchant_name="ChaosChain Genesis Studio",
                expiry_minutes=15
            )
            
            if cart_result.success:
                rprint(f"[green]✅ Shopping cart created: {cart_id}[/green]")
                rprint(f"[blue]   Total: ${estimated_price} USDC[/blue]")
                return {
                    "cart_mandate": cart_result.cart_mandate,
                    "cart_id": cart_id,
                    "items": items,
                    "total_amount": estimated_price,
                    "jwt_token": cart_result.jwt_token
                }
            else:
                raise Exception(f"Cart creation failed: {cart_result.error}")
                
        except Exception as e:
            rprint(f"[red]❌ Cart creation failed: {e}[/red]")
            raise
    
    def request_shopping_service(self, server_agent_domain: str, intent_data: Dict[str, Any], 
                               payment_amount: float) -> Dict[str, Any]:
        """
        Request shopping service from a server agent and pay for it
        
        Args:
            server_agent_domain: Domain of the server agent to request from
            intent_data: Shopping intent data
            payment_amount: Amount to pay for the service
            
        Returns:
            Service result and payment proof
        """
        try:
            rprint(f"[cyan]🛒 Requesting shopping service from {server_agent_domain}[/cyan]")
            
            # Create x402 payment for the shopping service
            payment_proof = self.sdk.execute_payment(
                to_agent=server_agent_domain.split('.')[0],  # Extract agent name
                amount=payment_amount,
                currency="USDC",
                service_description=f"Smart Shopping Service - {intent_data['item_type']}"
            )
            
            # Store payment in history
            self.payment_history.append({
                "service": "smart_shopping",
                "amount": payment_amount,
                "to_agent": server_agent_domain,
                "payment_proof": payment_proof,
                "timestamp": datetime.now().isoformat()
            })
            
            rprint(f"[green]✅ Payment successful: {payment_proof.transaction_hash}[/green]")
            rprint(f"[blue]   Amount: ${payment_amount} USDC[/blue]")
            
            return {
                "payment_proof": payment_proof,
                "service_requested": "smart_shopping",
                "intent_data": intent_data
            }
            
        except Exception as e:
            rprint(f"[red]❌ Service request failed: {e}[/red]")
            raise
    
    def request_validation_service(self, validator_agent_domain: str, analysis_cid: str, 
                                 payment_amount: float) -> Dict[str, Any]:
        """
        Request validation service from a validator agent and pay for it
        
        Args:
            validator_agent_domain: Domain of the validator agent
            analysis_cid: IPFS CID of the analysis to validate
            payment_amount: Amount to pay for validation
            
        Returns:
            Validation result and payment proof
        """
        try:
            rprint(f"[cyan]🔍 Requesting validation service from {validator_agent_domain}[/cyan]")
            
            # Create x402 payment for the validation service
            payment_proof = self.sdk.execute_payment(
                to_agent=validator_agent_domain.split('.')[0],  # Extract agent name
                amount=payment_amount,
                currency="USDC",
                service_description="Analysis Validation Service"
            )
            
            # Store payment in history
            self.payment_history.append({
                "service": "validation",
                "amount": payment_amount,
                "to_agent": validator_agent_domain,
                "payment_proof": payment_proof,
                "analysis_cid": analysis_cid,
                "timestamp": datetime.now().isoformat()
            })
            
            rprint(f"[green]✅ Validation payment successful: {payment_proof.transaction_hash}[/green]")
            rprint(f"[blue]   Amount: ${payment_amount} USDC[/blue]")
            
            return {
                "payment_proof": payment_proof,
                "service_requested": "validation",
                "analysis_cid": analysis_cid
            }
            
        except Exception as e:
            rprint(f"[red]❌ Validation request failed: {e}[/red]")
            raise
    
    def get_service_history(self) -> List[Dict[str, Any]]:
        """Get the complete service interaction history"""
        return self.service_history
    
    def get_payment_summary(self) -> Dict[str, Any]:
        """Get a summary of all payments made"""
        if not self.payment_history:
            return {
                "total_payments": 0,
                "total_amount": 0,
                "services_used": []
            }
        
        total_amount = sum(payment["amount"] for payment in self.payment_history)
        services_used = list(set(payment["service"] for payment in self.payment_history))
        
        return {
            "total_payments": len(self.payment_history),
            "total_amount": total_amount,
            "services_used": services_used,
            "payment_history": self.payment_history,
            "x402_summary": self.sdk.get_x402_payment_summary() if hasattr(self.sdk, 'get_x402_payment_summary') else {}
        }
    
    def display_agent_info(self):
        """Display comprehensive agent information"""
        rprint("\n[bold cyan]🤖 Genesis Client Agent Information[/bold cyan]")
        rprint(f"[blue]Agent Name:[/blue] {self.agent_name}")
        rprint(f"[blue]Agent Domain:[/blue] {self.agent_domain}")
        rprint(f"[blue]Wallet Address:[/blue] {self.sdk.wallet_address}")
        rprint(f"[blue]Network:[/blue] {self.network.value}")
        rprint(f"[blue]Agent ID:[/blue] {self.sdk.get_agent_id() if hasattr(self.sdk, 'get_agent_id') else 'Not registered'}")
        
        # Payment capabilities
        rprint(f"[blue]Payment Methods:[/blue] {len(self.sdk.get_supported_payment_methods()) if hasattr(self.sdk, 'get_supported_payment_methods') else 'Multiple'} supported")
        rprint(f"[blue]x402 Support:[/blue] ✅ Enabled")
        rprint(f"[blue]AP2 Support:[/blue] ✅ Enabled")
        
        # Service history
        if self.payment_history:
            rprint(f"[blue]Services Used:[/blue] {len(self.payment_history)} transactions")
            total_spent = sum(p["amount"] for p in self.payment_history)
            rprint(f"[blue]Total Spent:[/blue] ${total_spent} USDC")
