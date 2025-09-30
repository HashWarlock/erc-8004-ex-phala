#!/usr/bin/env python3
"""
Wallet Management Tool

Check funding status of TEE-derived agent addresses.
Helps track which addresses need Base Sepolia ETH.
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any
from tabulate import tabulate

sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from web3 import Web3
from src.agent.tee_auth import TEEAuthenticator


class WalletChecker:
    """Check wallet balances for multiple agents."""

    def __init__(self, rpc_url: str = "https://sepolia.base.org"):
        """Initialize wallet checker."""
        self.rpc_url = rpc_url
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to {rpc_url}")

    async def derive_address(self, domain: str, salt: str, use_tee: bool = True) -> str:
        """Derive agent address from domain and salt."""
        auth = TEEAuthenticator(
            domain=domain,
            salt=salt,
            use_tee=use_tee,
            tee_endpoint=None
        )
        return await auth.derive_address()

    def check_balance(self, address: str) -> Dict[str, Any]:
        """Check balance of an address."""
        balance_wei = self.w3.eth.get_balance(address)
        balance_eth = self.w3.from_wei(balance_wei, 'ether')

        # Estimate minimum needed (rough estimate)
        gas_price = self.w3.eth.gas_price
        estimated_gas = 500000  # Registration
        min_needed_wei = gas_price * estimated_gas
        min_needed_eth = self.w3.from_wei(min_needed_wei, 'ether')

        return {
            "address": address,
            "balance_eth": float(balance_eth),
            "balance_wei": balance_wei,
            "min_needed_eth": float(min_needed_eth),
            "funded": balance_wei >= min_needed_wei,
            "gas_price_gwei": float(self.w3.from_wei(gas_price, 'gwei'))
        }

    async def check_agent(
        self,
        name: str,
        domain: str,
        salt: str
    ) -> Dict[str, Any]:
        """Check a specific agent configuration."""
        address = await self.derive_address(domain, salt, use_tee=True)
        balance_info = self.check_balance(address)

        return {
            "name": name,
            "domain": domain,
            "address": address,
            **balance_info
        }


async def main():
    """Check common agent configurations."""
    print("\n" + "="*100)
    print("ERC-8004 AGENT WALLET STATUS - Base Sepolia")
    print("="*100 + "\n")

    load_dotenv()

    # Initialize checker
    checker = WalletChecker()

    # Define agent configurations to check
    # You can add more configurations as needed
    agents_to_check = [
        {
            "name": "Production Agent",
            "domain": "agent.phala.network",  # Update with actual domain
            "salt": "production-salt-change-this-value"  # From .env.production
        },
        {
            "name": "Test Agent",
            "domain": "test-agent.phala.network",
            "salt": "test-salt-123"
        },
        {
            "name": "Server Agent",
            "domain": "server-agent.test.phala.network",
            "salt": "server-test-salt"
        }
    ]

    # Check all agents
    results = []
    for agent_config in agents_to_check:
        print(f"Checking {agent_config['name']}...")
        result = await checker.check_agent(**agent_config)
        results.append(result)

    # Display results in table
    print("\n" + "="*100)
    print("WALLET STATUS SUMMARY")
    print("="*100 + "\n")

    table_data = []
    for r in results:
        status = "✓ Funded" if r['funded'] else "✗ Needs Funds"
        table_data.append([
            r['name'],
            r['address'],
            f"{r['balance_eth']:.4f}",
            f"{r['min_needed_eth']:.4f}",
            status
        ])

    headers = ["Agent Name", "Address", "Balance (ETH)", "Min Needed (ETH)", "Status"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    # Show addresses that need funding
    needs_funding = [r for r in results if not r['funded']]

    if needs_funding:
        print("\n" + "="*100)
        print("⚠️  ADDRESSES THAT NEED FUNDING")
        print("="*100 + "\n")

        for r in needs_funding:
            print(f"Agent: {r['name']}")
            print(f"Address: {r['address']}")
            print(f"Current: {r['balance_eth']:.4f} ETH")
            print(f"Needed: {r['min_needed_eth']:.4f} ETH")
            print(f"Send: At least {r['min_needed_eth']:.4f} ETH\n")

        print("Get Base Sepolia ETH from:")
        print("  • Coinbase Faucet: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet")
        print("  • Bridge from Sepolia: https://bridge.base.org/")
        print()

    else:
        print("\n✅ All agents are funded and ready for deployment!\n")

    # Gas price info
    gas_price = results[0]['gas_price_gwei'] if results else 0
    print(f"Current Gas Price: {gas_price:.2f} gwei")
    print(f"Network: Base Sepolia")
    print(f"RPC: {checker.rpc_url}\n")

    return results


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)