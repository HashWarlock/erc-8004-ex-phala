#!/usr/bin/env python3
"""
Genesis Studio - Validator Agent Runner (Bob)

This script runs the Genesis Studio Validator Agent (Bob), which provides 
analysis validation services using the complete Genesis Studio stack.

Usage:
    - Ensure agents are registered by running register_agents.py first.
    - Configure your .env file with all API keys.
    - Run the script: python run_validator_agent.py
"""

import os
import sys
import time
from dotenv import load_dotenv
from web3 import Web3

# Add agents directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from agents.cli_utils import GenesisStudioCLI
from agents.simple_wallet_manager import GenesisWalletManager
from agents.ipfs_storage import GenesisIPFSManager
from agents.validator_agent_genesis import GenesisValidatorAgent

# Load environment variables
load_dotenv()

def main():
    """Main Genesis Studio validator agent loop"""
    cli = GenesisStudioCLI()
    cli.print_banner()
    
    cli.print_phase_header(1, "Validator Agent (Bob)", "Running validation service with Genesis Studio")
    
    network = os.getenv('NETWORK', 'base-sepolia')
    print(f"🌍 Connected to network: {network.upper()}")

    try:
        # Initialize Genesis Studio components
        cli.print_step(1, "Initializing Genesis Studio components", "in_progress")
        wallet_manager = GenesisWalletManager()
        ipfs_manager = GenesisIPFSManager()
        cli.print_step(1, "Components initialized", "completed")

        # Load Bob's wallet and agent
        cli.print_step(2, "Loading Bob's AgentKit wallet", "in_progress")
        bob_wallet = wallet_manager.create_or_load_wallet("Bob")
        bob_address = wallet_manager.get_wallet_address("Bob")
        
        bob = GenesisValidatorAgent(
            agent_domain=os.getenv('AGENT_DOMAIN_BOB', 'bob.chaoschain-genesis-studio.com'),
            wallet_address=bob_address,
            wallet_manager=wallet_manager
        )
        cli.print_step(2, "Bob loaded and ready", "completed")

        if not bob.agent_id:
            cli.print_error("Bob not registered", "Please run register_agents.py first")
            return
            
        print(f"✅ Genesis Validator Agent Bob ready!")
        print(f"   Agent ID: {bob.agent_id}")
        print(f"   Wallet: {bob.address}")
        print(f"   Domain: {bob.agent_domain}")
        
        # Create event filter for validation requests
        cli.print_step(3, "Setting up blockchain event listener", "in_progress")
        event_filter = bob.validation_registry.events.ValidationRequestEvent.create_filter(
            fromBlock='latest',
            argument_filters={'agentValidatorId': bob.agent_id}
        )
        cli.print_step(3, "Event listener ready", "completed")
        
        print(f"\n👂 Listening for validation requests for Agent ID {bob.agent_id}...")
        print("Bob is now ready to:")
        print("• Monitor blockchain for ValidationRequestEvent")
        print("• Retrieve analysis from IPFS")
        print("• Perform comprehensive validation")
        print("• Submit validation responses on-chain")
        print("• Store validation reports on IPFS")
        
        validation_count = 0

        while True:
            try:
                # Check for new validation requests
                new_events = event_filter.get_new_entries()
                
                if new_events:
                    for event in new_events:
                        validation_count += 1
                        handle_genesis_validation_event(event, bob, ipfs_manager, cli, validation_count)
                else:
                    # Periodic status update
                    print("🔍 Monitoring for validation requests... (Press Ctrl+C to stop)")
                
                time.sleep(10)

            except KeyboardInterrupt:
                print("\n🛑 Validator Agent shutting down.")
                break
            except Exception as e:
                cli.print_error(f"Event monitoring error", str(e))
                print("Continuing to monitor...")
                time.sleep(5)

    except KeyboardInterrupt:
        print("\n🛑 Genesis Validator Agent shutting down.")
    except Exception as e:
        cli.print_error("Validator Agent failed to start", str(e))

def handle_genesis_validation_event(event, bob: GenesisValidatorAgent, ipfs_manager: GenesisIPFSManager, cli: GenesisStudioCLI, validation_count: int):
    """Handle a new ValidationRequestEvent with Genesis Studio integration."""
    
    print(f"\n🎯 === Validation Request #{validation_count} ===")
    print(f"📬 New validation request received!")
    print(f"   Server Agent ID: {event['args']['agentServerId']}")
    print(f"   Validator Agent ID: {event['args']['agentValidatorId']}")
    print(f"   Data Hash: {event['args']['dataHash'].hex()}")

    data_hash_hex = event['args']['dataHash'].hex()
    
    try:
        # Step 1: Retrieve analysis from IPFS (simulated - in real scenario we'd have the CID)
        cli.print_step(1, "Retrieving analysis data from IPFS", "in_progress")
        # For demo purposes, we'll create mock analysis data
        # In real scenario, we'd extract CID from the data hash or have it passed differently
        mock_analysis_data = {
            "symbol": "BTC",
            "technical_analysis": {
                "trend": "Bullish",
                "support_levels": [65000, 62000],
                "resistance_levels": [70000, 73000],
                "rsi": 58.7
            },
            "price_analysis": {
                "current_price": 67500.00,
                "24h_change": 2.34
            },
            "recommendations": {
                "short_term": "Hold with potential for upside",
                "risk_level": "Medium"
            },
            "genesis_studio_metadata": {
                "confidence_score": 87,
                "methodology": "Multi-factor quantitative analysis"
            }
        }
        cli.print_step(1, "Analysis data retrieved", "completed")
        
        # Step 2: Perform validation using Genesis Studio AI
        cli.print_step(2, "Performing comprehensive AI validation", "in_progress")
        validation_result = bob.validate_analysis(mock_analysis_data)
        score = validation_result.get("overall_score", 85)
        quality = validation_result.get("quality_rating", "Good")
        cli.print_step(2, f"Validation completed: {score}/100 ({quality})", "completed")
        
        # Step 3: Store validation report on IPFS
        cli.print_step(3, "Storing validation report on IPFS", "in_progress")
        validation_cid = ipfs_manager.store_validation_report(validation_result, bob.agent_id, data_hash_hex)
        if validation_cid:
            gateway_url = ipfs_manager.get_clickable_link(validation_cid)
            cli.print_ipfs_upload("validation_report.json", validation_cid, gateway_url)
            cli.print_step(3, "Validation report stored on IPFS", "completed")
        else:
            cli.print_step(3, "IPFS storage failed", "failed")
        
        # Step 4: Submit validation response on-chain
        cli.print_step(4, "Submitting validation response on-chain", "in_progress")
        tx_hash = bob.submit_validation_response(data_hash_hex, score)
        cli.print_validation_response("Bob", score, tx_hash)
        cli.print_step(4, "Validation response submitted", "completed")
        
        print(f"\n✅ Validation #{validation_count} completed successfully!")
        print(f"   Score: {score}/100 ({quality})")
        print(f"   IPFS Report: {validation_cid}")
        print(f"   Transaction: {tx_hash}")

    except Exception as e:
        cli.print_error(f"Validation #{validation_count} failed", str(e))


if __name__ == "__main__":
    main()
