#!/usr/bin/env python3
"""
Genesis Studio - Validator Agent Runner (Bob) - SDK Version

This script runs the Genesis Studio Validator Agent (Bob) using the ChaosChain SDK,
which provides analysis validation services using the complete Triple-Verified Stack.

Usage:
    - Install: pip install -i https://test.pypi.org/simple/ chaoschain-sdk==0.1.1
    - Install dependencies: pip install web3 eth-account requests httpx cryptography pyjwt pydantic python-dotenv rich aiohttp python-dateutil x402 crewai
    - Install AP2: pip install git+https://github.com/google-agentic-commerce/AP2.git@main
    - Configure your .env file with all API keys.
    - Run the script: python run_validator_agent.py
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
    """Main Genesis Studio validator agent loop using ChaosChain SDK"""
    
    rprint("[bold blue]🚀 Genesis Studio Validator Agent (Bob) - SDK Version[/bold blue]")
    rprint("=" * 60)
    
    network = os.getenv('NETWORK', 'base-sepolia')
    rprint(f"🌍 Connected to network: {network.upper()}")

    try:
        # Initialize Bob using ChaosChain SDK
        rprint("\n[blue]🔧 Step 1: Initializing Bob with ChaosChain SDK[/blue]")
        
        bob_sdk = ChaosChainAgentSDK(
            agent_name="Bob",
            agent_domain=os.getenv('AGENT_DOMAIN_BOB', 'bob.chaoschain-genesis-studio.com'),
            agent_role=AgentRole.VALIDATOR,
            network=NetworkConfig.BASE_SEPOLIA,
            enable_ap2=True,
            enable_process_integrity=True,
            enable_payments=True
        )
        
        rprint("[green]✅ Bob SDK initialized successfully[/green]")
        rprint(f"   Agent: {bob_sdk.agent_name}")
        rprint(f"   Domain: {bob_sdk.agent_domain}")
        rprint(f"   Wallet: {bob_sdk.wallet_address}")
        rprint(f"   Payment Methods: {len(bob_sdk.get_supported_payment_methods())}")
        
        # Register Bob's identity if not already registered
        rprint("\n[blue]🔧 Step 2: Registering Bob's identity[/blue]")
        try:
            agent_id, tx_hash = bob_sdk.register_identity()
            rprint(f"[green]✅ Bob registered with Agent ID: {agent_id}[/green]")
            rprint(f"   Transaction: {tx_hash}")
        except Exception as e:
            rprint(f"[yellow]⚠️  Registration: {e}[/yellow]")
            agent_id = bob_sdk.get_agent_id()
            if agent_id:
                rprint(f"[green]✅ Bob already registered with Agent ID: {agent_id}[/green]")
        
        # Register validation function with process integrity
        rprint("\n[blue]🔧 Step 3: Registering validation function with process integrity[/blue]")
        
        @bob_sdk.process_integrity.register_function
        def validate_market_analysis(analysis_data: dict) -> dict:
            """Validate market analysis with comprehensive scoring"""
            import random
            from datetime import datetime
            
            # Extract analysis components for validation
            price_analysis = analysis_data.get('price_analysis', {})
            technical_analysis = analysis_data.get('technical_analysis', {})
            recommendations = analysis_data.get('recommendations', {})
            metadata = analysis_data.get('genesis_studio_metadata', {})
            
            # Scoring logic
            completeness_score = 0
            if price_analysis: completeness_score += 25
            if technical_analysis: completeness_score += 25
            if recommendations: completeness_score += 25
            if metadata: completeness_score += 25
            
            # Accuracy scoring (simulated)
            accuracy_score = random.randint(80, 95)
            
            # Methodology scoring
            methodology_score = random.randint(85, 95)
            
            # Confidence scoring
            confidence_score = random.randint(80, 90)
            
            # Overall score
            overall_score = round((completeness_score + accuracy_score + methodology_score + confidence_score) / 4)
            
            validation_result = {
                "validation_timestamp": datetime.now().isoformat(),
                "validator_agent_id": bob_sdk.get_agent_id(),
                "overall_score": overall_score,
                "completeness_score": completeness_score,
                "accuracy_score": accuracy_score,
                "methodology_score": methodology_score,
                "confidence_score": confidence_score,
                "quality_rating": "Excellent" if overall_score >= 90 else "Good" if overall_score >= 80 else "Fair",
                "validation_summary": f"Analysis shows {overall_score}% quality with comprehensive coverage",
                "validator": "Bob (ChaosChain SDK)",
                "validation_details": {
                    "price_analysis_present": bool(price_analysis),
                    "technical_analysis_present": bool(technical_analysis),
                    "recommendations_present": bool(recommendations),
                    "metadata_present": bool(metadata)
                }
            }
            
            return validation_result
        
        rprint("[green]✅ Validation function registered with process integrity[/green]")
        
        # Create x402 paywall server for validation services
        rprint("\n[blue]🔧 Step 4: Setting up x402 paywall server[/blue]")
        try:
            paywall_server = bob_sdk.create_x402_paywall_server(port=8402)
            
            @paywall_server.require_payment(amount=0.5, description="Market Analysis Validation")
            def validate_analysis_service(analysis_data):
                """Paid validation service endpoint"""
                result, proof = asyncio.run(bob_sdk.execute_with_integrity_proof(
                    "validate_market_analysis",
                    {"analysis_data": analysis_data},
                    require_proof=True
                ))
                return {
                    "validation_result": result,
                    "process_integrity_proof": proof.proof_id if proof else None
                }
            
            rprint("[green]✅ x402 paywall server ready on port 8402[/green]")
        except Exception as e:
            rprint(f"[yellow]⚠️  Paywall server setup failed: {e}[/yellow]")
        
        # Service loop - Bob provides validation services
        rprint("\n[blue]🔄 Starting Genesis Studio validation service...[/blue]")
        rprint("Bob is now ready to:")
        rprint("• Monitor for validation requests")
        rprint("• Validate analysis with process integrity")
        rprint("• Store validation reports on IPFS")
        rprint("• Receive x402 payments for validation services")
        
        validation_count = 0

        # Simulate validation service loop
        while True:
            try:
                rprint(f"\n[bold cyan]--- Validation Service Cycle {validation_count + 1} ---[/bold cyan]")
                
                # Monitor for validation requests (simulated)
                rprint("[blue]👂 Monitoring for validation requests...[/blue]")
                time.sleep(10)  # Simulate monitoring
                
                # Simulate receiving a validation request
                if validation_count < 3:  # Limit demo cycles
                    rprint("[blue]📬 Simulating validation request received...[/blue]")
                    
                    # Mock analysis data for validation
                    mock_analysis = {
                        "symbol": "BTC",
                        "price_analysis": {
                            "current_price": 67500.00,
                            "24h_change": 2.34
                        },
                        "technical_analysis": {
                            "trend": "Bullish",
                            "rsi": 58.7
                        },
                        "recommendations": {
                            "short_term": "Hold",
                            "risk_level": "Medium"
                        },
                        "genesis_studio_metadata": {
                            "confidence_score": 87
                        }
                    }
                    
                    # Perform validation with process integrity
                    rprint("[blue]🔍 Performing validation with process integrity...[/blue]")
                    
                    result, proof = asyncio.run(bob_sdk.execute_with_integrity_proof(
                        "validate_market_analysis",
                        {"analysis_data": mock_analysis},
                        require_proof=True
                    ))
                    
                    score = result.get('overall_score', 0)
                    quality = result.get('quality_rating', 'Unknown')
                    rprint(f"[green]✅ Validation completed: {score}/100 ({quality})[/green]")
                    rprint(f"   Process Integrity Proof ID: {proof.proof_id if proof else 'N/A'}")
                    
                    # Store validation report on IPFS
                    rprint("[blue]📦 Storing validation report on IPFS...[/blue]")
                    validation_cid = bob_sdk.store_evidence(result, "validation_report")
                    
                    if validation_cid:
                        gateway_url = bob_sdk.storage_manager.get_clickable_link(validation_cid)
                        rprint(f"[green]✅ Validation report stored on IPFS[/green]")
                        rprint(f"   CID: {validation_cid}")
                        rprint(f"   Gateway: {gateway_url}")
                    else:
                        rprint("[red]❌ IPFS storage failed[/red]")
                    
                    # Submit validation response on-chain
                    rprint("[blue]📋 Submitting validation response on-chain...[/blue]")
                    try:
                        import hashlib
                        data_hash = "0x" + hashlib.sha256(str(mock_analysis).encode()).hexdigest()
                        validation_tx = bob_sdk.submit_validation_response(data_hash, score)
                        rprint(f"[green]✅ Validation response submitted[/green]")
                        rprint(f"   Transaction: {validation_tx}")
                    except Exception as e:
                        rprint(f"[yellow]⚠️  Validation response failed: {e}[/yellow]")
                    
                        validation_count += 1
                    
                    rprint(f"\n[green]✅ Validation #{validation_count} completed successfully![/green]")
                    rprint(f"   Score: {score}/100 ({quality})")
                    rprint(f"   IPFS Report: {validation_cid}")
                else:
                    rprint("[blue]ℹ️  Demo validation cycles completed[/blue]")
                    rprint("[yellow]Press Ctrl+C to stop the service.[/yellow]")
                    time.sleep(30)

            except KeyboardInterrupt:
                rprint("\n[yellow]🛑 Validation service interrupted by user.[/yellow]")
                break
            except Exception as e:
                rprint(f"[red]❌ Validation cycle {validation_count + 1} failed: {e}[/red]")
                import traceback
                traceback.print_exc()
                rprint("Continuing to monitor...")
                time.sleep(5)

    except KeyboardInterrupt:
        rprint("\n[yellow]🛑 Genesis Validator Agent shutting down.[/yellow]")
    except Exception as e:
        rprint(f"[red]❌ Validator Agent failed to start: {e}[/red]")
        import traceback
        traceback.print_exc()



if __name__ == "__main__":
    main()
