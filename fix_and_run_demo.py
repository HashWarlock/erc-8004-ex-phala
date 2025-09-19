#!/usr/bin/env python3
"""
Fix and run Genesis Studio demo with proper error handling
"""

import os
from agents.wallet_manager import GenesisWalletManager
from rich import print as rprint
from rich.console import Console
from rich.table import Table

def check_wallet_funding():
    """Check if wallets are properly funded"""
    rprint("[bold cyan]🔧 Checking Wallet Funding Status[/bold cyan]")
    
    wm = GenesisWalletManager()
    console = Console()
    
    # Create funding status table
    table = Table(title="💰 Wallet Funding Status")
    table.add_column("Agent", style="cyan", no_wrap=True)
    table.add_column("Address", style="blue")
    table.add_column("ETH Balance", style="green")
    table.add_column("Status", style="yellow")
    
    all_funded = True
    
    for name in ['Alice', 'Bob', 'Charlie']:
        wallet = wm.create_or_load_wallet(name)
        balance = wm.get_wallet_balance(name)
        
        if balance > 0.001:  # Minimum 0.001 ETH for gas
            status = "✅ Ready"
        else:
            status = "❌ Needs Funding"
            all_funded = False
        
        table.add_row(name, wallet.address, f"{balance:.6f} ETH", status)
    
    console.print(table)
    
    if not all_funded:
        rprint("\n[bold red]🚨 WALLETS NEED FUNDING[/bold red]")
        rprint("[yellow]Please fund the wallets using Base Sepolia faucet:[/yellow]")
        rprint("[blue]https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet[/blue]")
        rprint("\n[yellow]Each wallet needs at least 0.001 ETH for gas fees.[/yellow]")
        return False
    
    rprint("\n[bold green]✅ All wallets are funded and ready![/bold green]")
    return True

def run_demo_with_fixes():
    """Run the demo with proper error handling"""
    
    # Check funding first
    if not check_wallet_funding():
        rprint("\n[red]❌ Cannot run demo without funded wallets.[/red]")
        return False
    
    # Import and run the main demo
    try:
        rprint("\n[bold cyan]🚀 Starting Genesis Studio Demo[/bold cyan]")
        from genesis_studio import GenesisStudioDemo
        
        demo = GenesisStudioDemo()
        demo.run_complete_demo()
        
        rprint("\n[bold green]🎉 Demo completed successfully![/bold green]")
        return True
        
    except Exception as e:
        rprint(f"\n[bold red]❌ Demo failed: {e}[/bold red]")
        
        # Check if it's a funding issue
        if "insufficient funds" in str(e).lower():
            rprint("[yellow]💰 This appears to be a funding issue.[/yellow]")
            rprint("[yellow]Please ensure all wallets have sufficient ETH and USDC.[/yellow]")
        
        return False

def main():
    rprint("[bold cyan]🔧 Genesis Studio Demo Fixer & Runner[/bold cyan]")
    rprint("[blue]This script will check wallet funding and run the demo safely.[/blue]")
    
    success = run_demo_with_fixes()
    
    if success:
        rprint("\n[bold green]✅ All systems operational![/bold green]")
    else:
        rprint("\n[bold red]❌ Please fix the issues above and try again.[/bold red]")

if __name__ == "__main__":
    main()
