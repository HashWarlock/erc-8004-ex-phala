#!/usr/bin/env python3
"""Deploy IdentityRegistry contract to Base Sepolia"""

from web3 import Web3
from eth_account import Account
import json
import sys

# Compile contract
with open('contracts/IdentityRegistry.sol', 'r') as f:
    source = f.read()

# Simple deployment using solc-x
try:
    from solcx import compile_source, install_solc
    install_solc('0.8.20')
    compiled = compile_source(source, output_values=['abi', 'bin'], solc_version='0.8.20')
    contract_interface = compiled['<stdin>:IdentityRegistry']
except ImportError:
    print("solc-x not installed. Install: pip install py-solc-x")
    sys.exit(1)

# Setup
rpc_url = "https://sepolia.base.org"
private_key = input("Enter deployer private key: ")

w3 = Web3(Web3.HTTPProvider(rpc_url))
account = Account.from_key(private_key)

print(f"Deployer: {account.address}")
print(f"Balance: {w3.from_wei(w3.eth.get_balance(account.address), 'ether')} ETH")

# Deploy
IdentityRegistry = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
tx = IdentityRegistry.constructor().build_transaction({
    'chainId': 84532,
    'gas': 2000000,
    'gasPrice': w3.eth.gas_price,
    'nonce': w3.eth.get_transaction_count(account.address)
})

signed = account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
print(f"Deploying... tx: {tx_hash.hex()}")

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"✅ Deployed at: {receipt.contractAddress}")
print(f"Update .env: IDENTITY_REGISTRY_ADDRESS={receipt.contractAddress}")
