#!/usr/bin/env python3
"""
Genesis Studio - Server Agent Runner (Alice) - SDK Version

This script runs the Genesis Studio Server Agent (Alice) using the ChaosChain SDK,
which provides market analysis services using the complete Triple-Verified Stack.

Usage:
    - Install: pip install -i https://test.pypi.org/simple/ chaoschain-sdk==0.1.1
    - Install dependencies: pip install web3 eth-account requests httpx cryptography pyjwt pydantic python-dotenv rich aiohttp python-dateutil x402 crewai
    - Install AP2: pip install git+https://github.com/google-agentic-commerce/AP2.git@main
    - Configure your .env file with all API keys.
    - Run the script: python run_server_agent.py
"""

import os
import sys
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from rich import print as rprint

# Import ChaosChain SDK
from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig, AgentRole

# Load environment variables
load_dotenv()

def main():
    """Main Genesis Studio server agent loop using ChaosChain SDK"""
    
    rprint("[bold blue]🚀 Genesis Studio Server Agent (Alice) - SDK Version[/bold blue]")
    rprint("=" * 60)
    
    network = os.getenv('NETWORK', 'base-sepolia')
    rprint(f"🌍 Connected to network: {network.upper()}")

    try:
        # Initialize Alice using ChaosChain SDK
        rprint("\n[blue]🔧 Step 1: Initializing Alice with ChaosChain SDK[/blue]")
        
        alice_sdk = ChaosChainAgentSDK(
            agent_name="Alice",
            agent_domain=os.getenv('AGENT_DOMAIN_ALICE', 'alice.chaoschain-genesis-studio.com'),
            agent_role=AgentRole.SERVER,
            network=NetworkConfig.BASE_SEPOLIA,
            enable_ap2=True,
            enable_process_integrity=True,
            enable_payments=True
        )
        
        rprint("[green]✅ Alice SDK initialized successfully[/green]")
        rprint(f"   Agent: {alice_sdk.agent_name}")
        rprint(f"   Domain: {alice_sdk.agent_domain}")
        rprint(f"   Wallet: {alice_sdk.wallet_address}")
        rprint(f"   Payment Methods: {len(alice_sdk.get_supported_payment_methods())}")
        
        # Register Alice's identity if not already registered
        rprint("\n[blue]🔧 Step 2: Registering Alice's identity[/blue]")
        try:
            agent_id, tx_hash = alice_sdk.register_identity()
            rprint(f"[green]✅ Alice registered with Agent ID: {agent_id}[/green]")
            rprint(f"   Transaction: {tx_hash}")
        except Exception as e:
            rprint(f"[yellow]⚠️  Registration: {e}[/yellow]")
            agent_id = alice_sdk.get_agent_id()
            if agent_id:
                rprint(f"[green]✅ Alice already registered with Agent ID: {agent_id}[/green]")
        
        # Register analysis function with process integrity
        rprint("\n[blue]🔧 Step 3: Registering analysis function with process integrity[/blue]")
        
        @alice_sdk.process_integrity.register_function
        def generate_market_analysis(symbol: str, timeframe: str = "1d") -> dict:
            """Generate comprehensive market analysis with AI insights"""
            import random
            from datetime import datetime
            
            # Simulate comprehensive market analysis
            current_price = random.uniform(60000, 70000) if symbol == "BTC" else random.uniform(3000, 4000)
            change_24h = random.uniform(-5.0, 5.0)
            
            analysis = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "price_analysis": {
                    "current_price": round(current_price, 2),
                    "24h_change": round(change_24h, 2),
                    "24h_volume": random.randint(1000000, 5000000)
                },
                "technical_analysis": {
                    "trend": "Bullish" if change_24h > 0 else "Bearish",
                    "rsi": round(random.uniform(30, 70), 1),
                    "support_levels": [round(current_price * 0.95, 2), round(current_price * 0.90, 2)],
                    "resistance_levels": [round(current_price * 1.05, 2), round(current_price * 1.10, 2)]
                },
                "recommendations": {
                    "short_term": "Hold" if abs(change_24h) < 2 else ("Buy" if change_24h > 0 else "Sell"),
                    "risk_level": "Medium",
                    "confidence": round(random.uniform(0.75, 0.95), 2)
                },
                "genesis_studio_metadata": {
                    "agent_id": alice_sdk.get_agent_id(),
                    "confidence_score": round(random.uniform(85, 95)),
                    "methodology": "AI-powered multi-factor analysis",
                    "timeframe": timeframe
                }
            }
            
            return analysis
        
        rprint("[green]✅ Analysis function registered with process integrity[/green]")
        
        # Service loop - Alice provides market analysis services
        rprint("\n[blue]🔄 Starting Genesis Studio service loop...[/blue]")
        rprint("Alice is now ready to:")
        rprint("• Generate market analysis reports with process integrity")
        rprint("• Store analysis on IPFS via Pinata")
        rprint("• Request validation from other agents")
        rprint("• Receive x402 payments")
        
        service_count = 0
        
        while True:
            try:
                rprint(f"\n[bold cyan]--- Service Cycle {service_count + 1} ---[/bold cyan]")
                
                # Simulate receiving a service request
                rprint("[blue]⏳ Waiting for service requests...[/blue]")
                time.sleep(5)  # Simulate waiting
                
                # Generate market analysis with process integrity
                rprint("[blue]🔍 Generating BTC market analysis with process integrity...[/blue]")
                
                result, proof = asyncio.run(alice_sdk.execute_with_integrity_proof(
                    "generate_market_analysis",
                    {"symbol": "BTC", "timeframe": "1d"},
                    require_proof=True
                ))
                
                confidence = result.get('genesis_studio_metadata', {}).get('confidence_score', 'N/A')
                rprint(f"[green]✅ Analysis completed (Confidence: {confidence}%)[/green]")
                rprint(f"   Process Integrity Proof ID: {proof.proof_id if proof else 'N/A'}")
                
                # Store on IPFS
                rprint("[blue]📦 Storing analysis on IPFS...[/blue]")
                analysis_cid = alice_sdk.store_evidence(result, "market_analysis")
                
                if analysis_cid:
                    gateway_url = alice_sdk.storage_manager.get_clickable_link(analysis_cid)
                    rprint(f"[green]✅ Analysis stored on IPFS[/green]")
                    rprint(f"   CID: {analysis_cid}")
                    rprint(f"   Gateway: {gateway_url}")
                else:
                    rprint("[red]❌ IPFS storage failed[/red]")
                
                # Request validation (assuming Bob is Agent ID 2)
                if analysis_cid:
                    rprint("[blue]📋 Requesting validation from Bob...[/blue]")
                    try:
                        import hashlib
                        data_hash = "0x" + hashlib.sha256(analysis_cid.encode()).hexdigest()
                        validation_tx = alice_sdk.request_validation(2, data_hash)  # Bob's agent ID
                        rprint(f"[green]✅ Validation requested[/green]")
                        rprint(f"   Data Hash: {data_hash}")
                        rprint(f"   Transaction: {validation_tx}")
                    except Exception as e:
                        rprint(f"[yellow]⚠️  Validation request failed: {e}[/yellow]")
                
                service_count += 1
                
                rprint(f"\n[green]✅ Service cycle {service_count} completed![/green]")
                rprint("Alice continues to provide market analysis services...")
                rprint("[yellow]Press Ctrl+C to stop the service.[/yellow]")
                
                # Wait before next cycle
                time.sleep(30)
                
            except KeyboardInterrupt:
                rprint("\n[yellow]🛑 Service interrupted by user.[/yellow]")
                break
            except Exception as e:
                rprint(f"[red]❌ Service cycle {service_count + 1} failed: {e}[/red]")
                import traceback
                traceback.print_exc()
                rprint("Continuing to next cycle...")
                time.sleep(10)

    except KeyboardInterrupt:
        rprint("\n[yellow]🛑 Genesis Server Agent shutting down.[/yellow]")
    except Exception as e:
        rprint(f"[red]❌ Server Agent failed to start: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
