#!/usr/bin/env python3
"""
ERC-8004 Registry Deployment Script

This script deploys the three core ERC-8004 registry contracts:
- IdentityRegistry
- ReputationRegistry  
- ValidationRegistry

Usage:
    python scripts/deploy.py
"""

import json
import os
from pathlib import Path
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_contract_abi(contract_name: str) -> dict:
    """Load contract ABI from compiled artifacts"""
    abi_path = Path(f"contracts/out/{contract_name}.sol/{contract_name}.json")
    
    if not abi_path.exists():
        raise FileNotFoundError(f"Contract ABI not found: {abi_path}")
    
    with open(abi_path, 'r') as f:
        artifact = json.load(f)
        return artifact['abi']

def load_contract_bytecode(contract_name: str) -> str:
    """Load contract bytecode from compiled artifacts"""
    abi_path = Path(f"contracts/out/{contract_name}.sol/{contract_name}.json")
    
    if not abi_path.exists():
        raise FileNotFoundError(f"Contract artifact not found: {abi_path}")
    
    with open(abi_path, 'r') as f:
        artifact = json.load(f)
        return artifact['bytecode']['object']

def deploy_contract(w3: Web3, account, contract_name: str, constructor_args=None) -> tuple:
    """Deploy a contract and return address and transaction hash"""
    print(f"\n📦 Deploying {contract_name}...")
    
    # Load contract ABI and bytecode
    abi = load_contract_abi(contract_name)
    bytecode = load_contract_bytecode(contract_name)
    
    # Create contract instance
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Build constructor transaction
    if constructor_args:
        constructor = contract.constructor(*constructor_args)
    else:
        constructor = contract.constructor()
    
    # Estimate gas
    gas_estimate = constructor.estimate_gas({'from': account.address})
    print(f"   Gas estimate: {gas_estimate:,}")
    
    # Build transaction
    transaction = constructor.build_transaction({
        'from': account.address,
        'gas': int(gas_estimate * 1.2),  # Add 20% buffer
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(account.address),
    })
    
    # Sign and send transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=account.key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    
    print(f"   Transaction hash: {tx_hash.hex()}")
    
    # Wait for confirmation
    print("   Waiting for confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt.status == 1:
        print(f"   ✅ {contract_name} deployed at: {receipt.contractAddress}")
        return receipt.contractAddress, tx_hash.hex()
    else:
        raise Exception(f"❌ {contract_name} deployment failed!")

def save_deployment_info(addresses: dict, tx_hashes: dict):
    """Save deployment information to files"""
    deployment_info = {
        'contracts': addresses,
        'transactions': tx_hashes,
        'network': {
            'chain_id': int(os.getenv('CHAIN_ID', 31337)),
            'rpc_url': os.getenv('RPC_URL', 'http://127.0.0.1:8545')
        }
    }
    
    # Save to JSON file
    with open('deployment.json', 'w') as f:
        json.dump(deployment_info, f, indent=2)
    
    # Update .env file with addresses
    env_updates = []
    for name, address in addresses.items():
        env_var = f"{name.upper()}_ADDRESS"
        env_updates.append(f"{env_var}={address}")
    
    print(f"\n📝 Deployment complete! Add these to your .env file:")
    for update in env_updates:
        print(f"   {update}")

def main():
    """Main deployment function"""
    print("🚀 ERC-8004 Registry Deployment")
    print("=" * 50)
    
    # Connect to blockchain
    rpc_url = os.getenv('RPC_URL', 'http://127.0.0.1:8545')
    private_key = os.getenv('PRIVATE_KEY')
    
    if not private_key:
        raise ValueError("PRIVATE_KEY environment variable is required")
    
    print(f"🔗 Connecting to: {rpc_url}")
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    if not w3.is_connected():
        raise ConnectionError(f"Failed to connect to {rpc_url}")
    
    # Load account
    account = w3.eth.account.from_key(private_key)
    print(f"👤 Deployer address: {account.address}")
    
    # Check balance
    balance = w3.eth.get_balance(account.address)
    balance_eth = w3.from_wei(balance, 'ether')
    print(f"💰 Balance: {balance_eth:.4f} ETH")
    
    if balance_eth < 0.1:
        print("⚠️  Warning: Low balance, deployment may fail")
    
    # Deploy contracts
    addresses = {}
    tx_hashes = {}
    
    try:
        # Deploy IdentityRegistry first (no dependencies)
        addr, tx = deploy_contract(w3, account, 'IdentityRegistry')
        addresses['identity_registry'] = addr
        tx_hashes['identity_registry'] = tx
        
        # Deploy ReputationRegistry (depends on IdentityRegistry)
        addr, tx = deploy_contract(w3, account, 'ReputationRegistry', [addresses['identity_registry']])
        addresses['reputation_registry'] = addr
        tx_hashes['reputation_registry'] = tx
        
        # Deploy ValidationRegistry (depends on IdentityRegistry)
        addr, tx = deploy_contract(w3, account, 'ValidationRegistry', [addresses['identity_registry']])
        addresses['validation_registry'] = addr
        tx_hashes['validation_registry'] = tx
        
        # Save deployment info
        save_deployment_info(addresses, tx_hashes)
        
        print(f"\n🎉 All contracts deployed successfully!")
        print(f"📄 Deployment details saved to: deployment.json")
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        raise

if __name__ == "__main__":
    main() 