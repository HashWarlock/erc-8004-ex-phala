#!/usr/bin/env python3
"""
Genesis Studio - Client Task Script (Charlie) - SDK Version

This script simulates a Genesis Studio Client Agent (Charlie) using the ChaosChain SDK who:
- Discovers Alice's market analysis service
- Creates AP2 intent mandates
- Executes x402 payments for services
- Monitors validation completion

Usage:
    - Install: pip install -i https://test.pypi.org/simple/ chaoschain-sdk==0.1.1
    - Install dependencies: pip install web3 eth-account requests httpx cryptography pyjwt pydantic python-dotenv rich aiohttp python-dateutil x402 crewai
    - Install AP2: pip install git+https://github.com/google-agentic-commerce/AP2.git@main
    - Configure your .env file with all API keys.
    - Make sure Alice and Bob are running (or use genesis_studio.py for full demo).
    - Run the script: python client_task.py
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
from rich import print as rprint

# Import ChaosChain SDK
from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig, AgentRole

# Load environment variables
load_dotenv()

def main():
    """Main Genesis Studio client task function using ChaosChain SDK"""
    
    rprint("[bold blue]🚀 Genesis Studio Client Agent (Charlie) - SDK Version[/bold blue]")
    rprint("=" * 60)
    
    network = os.getenv('NETWORK', 'base-sepolia')
    rprint(f"🌍 Connected to network: {network.upper()}")

    try:
        # Initialize Charlie using ChaosChain SDK
        rprint("\n[blue]🔧 Step 1: Initializing Charlie with ChaosChain SDK[/blue]")
        
        charlie_sdk = ChaosChainAgentSDK(
            agent_name="Charlie",
            agent_domain=os.getenv('AGENT_DOMAIN_CHARLIE', 'charlie.chaoschain-genesis-studio.com'),
            agent_role=AgentRole.CLIENT,
            network=NetworkConfig.BASE_SEPOLIA,
            enable_ap2=True,
            enable_process_integrity=False,  # Client doesn't need process integrity
            enable_payments=True
        )
        
        rprint("[green]✅ Charlie SDK initialized successfully[/green]")
        rprint(f"   Agent: {charlie_sdk.agent_name}")
        rprint(f"   Domain: {charlie_sdk.agent_domain}")
        rprint(f"   Wallet: {charlie_sdk.wallet_address}")
        rprint(f"   Payment Methods: {len(charlie_sdk.get_supported_payment_methods())}")
        
        # Register Charlie's identity if not already registered
        rprint("\n[blue]🔧 Step 2: Registering Charlie's identity[/blue]")
        try:
            agent_id, tx_hash = charlie_sdk.register_identity()
            rprint(f"[green]✅ Charlie registered with Agent ID: {agent_id}[/green]")
            rprint(f"   Transaction: {tx_hash}")
        except Exception as e:
            rprint(f"[yellow]⚠️  Registration: {e}[/yellow]")
            agent_id = charlie_sdk.get_agent_id()
            if agent_id:
                rprint(f"[green]✅ Charlie already registered with Agent ID: {agent_id}[/green]")
        
        # Create AP2 Intent Mandate for market analysis service
        rprint("\n[blue]🔧 Step 3: Creating AP2 intent mandate[/blue]")
        try:
            intent_result = charlie_sdk.create_intent_mandate(
                user_description="Find me a comprehensive BTC market analysis with technical indicators under $10",
                merchants=["Alice", "TrustedAnalytics"],
                skus=["market_analysis", "btc_analysis"],
                requires_refundability=True,
                expiry_minutes=60
            )
            
            if intent_result.success:
                rprint("[green]✅ AP2 intent mandate created successfully[/green]")
                rprint(f"   Intent ID: {intent_result.intent_mandate.intent_id}")
                rprint(f"   Authorized merchants: Alice, TrustedAnalytics")
                rprint(f"   Budget limit: $10")
            else:
                rprint(f"[yellow]⚠️  Intent mandate creation: {intent_result.error}[/yellow]")
        except Exception as e:
            rprint(f"[yellow]⚠️  AP2 intent mandate failed: {e}[/yellow]")
        
        # Create cart mandate for specific service
        rprint("\n[blue]🔧 Step 4: Creating cart mandate for Alice's service[/blue]")
        try:
            cart_result = charlie_sdk.create_cart_mandate(
                cart_id="btc_analysis_001",
                items=[
                    {
                        "name": "BTC Market Analysis",
                        "description": "Comprehensive technical and fundamental analysis",
                        "price": 5.0,
                        "quantity": 1
                    }
                ],
                total_amount=5.0,
                currency="USDC",
                merchant_name="Alice Market Analysis Service",
                expiry_minutes=30
            )
            
            if cart_result.success:
                rprint("[green]✅ Cart mandate created successfully[/green]")
                rprint(f"   Cart ID: {cart_result.cart_mandate.cart_id}")
                rprint(f"   Total: $5.0 USDC")
                rprint(f"   Merchant: Alice Market Analysis Service")
            else:
                rprint(f"[yellow]⚠️  Cart mandate creation: {cart_result.error}[/yellow]")
        except Exception as e:
            rprint(f"[yellow]⚠️  Cart mandate failed: {e}[/yellow]")
        
        # Service discovery and payment loop
        rprint("\n[blue]🔄 Starting service discovery and payment loop...[/blue]")
        rprint("Charlie is now ready to:")
        rprint("• Discover market analysis services")
        rprint("• Execute x402 payments for services")
        rprint("• Monitor validation completion")
        rprint("• Receive verified analysis results")
        
        service_count = 0
        
        while True:
            try:
                rprint(f"\n[bold cyan]--- Service Discovery Cycle {service_count + 1} ---[/bold cyan]")
                
                # Discover Alice's service (simulated)
                rprint("[blue]🔍 Discovering Alice's market analysis service...[/blue]")
                time.sleep(3)
                
                # Execute x402 payment to Alice for market analysis
                rprint("[blue]💳 Executing x402 payment to Alice for market analysis...[/blue]")
                try:
                    payment_result = charlie_sdk.execute_payment(
                        to_agent="Alice",
                        amount=5.0,
                        service_type="market_analysis"
                    )
                    
                    if payment_result.transaction_hash:
                        rprint(f"[green]✅ x402 payment successful[/green]")
                        rprint(f"   Payment ID: {payment_result.payment_id}")
                        rprint(f"   Amount: ${payment_result.amount} {payment_result.currency}")
                        rprint(f"   Transaction: {payment_result.transaction_hash}")
                        rprint(f"   To: {payment_result.to_agent}")
                    else:
                        rprint(f"[yellow]⚠️  x402 payment simulated (no funding)[/yellow]")
                        rprint(f"   Payment ID: {payment_result.payment_id}")
                        rprint(f"   Amount: ${payment_result.amount} {payment_result.currency}")
                        
                except Exception as e:
                    rprint(f"[red]❌ x402 payment failed: {e}[/red]")
                
                # Execute x402 payment to Bob for validation
                rprint("[blue]💳 Executing x402 payment to Bob for validation...[/blue]")
                try:
                    validation_payment = charlie_sdk.execute_payment(
                        to_agent="Bob",
                        amount=0.5,
                        service_type="validation"
                    )
                    
                    if validation_payment.transaction_hash:
                        rprint(f"[green]✅ Validation payment successful[/green]")
                        rprint(f"   Payment ID: {validation_payment.payment_id}")
                        rprint(f"   Amount: ${validation_payment.amount} {validation_payment.currency}")
                        rprint(f"   Transaction: {validation_payment.transaction_hash}")
                    else:
                        rprint(f"[yellow]⚠️  Validation payment simulated (no funding)[/yellow]")
                        rprint(f"   Payment ID: {validation_payment.payment_id}")
                        
                except Exception as e:
                    rprint(f"[red]❌ Validation payment failed: {e}[/red]")
                
                # Check payment history
                rprint("[blue]📊 Checking payment history...[/blue]")
                try:
                    payment_history = charlie_sdk.get_payment_history()
                    rprint(f"[green]✅ Payment history retrieved[/green]")
                    rprint(f"   Total payments: {len(payment_history)}")
                    
                    if payment_history:
                        latest_payment = payment_history[-1]
                        rprint(f"   Latest payment: ${latest_payment.amount} to {latest_payment.to_agent}")
                        
                except Exception as e:
                    rprint(f"[yellow]⚠️  Payment history failed: {e}[/yellow]")
                
                service_count += 1
                
                rprint(f"\n[green]✅ Service discovery cycle {service_count} completed![/green]")
                
                if service_count >= 3:  # Limit demo cycles
                    rprint("[blue]ℹ️  Demo service cycles completed[/blue]")
                    rprint("[yellow]Press Ctrl+C to stop the service.[/yellow]")
                    time.sleep(30)
                else:
                    rprint("Charlie continues to discover and pay for services...")
                    rprint("[yellow]Press Ctrl+C to stop the service.[/yellow]")
                    time.sleep(20)
                
            except KeyboardInterrupt:
                rprint("\n[yellow]🛑 Service discovery interrupted by user.[/yellow]")
                break
            except Exception as e:
                rprint(f"[red]❌ Service cycle {service_count + 1} failed: {e}[/red]")
                import traceback
                traceback.print_exc()
                rprint("Continuing to next cycle...")
                time.sleep(10)

        rprint("\n[blue]🎯 Charlie's service discovery and payment demo completed![/blue]")
        rprint("[green]✅ For the complete commercial demo, run: python genesis_studio.py[/green]")

    except KeyboardInterrupt:
        rprint("\n[yellow]🛑 Genesis Client Agent shutting down.[/yellow]")
    except Exception as e:
        rprint(f"[red]❌ Client Agent failed: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
