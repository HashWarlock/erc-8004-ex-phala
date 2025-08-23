#!/usr/bin/env python3
"""
Simple test to verify contract deployment and basic functions
"""

import json
from web3 import Web3

# Connect to Anvil
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
print(f"Connected: {w3.is_connected()}")
print(f"Chain ID: {w3.eth.chain_id}")

# Load contract addresses
with open('deployed_contracts.json', 'r') as f:
    contracts = json.load(f)['contracts']

# Load IdentityRegistry ABI
with open('contracts/out/IdentityRegistry.sol/IdentityRegistry.json', 'r') as f:
    identity_abi = json.load(f)['abi']

# Create contract instance
identity = w3.eth.contract(
    address=contracts['IdentityRegistry'],
    abi=identity_abi
)

print(f"\n=== Testing IdentityRegistry ===")
print(f"Contract Address: {contracts['IdentityRegistry']}")

# Test 1: Get registration fee
try:
    fee = identity.functions.REGISTRATION_FEE().call()
    print(f"✅ Registration Fee: {w3.from_wei(fee, 'ether')} ETH")
except Exception as e:
    print(f"❌ Error getting fee: {e}")

# Test 2: Get agent count
try:
    count = identity.functions.getAgentCount().call()
    print(f"✅ Current Agent Count: {count}")
except Exception as e:
    print(f"❌ Error getting count: {e}")

# Test 3: Register an agent
alice = w3.eth.accounts[1]
print(f"\n=== Registering Alice ({alice}) ===")

try:
    # Get current nonce
    nonce = w3.eth.get_transaction_count(alice)
    
    # Build transaction
    tx = identity.functions.newAgent(
        "alice.test.com",
        alice
    ).build_transaction({
        'from': alice,
        'value': fee,
        'gas': 500000,
        'gasPrice': w3.to_wei('2', 'gwei'),
        'nonce': nonce,
    })
    
    # Sign with Alice's private key (Anvil account 1)
    signed = w3.eth.account.sign_transaction(
        tx, 
        '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d'
    )
    
    # Send transaction
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt.status == 1:
        print(f"✅ Registration successful! Gas used: {receipt.gasUsed}")
        
        # Get Alice's info
        alice_info = identity.functions.resolveByAddress(alice).call()
        print(f"✅ Alice's Agent ID: {alice_info[0]}")
        print(f"✅ Alice's Domain: {alice_info[1]}")
        print(f"✅ Alice's Address: {alice_info[2]}")
    else:
        print(f"❌ Registration failed!")
        
except Exception as e:
    print(f"❌ Error during registration: {e}")

# Test 4: Check final agent count
try:
    final_count = identity.functions.getAgentCount().call()
    print(f"\n✅ Final Agent Count: {final_count}")
except Exception as e:
    print(f"❌ Error getting final count: {e}")

print("\n=== Test Complete ===")