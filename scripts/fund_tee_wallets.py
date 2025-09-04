#!/usr/bin/env python3
"""
Fund TEE-generated wallets based on environment configuration

This script reads the TEE configuration from environment variables
and automatically funds the deterministically-generated addresses.
"""

import os
import sys
from web3 import Web3

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.tee_server_agent import TEEServerAgent
from agents.tee_client_agent import TEEClientAgent
from agents.tee_validator_agent import TEEValidatorAgent


def fund_tee_wallets():
    """Fund TEE wallets based on environment configuration"""
    
    # Check if TEE mode is enabled
    use_tee = os.getenv("USE_TEE_AUTH", "false").lower() == "true"
    if not use_tee:
        print("ℹ️  TEE authentication is not enabled (USE_TEE_AUTH=false)")
        return
    
    print("🔐 Funding TEE-generated wallets")
    print("=" * 50)
    
    # Connect to blockchain
    rpc_url = os.getenv("RPC_URL", "http://localhost:8545")
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    if not w3.is_connected():
        print(f"❌ Failed to connect to blockchain at {rpc_url}")
        print("   Please ensure Anvil is running: flox activate -- anvil")
        sys.exit(1)
    
    print(f"✅ Connected to blockchain at {rpc_url}")
    
    # Create TEE agents with env configuration
    agents = [
        ("Server", TEEServerAgent(
            agent_domain=os.getenv("SERVER_AGENT_DOMAIN", "alice.example.com"),
            salt=os.getenv("SERVER_AGENT_SALT", "server-secret-salt-2024")
        )),
        ("Validator", TEEValidatorAgent(
            agent_domain=os.getenv("VALIDATOR_AGENT_DOMAIN", "bob.example.com"),
            salt=os.getenv("VALIDATOR_AGENT_SALT", "validator-secret-salt-2024")
        )),
        ("Client", TEEClientAgent(
            agent_domain=os.getenv("CLIENT_AGENT_DOMAIN", "charlie.example.com"),
            salt=os.getenv("CLIENT_AGENT_SALT", "client-secret-salt-2024")
        ))
    ]
    
    # Fund each agent
    funded_count = 0
    for name, agent in agents:
        balance = w3.eth.get_balance(agent.address) / 10**18
        print(f"\n{name} Agent:")
        print(f"  Domain: {agent.agent_domain}")
        print(f"  Address: {agent.address}")
        print(f"  Current Balance: {balance:.4f} ETH")
        
        if balance < 0.01:
            try:
                # Fund from Anvil's first account
                tx = {
                    'from': w3.eth.accounts[0],
                    'to': agent.address,
                    'value': w3.to_wei(0.1, 'ether'),
                    'gas': 21000,
                    'gasPrice': w3.eth.gas_price
                }
                tx_hash = w3.eth.send_transaction(tx)
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                
                if receipt.status == 1:
                    new_balance = w3.eth.get_balance(agent.address) / 10**18
                    print(f"  ✅ Funded with 0.1 ETH! New balance: {new_balance:.4f} ETH")
                    funded_count += 1
                else:
                    print(f"  ❌ Funding transaction failed")
            except Exception as e:
                print(f"  ❌ Error funding: {e}")
        else:
            print(f"  ✓ Already has sufficient funds")
    
    print("\n" + "=" * 50)
    if funded_count > 0:
        print(f"✅ Successfully funded {funded_count} TEE wallet(s)")
    else:
        print("✅ All TEE wallets already have sufficient funds")
    
    print("\nTEE wallets are ready for use!")


if __name__ == "__main__":
    fund_tee_wallets()