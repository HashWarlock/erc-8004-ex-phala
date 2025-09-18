#!/usr/bin/env python3
"""
Genesis Studio - Client Task Script (Charlie)

This script simulates a Genesis Studio Client Agent (Charlie) who:
- Discovers Alice's market analysis service
- Monitors validation completion
- Pays Alice in USDC based on validation scores

Usage:
    - Ensure agents are registered by running register_agents.py first.
    - Configure your .env file with all API keys.
    - Make sure Alice and Bob are running (or use genesis_studio.py for full demo).
    - Run the script: python client_task.py
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add agents directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from agents.cli_utils import GenesisStudioCLI
from agents.simple_wallet_manager import GenesisWalletManager
from agents.base_agent_genesis import GenesisBaseAgent

# Load environment variables
load_dotenv()

def main():
    """Main Genesis Studio client task function"""
    cli = GenesisStudioCLI()
    cli.print_banner()
    
    cli.print_phase_header(1, "Client Agent (Charlie)", "Discovering services and making payments")
    
    network = os.getenv('NETWORK', 'base-sepolia')
    print(f"🌍 Connected to network: {network.upper()}")

    try:
        # Initialize Genesis Studio components
        cli.print_step(1, "Initializing Genesis Studio components", "in_progress")
        wallet_manager = GenesisWalletManager()
        cli.print_step(1, "Components initialized", "completed")

        # Load Charlie's wallet and agent
        cli.print_step(2, "Loading Charlie's AgentKit wallet", "in_progress")
        charlie_wallet = wallet_manager.create_or_load_wallet("Charlie")
        charlie_address = wallet_manager.get_wallet_address("Charlie")
        
        charlie = GenesisBaseAgent(
            agent_domain=os.getenv('AGENT_DOMAIN_CHARLIE', 'charlie.chaoschain-genesis-studio.com'),
            wallet_address=charlie_address,
            wallet_manager=wallet_manager
        )
        cli.print_step(2, "Charlie loaded and ready", "completed")

        if not charlie.agent_id:
            cli.print_error("Charlie not registered", "Please run register_agents.py first")
            return
            
        print(f"✅ Genesis Client Agent Charlie ready!")
        print(f"   Agent ID: {charlie.agent_id}")
        print(f"   Wallet: {charlie.address}")
        print(f"   Domain: {charlie.agent_domain}")
        
        print("\n🎯 Charlie is ready to discover services and make payments!")
        print("For the complete commercial demo, run: python genesis_studio.py")

    except Exception as e:
        cli.print_error("Client Agent failed", str(e))

if __name__ == "__main__":
    main()
