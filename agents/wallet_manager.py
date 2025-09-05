"""
Genesis Studio - Wallet Management Module

This module handles wallet creation and management using Coinbase AgentKit.
Each agent (Alice, Bob, Charlie) gets their own dedicated wallet for on-chain operations.
"""

import os
import json
from typing import Dict, Optional
from cdp import EvmLocalAccount
from rich.console import Console
from rich.spinner import Spinner
from rich import print as rprint

console = Console()

class GenesisWalletManager:
    """Manages agent wallets using Coinbase AgentKit"""
    
    def __init__(self):
        self.wallets: Dict[str, EvmLocalAccount] = {}
        self.wallet_data_file = "genesis_wallets.json"
        
        # For now, we'll use simple local accounts
        # In production, you'd configure CDP properly
        
    def create_or_load_wallet(self, agent_name: str) -> Wallet:
        """Create a new wallet or load existing one for an agent"""
        
        if agent_name in self.wallets:
            return self.wallets[agent_name]
            
        # Try to load existing wallet data
        wallet_data = self._load_wallet_data(agent_name)
        
        if wallet_data:
            rprint(f"[green]📂 Loading existing wallet for {agent_name}...")
            wallet = Wallet.import_data(wallet_data)
        else:
            rprint(f"[yellow]🔧 Creating new wallet for {agent_name}...")
            with console.status(f"[bold green]Creating wallet for {agent_name}..."):
                wallet = Wallet.create()
                self._save_wallet_data(agent_name, wallet.export_data())
            
            rprint(f"[green]✅ New wallet created for {agent_name}")
            rprint(f"[blue]   Address: {wallet.default_address.address_id}")
        
        self.wallets[agent_name] = wallet
        return wallet
    
    def get_wallet_address(self, agent_name: str) -> str:
        """Get the address of an agent's wallet"""
        if agent_name not in self.wallets:
            self.create_or_load_wallet(agent_name)
        return self.wallets[agent_name].default_address.address_id
    
    def get_wallet_balance(self, agent_name: str, asset_id: str = "eth") -> float:
        """Get the balance of an agent's wallet"""
        if agent_name not in self.wallets:
            self.create_or_load_wallet(agent_name)
        
        wallet = self.wallets[agent_name]
        balance = wallet.balance(asset_id)
        return float(balance.amount)
    
    def fund_wallet_from_faucet(self, agent_name: str) -> bool:
        """Fund wallet from testnet faucet (Base Sepolia)"""
        if agent_name not in self.wallets:
            self.create_or_load_wallet(agent_name)
            
        wallet = self.wallets[agent_name]
        
        try:
            with console.status(f"[bold yellow]Requesting testnet funds for {agent_name}..."):
                faucet_tx = wallet.faucet()
                faucet_tx.wait()
            
            rprint(f"[green]💰 Testnet funds received for {agent_name}")
            rprint(f"[blue]   Transaction: {faucet_tx.transaction_hash}")
            return True
            
        except Exception as e:
            rprint(f"[red]❌ Failed to fund wallet for {agent_name}: {e}")
            return False
    
    def transfer_usdc(self, from_agent: str, to_agent: str, amount: float) -> Optional[str]:
        """Transfer USDC between agent wallets"""
        from_wallet = self.wallets.get(from_agent)
        to_address = self.get_wallet_address(to_agent)
        
        if not from_wallet:
            rprint(f"[red]❌ Wallet not found for {from_agent}")
            return None
        
        usdc_address = os.getenv("USDC_CONTRACT_ADDRESS")
        if not usdc_address:
            rprint("[red]❌ USDC contract address not configured")
            return None
        
        try:
            with console.status(f"[bold blue]Transferring {amount} USDC from {from_agent} to {to_agent}..."):
                transfer = from_wallet.transfer(
                    amount=amount,
                    asset_id=usdc_address,
                    destination=to_address
                )
                transfer.wait()
            
            rprint(f"[green]💸 USDC transfer successful!")
            rprint(f"[blue]   Amount: {amount} USDC")
            rprint(f"[blue]   From: {from_agent} ({from_wallet.default_address.address_id})")
            rprint(f"[blue]   To: {to_agent} ({to_address})")
            rprint(f"[blue]   Transaction: {transfer.transaction_hash}")
            
            return transfer.transaction_hash
            
        except Exception as e:
            rprint(f"[red]❌ USDC transfer failed: {e}")
            return None
    
    def _load_wallet_data(self, agent_name: str) -> Optional[WalletData]:
        """Load wallet data from file"""
        if not os.path.exists(self.wallet_data_file):
            return None
            
        try:
            with open(self.wallet_data_file, 'r') as f:
                all_data = json.load(f)
                return all_data.get(agent_name)
        except Exception:
            return None
    
    def _save_wallet_data(self, agent_name: str, wallet_data: WalletData):
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
                address = wallet.default_address.address_id
                eth_balance = self.get_wallet_balance(agent_name, "eth")
                
                rprint(f"[green]{agent_name}:[/green]")
                rprint(f"  Address: [blue]{address}[/blue]")
                rprint(f"  ETH Balance: [yellow]{eth_balance:.4f} ETH[/yellow]")
                
                # Try to get USDC balance
                try:
                    usdc_balance = self.get_wallet_balance(agent_name, os.getenv("USDC_CONTRACT_ADDRESS", ""))
                    rprint(f"  USDC Balance: [yellow]{usdc_balance:.2f} USDC[/yellow]")
                except:
                    rprint(f"  USDC Balance: [dim]Unable to fetch[/dim]")
                
                rprint()
