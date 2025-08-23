#!/usr/bin/env python3
"""
Fund TEE Agents for Testing

This script funds the TEE-derived agent addresses with ETH from
Anvil's default funded account.
"""

import os
import sys
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fund_agents():
    """Fund TEE agent addresses"""
    # Connect to local Anvil
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
    
    if not w3.is_connected():
        print("❌ Failed to connect to Anvil")
        return False
    
    # Anvil's default funded account
    funder_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    funder_account = w3.eth.account.from_key(funder_key)
    
    print(f"💰 Funding from: {funder_account.address}")
    print(f"   Balance: {w3.from_wei(w3.eth.get_balance(funder_account.address), 'ether')} ETH")
    
    # Known TEE agent addresses (from our test output)
    tee_agents = [
        ("Alice", "0x879D3599132A4c74048f0F181c9F755B463d360f"),
        ("Bob", "0xBF1686C7c794Ff2d04c3280BABebfBF8399605eD"),
        ("Charlie", "0x9ae7CA11eB289A72DEF9d5625b3FCa45B52dDe06"),
    ]
    
    # Fund each agent with 1 ETH
    for name, address in tee_agents:
        current_balance = w3.eth.get_balance(address)
        
        if current_balance < w3.to_wei(0.1, 'ether'):
            print(f"\n💸 Funding {name} ({address})...")
            print(f"   Current balance: {w3.from_wei(current_balance, 'ether')} ETH")
            
            # Send 1 ETH
            tx = {
                'from': funder_account.address,
                'to': address,
                'value': w3.to_wei(1, 'ether'),
                'gas': 21000,
                'gasPrice': w3.eth.gas_price,
                'nonce': w3.eth.get_transaction_count(funder_account.address),
            }
            
            signed_tx = w3.eth.account.sign_transaction(tx, funder_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                new_balance = w3.eth.get_balance(address)
                print(f"   ✅ Funded successfully!")
                print(f"   New balance: {w3.from_wei(new_balance, 'ether')} ETH")
            else:
                print(f"   ❌ Funding failed!")
        else:
            print(f"\n✅ {name} already has sufficient funds: {w3.from_wei(current_balance, 'ether')} ETH")
    
    return True

if __name__ == "__main__":
    print("="*60)
    print("FUNDING TEE AGENTS")
    print("="*60)
    
    if fund_agents():
        print("\n✅ All agents funded successfully!")
    else:
        print("\n❌ Funding failed!")
        sys.exit(1)