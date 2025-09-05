#!/usr/bin/env python3
"""
Genesis Studio - Server Agent Runner (Alice)

This script runs the Genesis Studio Server Agent (Alice), which provides 
market analysis services using the complete Genesis Studio stack.

Usage:
    - Ensure agents are registered by running register_agents.py first.
    - Configure your .env file with all API keys.
    - Run the script: python run_server_agent.py
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add agents directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from agents.cli_utils import GenesisStudioCLI
from agents.simple_wallet_manager import GenesisWalletManager
from agents.ipfs_storage import GenesisIPFSManager
from agents.server_agent_genesis import GenesisServerAgent

# Load environment variables
load_dotenv()

def main():
    """Main Genesis Studio server agent loop"""
    cli = GenesisStudioCLI()
    cli.print_banner()
    
    cli.print_phase_header(1, "Server Agent (Alice)", "Running market analysis service with Genesis Studio")
    
    network = os.getenv('NETWORK', 'base-sepolia')
    print(f"🌍 Connected to network: {network.upper()}")

    try:
        # Initialize Genesis Studio components
        cli.print_step(1, "Initializing Genesis Studio components", "in_progress")
        wallet_manager = GenesisWalletManager()
        ipfs_manager = GenesisIPFSManager()
        cli.print_step(1, "Components initialized", "completed")

        # Load Alice's wallet and agent
        cli.print_step(2, "Loading Alice's AgentKit wallet", "in_progress")
        alice_wallet = wallet_manager.create_or_load_wallet("Alice")
        alice_address = wallet_manager.get_wallet_address("Alice")
        
        alice = GenesisServerAgent(
            agent_domain=os.getenv('AGENT_DOMAIN_ALICE', 'alice.chaoschain-genesis-studio.com'),
            wallet_address=alice_address,
            wallet_manager=wallet_manager
        )
        cli.print_step(2, "Alice loaded and ready", "completed")

        if not alice.agent_id:
            cli.print_error("Alice not registered", "Please run register_agents.py first")
            return
            
        print(f"✅ Genesis Server Agent Alice ready!")
        print(f"   Agent ID: {alice.agent_id}")
        print(f"   Wallet: {alice.address}")
        print(f"   Domain: {alice.agent_domain}")
        
        # Service loop - Alice provides market analysis services
        print("\n🔄 Starting Genesis Studio service loop...")
        print("Alice is now ready to:")
        print("• Generate market analysis reports")
        print("• Store analysis on IPFS via Pinata")
        print("• Request validation from Bob")
        print("• Receive payments in USDC")
        
        service_count = 0
        
        while True:
            try:
                print(f"\n--- Service Cycle {service_count + 1} ---")
                
                # Simulate receiving a service request
                cli.print_step(3, "Waiting for service requests", "in_progress")
                time.sleep(5)  # Simulate waiting
                
                # Generate market analysis
                cli.print_step(4, "Generating BTC market analysis", "in_progress")
                analysis_data = alice.generate_market_analysis("BTC")
                cli.print_step(4, f"Analysis completed (Confidence: {analysis_data.get('genesis_studio_metadata', {}).get('confidence_score', 'N/A')}%)", "completed")
                
                # Store on IPFS
                cli.print_step(5, "Storing analysis on IPFS", "in_progress")
                analysis_cid = ipfs_manager.store_analysis_report(analysis_data, alice.agent_id)
                if analysis_cid:
                    gateway_url = ipfs_manager.get_clickable_link(analysis_cid)
                    cli.print_ipfs_upload("analysis.json", analysis_cid, gateway_url)
                    cli.print_step(5, "Analysis stored on IPFS", "completed")
                else:
                    cli.print_step(5, "IPFS storage failed", "failed")
                
                # Request validation (assuming Bob is Agent ID 2)
                if analysis_cid:
                    cli.print_step(6, "Requesting validation from Bob", "in_progress")
                    data_hash = alice.calculate_data_hash(analysis_data)
                    try:
                        validation_tx = alice.request_validation(2, data_hash)  # Bob's agent ID
                        cli.print_validation_request("Bob", data_hash, validation_tx)
                        cli.print_step(6, "Validation requested", "completed")
                    except Exception as e:
                        cli.print_step(6, f"Validation request failed: {e}", "failed")
                
                service_count += 1
                
                print(f"\n✅ Service cycle {service_count} completed!")
                print("Alice continues to provide market analysis services...")
                print("Press Ctrl+C to stop the service.")
                
                # Wait before next cycle
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("\n🛑 Service interrupted by user.")
                break
            except Exception as e:
                cli.print_error(f"Service cycle {service_count + 1} failed", str(e))
                print("Continuing to next cycle...")
                time.sleep(10)

    except KeyboardInterrupt:
        print("\n🛑 Genesis Server Agent shutting down.")
    except Exception as e:
        cli.print_error("Server Agent failed to start", str(e))

if __name__ == "__main__":
    main()
