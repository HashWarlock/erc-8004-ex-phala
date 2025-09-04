#!/usr/bin/env python3
"""
Create deployed_contracts.json from Forge broadcast output
"""
import json
import sys
import os
from web3 import Web3

def main():
    # Read the broadcast file
    broadcast_file = 'contracts/broadcast/Deploy.s.sol/31337/run-latest.json'
    
    if not os.path.exists(broadcast_file):
        print(f"Error: {broadcast_file} not found")
        sys.exit(1)
    
    with open(broadcast_file, 'r') as f:
        broadcast = json.load(f)
    
    # Extract contract addresses and convert to checksum format
    contracts = {}
    for tx in broadcast.get('transactions', []):
        contract_name = tx.get('contractName')
        contract_address = tx.get('contractAddress')
        
        if contract_name and contract_address:
            # Convert to checksum address for Web3.py compatibility
            checksum_address = Web3.to_checksum_address(contract_address)
            contracts[contract_name] = checksum_address
    
    # Create output
    output = {
        'contracts': contracts
    }
    
    # Write to deployed_contracts.json
    with open('deployed_contracts.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"  Created deployed_contracts.json with {len(contracts)} contracts")
    for name, addr in contracts.items():
        print(f"    {name}: {addr}")

if __name__ == '__main__':
    main()