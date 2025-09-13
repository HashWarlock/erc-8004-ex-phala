"""
Genesis Studio - Rich CLI Utilities

This module provides beautiful, interactive command-line interface components
using the Rich library for Genesis Studio operations.
"""

import time
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.text import Text
from rich.align import Align
from rich import print as rprint
from rich.markdown import Markdown

console = Console()

class GenesisStudioCLI:
    """Rich CLI interface for Genesis Studio operations"""
    
    def __init__(self):
        self.console = console
    
    def print_banner(self):
        """Display the Genesis Studio banner"""
        banner_text = """
# 🚀 CHAOSCHAIN GENESIS STUDIO
## ERC-8004 Commercial Prototype

*Demonstrating the complete lifecycle of trustless agentic commerce:*
- **On-chain Identity** via ERC-8004 registries
- **Verifiable Work** with IPFS storage  
- **Direct Payments** using USDC on Base Sepolia
- **IP Monetization** through Story Protocol
        """
        
        banner_panel = Panel(
            Markdown(banner_text),
            title="[bold cyan]Welcome to ChaosChain Genesis Studio[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(Align.center(banner_panel))
        self.console.print()
    
    def print_phase_header(self, phase_num: int, phase_name: str, description: str):
        """Display a phase header"""
        header = f"Phase {phase_num}: {phase_name}"
        
        phase_panel = Panel(
            f"[bold white]{description}[/bold white]",
            title=f"[bold yellow]{header}[/bold yellow]",
            border_style="yellow",
            padding=(0, 1)
        )
        
        self.console.print()
        self.console.print(phase_panel)
        self.console.print()
    
    def print_step(self, step_num: int, description: str, status: str = "pending"):
        """Print a step with status indicator"""
        if status == "pending":
            icon = "⏳"
            color = "yellow"
        elif status == "in_progress":
            icon = "🔄"
            color = "blue"
        elif status == "completed":
            icon = "✅"
            color = "green"
        elif status == "failed":
            icon = "❌"
            color = "red"
        else:
            icon = "📋"
            color = "white"
        
        self.console.print(f"{icon} [bold {color}]Step {step_num}:[/bold {color}] {description}")
    
    def print_agent_registration(self, agent_name: str, agent_id: int, address: str, tx_hash: str):
        """Display agent registration success"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Agent Name:", f"[bold green]{agent_name}[/bold green]")
        table.add_row("Agent ID:", f"[bold yellow]{agent_id}[/bold yellow]")
        table.add_row("Wallet Address:", f"[blue]{address}[/blue]")
        table.add_row("Registration Tx:", f"[link=https://sepolia.basescan.org/tx/{tx_hash}]{tx_hash}[/link]")
        
        panel = Panel(
            table,
            title=f"[bold green]✅ {agent_name} Registered Successfully[/bold green]",
            border_style="green"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def print_ipfs_upload(self, filename: str, cid: str, gateway_url: str):
        """Display IPFS upload success"""
        self.console.print(f"[green]📁 {filename} uploaded to IPFS[/green]")
        self.console.print(f"   [blue]CID:[/blue] {cid}")
        self.console.print(f"   [blue]URL:[/blue] [link={gateway_url}]{gateway_url}[/link]")
        self.console.print()
    
    def print_usdc_payment(self, from_agent: str, to_agent: str, amount: float, tx_hash: str):
        """Display USDC payment success"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("From:", f"[yellow]{from_agent}[/yellow]")
        table.add_row("To:", f"[yellow]{to_agent}[/yellow]")
        table.add_row("Amount:", f"[bold green]{amount} USDC[/bold green]")
        table.add_row("Transaction:", f"[link=https://sepolia.basescan.org/tx/{tx_hash}]{tx_hash}[/link]")
        
        panel = Panel(
            table,
            title="[bold green]💸 USDC Payment Successful[/bold green]",
            border_style="green"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def print_x402_payment(self, from_agent: str, to_agent: str, amount: float, tx_hash: str, service_description: str):
        """Display x402 payment success"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("From:", f"[yellow]{from_agent}[/yellow]")
        table.add_row("To:", f"[yellow]{to_agent}[/yellow]")
        table.add_row("Amount:", f"[bold green]{amount} USDC[/bold green]")
        table.add_row("Service:", f"[blue]{service_description}[/blue]")
        table.add_row("Protocol:", f"[magenta]x402 (HTTP 402)[/magenta]")
        table.add_row("Transaction:", f"[link=https://sepolia.basescan.org/tx/{tx_hash}]{tx_hash}[/link]")
        table.add_row("Receipt:", f"[dim]✅ Cryptographic proof generated[/dim]")
        
        panel = Panel(
            table,
            title="[bold cyan]💳 x402 Payment Successful[/bold cyan]",
            border_style="cyan"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def print_story_protocol_registration(self, title: str, asset_id: str, creator: str, story_url: str):
        """Display Story Protocol IP registration success"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("IP Title:", f"[bold white]{title}[/bold white]")
        table.add_row("Asset ID:", f"[yellow]{asset_id}[/yellow]")
        table.add_row("Creator:", f"[blue]{creator}[/blue]")
        table.add_row("Story Protocol:", f"[link={story_url}]{story_url}[/link]")
        
        panel = Panel(
            table,
            title="[bold magenta]🎨 IP Asset Registered on Story Protocol[/bold magenta]",
            border_style="magenta"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def print_validation_request(self, validator_name: str, data_hash: str, tx_hash: str):
        """Display validation request"""
        self.console.print(f"[blue]🔍 Validation requested from {validator_name}[/blue]")
        self.console.print(f"   [dim]Data Hash:[/dim] {data_hash}")
        self.console.print(f"   [dim]Transaction:[/dim] [link=https://sepolia.basescan.org/tx/{tx_hash}]{tx_hash}[/link]")
        self.console.print()
    
    def print_validation_response(self, validator_name: str, score: int, tx_hash: str):
        """Display validation response"""
        color = "green" if score >= 90 else "yellow" if score >= 70 else "red"
        self.console.print(f"[{color}]📊 Validation completed by {validator_name}: {score}/100[/{color}]")
        self.console.print(f"   [dim]Transaction:[/dim] [link=https://sepolia.basescan.org/tx/{tx_hash}]{tx_hash}[/link]")
        self.console.print()
    
    def print_final_summary(self, summary_data: Dict[str, Any]):
        """Display the final success summary"""
        
        # Create summary table
        table = Table(title="[bold cyan]🎉 Genesis Studio Demo Completed Successfully![/bold cyan]", 
                     show_header=True, header_style="bold magenta")
        table.add_column("Component", style="cyan", width=20)
        table.add_column("Status", style="green", width=15)
        table.add_column("Details", style="white", width=50)
        
        # Add rows for each component
        for component, data in summary_data.items():
            if data.get("success"):
                status = "✅ Success"
                details = data.get("details", "Completed successfully")
            else:
                status = "❌ Failed"
                details = data.get("error", "Unknown error")
            
            table.add_row(component, status, details)
        
        self.console.print()
        self.console.print(table)
        self.console.print()
        
        # Print key links
        links_panel = Panel(
            self._format_key_links(summary_data),
            title="[bold blue]🔗 Key Links[/bold blue]",
            border_style="blue"
        )
        
        self.console.print(links_panel)
        self.console.print()
    
    def _format_key_links(self, summary_data: Dict[str, Any]) -> str:
        """Format key links for the final summary"""
        links = []
        
        # Agent registrations
        if "Agent Registration" in summary_data:
            agent_data = summary_data["Agent Registration"]
            if agent_data.get("success") and "tx_hashes" in agent_data:
                links.append("🤖 Agent Registrations:")
                for agent, tx_hash in agent_data["tx_hashes"].items():
                    links.append(f"   • {agent}: https://sepolia.basescan.org/tx/{tx_hash}")
        
        # IPFS uploads
        if "IPFS Storage" in summary_data:
            ipfs_data = summary_data["IPFS Storage"]
            if ipfs_data.get("success") and "cids" in ipfs_data:
                links.append("\n📁 IPFS Files:")
                for filename, cid in ipfs_data["cids"].items():
                    links.append(f"   • {filename}: https://gateway.pinata.cloud/ipfs/{cid}")
        
        # USDC payment
        if "USDC Payment" in summary_data:
            payment_data = summary_data["USDC Payment"]
            if payment_data.get("success") and "tx_hash" in payment_data:
                links.append(f"\n💸 USDC Payment: https://sepolia.basescan.org/tx/{payment_data['tx_hash']}")
        
        # Story Protocol
        if "Story Protocol" in summary_data:
            story_data = summary_data["Story Protocol"]
            if story_data.get("success") and "asset_urls" in story_data:
                links.append("\n🎨 Story Protocol IP Assets:")
                for title, url in story_data["asset_urls"].items():
                    links.append(f"   • {title}: {url}")
        
        return "\n".join(links) if links else "No links available"
    
    def print_error(self, message: str, details: Optional[str] = None):
        """Display an error message"""
        error_text = f"[bold red]❌ Error:[/bold red] {message}"
        if details:
            error_text += f"\n[dim]{details}[/dim]"
        
        error_panel = Panel(
            error_text,
            border_style="red",
            padding=(0, 1)
        )
        
        self.console.print(error_panel)
        self.console.print()
    
    def print_warning(self, message: str):
        """Display a warning message"""
        self.console.print(f"[bold yellow]⚠️  Warning:[/bold yellow] {message}")
        self.console.print()
    
    def print_info(self, message: str):
        """Display an info message"""
        self.console.print(f"[blue]ℹ️  Info:[/blue] {message}")
        self.console.print()
    
    def create_progress_bar(self, description: str) -> Progress:
        """Create a progress bar for long-running operations"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        )
    
    def wait_with_spinner(self, message: str, duration: float = 2.0):
        """Display a spinner for a specified duration"""
        with self.console.status(f"[bold blue]{message}..."):
            time.sleep(duration)
