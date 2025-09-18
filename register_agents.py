#!/usr/bin/env python3
"""
Genesis Studio - Agent Registration Script

This script registers the demo agents (Alice, Bob, Charlie) using Genesis Studio
AgentKit wallets on the configured blockchain network.

Usage:
    - Configure your settings in the .env file (API keys, network, etc.)
    - Run the script: python register_agents.py
    - Fund the displayed wallet addresses with Base Sepolia ETH
    - Run again to complete registration
"""

import os
import sys
from dotenv import load_dotenv

# Add agents directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from agents.cli_utils import GenesisStudioCLI
from agents.simple_wallet_manager import GenesisWalletManager
from agents.server_agent_genesis import GenesisServerAgent
from agents.validator_agent_genesis import GenesisValidatorAgent
from agents.base_agent_genesis import GenesisBaseAgent

# Load environment variables
load_dotenv()

def main():
    """Main registration function using Genesis Studio"""
    cli = GenesisStudioCLI()
    cli.print_banner()
    
    cli.print_phase_header(1, "Agent Registration", "Creating AgentKit wallets and registering on ERC-8004")
    
    network = os.getenv('NETWORK', 'base-sepolia')
    print(f"🌍 Targeting network: {network.upper()}")

    try:
        # Initialize wallet manager
        cli.print_step(1, "Initializing Genesis Studio wallet manager", "in_progress")
        wallet_manager = GenesisWalletManager()
        cli.print_step(1, "Wallet manager initialized", "completed")

        # Create/load wallets for all agents
        cli.print_step(2, "Creating AgentKit wallets for Alice, Bob, Charlie", "in_progress")
        alice_wallet = wallet_manager.create_or_load_wallet("Alice")
        bob_wallet = wallet_manager.create_or_load_wallet("Bob")
        charlie_wallet = wallet_manager.create_or_load_wallet("Charlie")
        cli.print_step(2, "AgentKit wallets ready", "completed")

        # Display wallet addresses for funding
        wallet_manager.display_wallet_summary()
        
        # Check if wallets need funding
        alice_balance = wallet_manager.get_wallet_balance("Alice", "eth")
        bob_balance = wallet_manager.get_wallet_balance("Bob", "eth")
        charlie_balance = wallet_manager.get_wallet_balance("Charlie", "eth")
        
        if alice_balance < 0.001 or bob_balance < 0.001 or charlie_balance < 0.001:
            cli.print_warning("⚠️  Some wallets have low ETH balance!")
            print("Please fund the wallet addresses shown above with Base Sepolia ETH:")
            print("• Base Sepolia Faucet: https://faucet.quicknode.com/base/sepolia")
            print("• Send ~0.002 ETH to each address (minimal for gas fees)")
            print("• Also send ~10 USDC to Charlie's address for payments")
            print("• Circle USDC Faucet: https://faucet.circle.com/ (select Base Sepolia)")
            print("\nRun this script again after funding.")
            return

        # Try to fund from faucet (may not work for all networks)
        cli.print_step(3, "Attempting to fund wallets from testnet faucet", "in_progress")
        wallet_manager.fund_wallet_from_faucet("Alice")
        wallet_manager.fund_wallet_from_faucet("Bob") 
        wallet_manager.fund_wallet_from_faucet("Charlie")
        cli.print_step(3, "Faucet funding attempted", "completed")

        # Initialize Genesis agents with wallets
        cli.print_step(4, "Initializing Genesis Studio agents", "in_progress")
        
        alice = GenesisServerAgent(
            agent_domain=os.getenv('AGENT_DOMAIN_ALICE', 'alice.chaoschain-genesis-studio.com'),
            wallet_address=wallet_manager.get_wallet_address("Alice"),
            wallet_manager=wallet_manager
        )
        
        bob = GenesisValidatorAgent(
            agent_domain=os.getenv('AGENT_DOMAIN_BOB', 'bob.chaoschain-genesis-studio.com'),
            wallet_address=wallet_manager.get_wallet_address("Bob"),
            wallet_manager=wallet_manager
        )
        
        charlie = GenesisBaseAgent(
            agent_domain=os.getenv('AGENT_DOMAIN_CHARLIE', 'charlie.chaoschain-genesis-studio.com'),
            wallet_address=wallet_manager.get_wallet_address("Charlie"),
            wallet_manager=wallet_manager
        )
        
        cli.print_step(4, "Genesis agents initialized", "completed")
        
        agents = {"Alice": alice, "Bob": bob, "Charlie": charlie}

        # Register each agent on-chain
        cli.print_step(5, "Registering agents on ERC-8004 IdentityRegistry", "in_progress")
        registration_results = {}
        
        for name, agent in agents.items():
            try:
                if agent.agent_id:
                    print(f"✅ {name} already registered with Agent ID: {agent.agent_id}")
                    registration_results[name] = {"agent_id": agent.agent_id, "status": "already_registered"}
                else:
                    agent_id, tx_hash = agent.register_agent()
                    cli.print_agent_registration(name, agent_id, agent.address, tx_hash)
                    registration_results[name] = {"agent_id": agent_id, "tx_hash": tx_hash, "status": "newly_registered"}
            except Exception as e:
                cli.print_error(f"Failed to register {name}", str(e))
                registration_results[name] = {"error": str(e), "status": "failed"}

        cli.print_step(5, "Agent registration completed", "completed")

        # Summary
        successful_registrations = sum(1 for result in registration_results.values() if "agent_id" in result)
        
        if successful_registrations == 3:
            print("\n🎉 All agents registered successfully!")
            print("You can now run genesis_studio.py for the full commercial demo.")
        else:
            print(f"\n⚠️  {successful_registrations}/3 agents registered successfully.")
            print("Please check the error messages above for specific issues.")
            print("Note: Wallets appear to be properly funded - this may be a contract interaction issue.")

    except Exception as e:
        cli.print_error("Registration process failed", str(e))
        print("Please check your .env configuration and ensure all required API keys are set.")

if __name__ == "__main__":
    main()
