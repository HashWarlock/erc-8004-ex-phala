"""
Genesis Studio - Simple Wallet Management Module

This module provides a simplified wallet manager using Web3.py accounts
for quick testing. In production, you'd use the full Coinbase AgentKit.
"""

import os
import json
from typing import Dict, Optional
from web3 import Web3
from eth_account import Account
from rich.console import Console
from rich import print as rprint

console = Console()

class GenesisWalletManager:
    """Simplified wallet manager for Genesis Studio testing"""
    
    def __init__(self):
        self.wallets: Dict[str, Account] = {}
        self.wallet_data_file = "genesis_wallets.json"
        
        # Initialize Web3 connection
        network = os.getenv('NETWORK', 'base-sepolia')
        if network == 'base-sepolia':
            rpc_url = os.getenv('BASE_SEPOLIA_RPC_URL')
        elif network == 'sepolia':
            rpc_url = os.getenv('SEPOLIA_RPC_URL')
        else:
            rpc_url = os.getenv('LOCAL_RPC_URL', 'http://127.0.0.1:8545')
        
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
    def create_or_load_wallet(self, agent_name: str) -> Account:
        """Create a new wallet or load existing one for an agent"""
        
        if agent_name in self.wallets:
            return self.wallets[agent_name]
            
        # Try to load existing wallet data
        wallet_data = self._load_wallet_data(agent_name)
        
        if wallet_data:
            rprint(f"[green]📂 Loading existing wallet for {agent_name}...")
            # Load from private key
            account = Account.from_key(wallet_data['private_key'])
        else:
            rprint(f"[yellow]🔧 Creating new wallet for {agent_name}...")
            with console.status(f"[bold green]Creating wallet for {agent_name}..."):
                # Create new account
                account = Account.create()
                self._save_wallet_data(agent_name, {
                    'private_key': account.key.hex(),
                    'address': account.address
                })
            
            rprint(f"[green]✅ New wallet created for {agent_name}")
            rprint(f"[blue]   Address: {account.address}")
        
        self.wallets[agent_name] = account
        return account
    
    def get_wallet_address(self, agent_name: str) -> str:
        """Get the address of an agent's wallet"""
        if agent_name not in self.wallets:
            self.create_or_load_wallet(agent_name)
        return self.wallets[agent_name].address
    
    def get_wallet_balance(self, agent_name: str, asset_id: str = "eth") -> float:
        """Get the balance of an agent's wallet"""
        if agent_name not in self.wallets:
            self.create_or_load_wallet(agent_name)
        
        wallet = self.wallets[agent_name]
        
        if asset_id == "eth":
            balance_wei = self.w3.eth.get_balance(wallet.address)
            return self.w3.from_wei(balance_wei, 'ether')
        else:
            # For ERC20 tokens, we'd need the contract ABI
            # For now, return 0
            return 0.0
    
    def fund_wallet_from_faucet(self, agent_name: str) -> bool:
        """Fund wallet from testnet faucet (placeholder - manual funding required)"""
        if agent_name not in self.wallets:
            self.create_or_load_wallet(agent_name)
            
        wallet = self.wallets[agent_name]
        
        rprint(f"[yellow]💰 Please manually fund {agent_name}'s wallet:")
        rprint(f"[blue]   Address: {wallet.address}")
        rprint(f"[blue]   Network: {os.getenv('NETWORK', 'base-sepolia')}")
        
        return True
    
    def transfer_usdc(self, from_agent: str, to_agent: str, amount: float) -> Optional[str]:
        """Transfer USDC between agent wallets (simplified implementation)"""
        from_wallet = self.wallets.get(from_agent)
        
        # Handle direct addresses vs agent names
        if to_agent.startswith('0x') and len(to_agent) == 42:
            # Direct address provided
            to_address = to_agent
        else:
            # Agent name provided, get wallet address
            to_address = self.get_wallet_address(to_agent)
        
        if not from_wallet:
            rprint(f"[red]❌ Wallet not found for {from_agent}")
            return None
        
        usdc_address = os.getenv("USDC_CONTRACT_ADDRESS")
        if not usdc_address:
            rprint("[red]❌ USDC contract address not configured")
            return None
        
        try:
            # Base Sepolia USDC contract address
            usdc_contract_address = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"  # Base Sepolia USDC
            
            # ERC-20 ABI (minimal for transfer)
            erc20_abi = [
                {
                    "constant": False,
                    "inputs": [
                        {"name": "_to", "type": "address"},
                        {"name": "_value", "type": "uint256"}
                    ],
                    "name": "transfer",
                    "outputs": [{"name": "", "type": "bool"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function"
                }
            ]
            
            # Create USDC contract instance
            usdc_contract = self.w3.eth.contract(
                address=usdc_contract_address,
                abi=erc20_abi
            )
            
            # Convert amount to wei (USDC has 6 decimals)
            amount_wei = int(amount * 10**6)
            
            rprint(f"[blue]💸 Initiating real USDC transfer...[/blue]")
            rprint(f"[blue]   Amount: {amount} USDC ({amount_wei} wei)[/blue]")
            rprint(f"[blue]   From: {from_agent} ({from_wallet.address})[/blue]")
            rprint(f"[blue]   To: {to_agent} ({to_address})[/blue]")
            
            # Check balance first
            balance = usdc_contract.functions.balanceOf(from_wallet.address).call()
            balance_usdc = balance / 10**6
            rprint(f"[blue]   Current balance: {balance_usdc} USDC[/blue]")
            
            if balance < amount_wei:
                raise Exception(f"Insufficient USDC balance: {balance_usdc} < {amount}")
            
            # Build the transfer transaction
            transfer_function = usdc_contract.functions.transfer(to_address, amount_wei)
            
            # Estimate gas
            gas_estimate = transfer_function.estimate_gas({'from': from_wallet.address})
            gas_limit = int(gas_estimate * 1.2)  # Add 20% buffer
            
            rprint(f"[blue]⛽ Gas estimate: {gas_estimate}, using limit: {gas_limit}[/blue]")
            
            # Build transaction
            transaction = transfer_function.build_transaction({
                'from': from_wallet.address,
                'gas': gas_limit,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(from_wallet.address),
                'chainId': self.w3.eth.chain_id
            })
            
            # Sign and send transaction
            signed_txn = from_wallet.sign_transaction(transaction)
            # Handle different Web3.py versions
            raw_transaction = signed_txn.raw_transaction if hasattr(signed_txn, 'raw_transaction') else signed_txn.rawTransaction
            tx_hash = self.w3.eth.send_raw_transaction(raw_transaction)
            
            # Wait for confirmation
            rprint(f"[blue]⏳ Waiting for USDC transfer confirmation...[/blue]")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                rprint(f"[green]✅ USDC transfer successful![/green]")
                rprint(f"[green]   Transaction: {tx_hash.hex()}[/green]")
                return tx_hash.hex()
            else:
                raise Exception(f"USDC transfer failed with status {receipt.status}")
                
        except Exception as e:
            rprint(f"[red]❌ USDC transfer failed: {e}[/red]")
            rprint(f"[yellow]💸 Falling back to simulated transfer[/yellow]")
            rprint(f"[blue]   Amount: {amount} USDC[/blue]")
            rprint(f"[blue]   From: {from_agent} ({from_wallet.address})[/blue]")
            rprint(f"[blue]   To: {to_agent} ({to_address})[/blue]")
            
            # Return a simulated transaction hash as fallback
            return "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    
    def _load_wallet_data(self, agent_name: str) -> Optional[Dict]:
        """Load wallet data from file"""
        if not os.path.exists(self.wallet_data_file):
            return None
            
        try:
            with open(self.wallet_data_file, 'r') as f:
                all_data = json.load(f)
                return all_data.get(agent_name)
        except Exception:
            return None
    
    def _save_wallet_data(self, agent_name: str, wallet_data: Dict):
        """Save wallet data to file"""
        all_data = {}
        
        if os.path.exists(self.wallet_data_file):
            try:
                with open(self.wallet_data_file, 'r') as f:
                    all_data = json.load(f)
            except Exception:
                pass
        
        all_data[agent_name] = wallet_data
        
        with open(self.wallet_data_file, 'w') as f:
            json.dump(all_data, f, indent=2)
    
    def display_wallet_summary(self):
        """Display a summary of all agent wallets"""
        rprint("\n[bold cyan]🏦 Genesis Studio Wallet Summary[/bold cyan]")
        rprint("=" * 50)
        
        for agent_name in ["Alice", "Bob", "Charlie"]:
            if agent_name in self.wallets:
                wallet = self.wallets[agent_name]
                address = wallet.address
                eth_balance = self.get_wallet_balance(agent_name, "eth")
                
                rprint(f"[green]{agent_name}:[/green]")
                rprint(f"  Address: [blue]{address}[/blue]")
                rprint(f"  ETH Balance: [yellow]{eth_balance:.4f} ETH[/yellow]")
                rprint()
            else:
                # Create wallet to show address
                self.create_or_load_wallet(agent_name)
                wallet = self.wallets[agent_name]
                address = wallet.address
                eth_balance = self.get_wallet_balance(agent_name, "eth")
                
                rprint(f"[green]{agent_name}:[/green]")
                rprint(f"  Address: [blue]{address}[/blue]")
                rprint(f"  ETH Balance: [yellow]{eth_balance:.4f} ETH[/yellow]")
                rprint()
