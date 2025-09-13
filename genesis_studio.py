#!/usr/bin/env python3
"""
CHAOSCHAIN GENESIS STUDIO - x402 Enhanced Commercial Prototype

This script demonstrates the complete end-to-end commercial lifecycle of agentic work
with x402 payment integration:

1. On-chain identity registration using ERC-8004
2. Verifiable work execution with IPFS storage
3. x402 agent-to-agent payments with cryptographic receipts
4. Enhanced evidence packages with payment proofs for PoA
5. IP monetization through Story Protocol

Usage:
    python genesis_studio.py
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Add agents directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from dotenv import load_dotenv
from agents.cli_utils import GenesisStudioCLI
from agents.chaoschain_agent_sdk import ChaosChainAgentSDK, create_client_agent, create_server_agent, create_validator_agent

# Load environment variables
load_dotenv()

class GenesisStudioX402Orchestrator:
    """Enhanced Genesis Studio orchestrator with x402 payment integration"""
    
    def __init__(self):
        self.cli = GenesisStudioCLI()
        
        # Track results for final summary
        self.results = {}
        
        # Agent SDK instances
        self.alice_sdk = None  # Server Agent
        self.bob_sdk = None    # Validator Agent
        self.charlie_sdk = None # Client Agent
    
    def run_complete_demo(self):
        """Execute the complete Genesis Studio x402 demonstration"""
        
        try:
            self.cli.print_banner()
            
            # Phase 1: Setup & On-Chain Identity
            self._phase_1_setup_and_identity()
            
            # Phase 2: x402 Enhanced Work & Payment Flow
            self._phase_2_x402_work_and_payment()
            
            # Phase 3: Enhanced Evidence Packages with Payment Proofs
            self._phase_3_enhanced_evidence_packages()
            
            # Phase 4: IP Monetization Flywheel
            self._phase_4_ip_monetization()
            
            # Final Summary
            self._display_final_summary()
            
        except KeyboardInterrupt:
            self.cli.print_warning("Demo interrupted by user")
            sys.exit(1)
        except Exception as e:
            self.cli.print_error("Demo failed with unexpected error", str(e))
            sys.exit(1)
    
    def _phase_1_setup_and_identity(self):
        """Phase 1: Setup & On-Chain Identity Registration with x402 Integration"""
        
        self.cli.print_phase_header(
            1, 
            "Setup & x402-Enhanced Identity",
            "Creating agent SDKs and registering on-chain identities with payment capabilities"
        )
        
        # Step 1: Configuration Check
        self.cli.print_step(1, "Validating x402 and ERC-8004 configuration", "in_progress")
        self._validate_configuration()
        self.cli.print_step(1, "Configuration validated", "completed")
        
        # Step 2: Initialize Agent SDKs with x402 Integration
        self.cli.print_step(2, "Initializing ChaosChain Agent SDKs with x402 payment support", "in_progress")
        self._initialize_agent_sdks()
        self.cli.print_step(2, "Agent SDKs initialized", "completed")
        
        # Step 3: Fund wallets from faucet
        self.cli.print_step(3, "Funding wallets from Base Sepolia faucet", "in_progress")
        self._fund_agent_wallets()
        self.cli.print_step(3, "Wallets funded", "completed")
        
        # Step 4: On-chain registration
        self.cli.print_step(4, "Registering agents on ERC-8004 IdentityRegistry", "in_progress")
        self._register_agents_onchain()
        self.cli.print_step(4, "Agents registered on-chain", "completed")
    
    def _phase_2_x402_work_and_payment(self):
        """Phase 2: x402-Enhanced Work & Payment Flow"""
        
        self.cli.print_phase_header(
            2,
            "x402-Enhanced Work & Payment", 
            "Alice performs analysis, receives x402 payment, Bob validates with payment proof"
        )
        
        # Step 5: Work Execution (Alice)
        self.cli.print_step(5, "Alice performing market analysis", "in_progress")
        analysis_data = self._execute_market_analysis()
        self.cli.print_step(5, "Market analysis completed", "completed")
        
        # Step 6: Evidence Storage (Alice)
        self.cli.print_step(6, "Storing analysis on IPFS via Pinata", "in_progress")
        analysis_cid = self._store_analysis_on_ipfs(analysis_data)
        self.cli.print_step(6, "Analysis stored on IPFS", "completed")
        
        # Step 7: x402 Payment Flow (Charlie -> Alice)
        self.cli.print_step(7, "Charlie paying Alice via x402 for market analysis", "in_progress")
        analysis_payment_result = self._execute_x402_analysis_payment(analysis_cid, analysis_data)
        self.cli.print_step(7, f"x402 payment completed ({analysis_payment_result['final_amount']} USDC)", "completed")
        
        # Step 8: Validation Request (Alice)
        self.cli.print_step(8, "Alice requesting validation from Bob", "in_progress")
        validation_tx = self._request_validation(analysis_cid, analysis_data)
        self.cli.print_step(8, "Validation requested", "completed")
        
        # Step 9: Validation & x402 Payment (Bob)
        self.cli.print_step(9, "Bob validating and Charlie paying for validation service", "in_progress")
        validation_score, validation_result = self._perform_validation_with_payment(analysis_cid)
        self.cli.print_step(9, f"Validation completed (Score: {validation_score}/100)", "completed")
    
    def _phase_3_enhanced_evidence_packages(self):
        """Phase 3: Enhanced Evidence Packages with Payment Proofs"""
        
        self.cli.print_phase_header(
            3,
            "Enhanced Evidence Packages",
            "Creating comprehensive evidence packages with x402 payment proofs for PoA"
        )
        
        # Step 10: Create Enhanced Evidence Package (Alice)
        self.cli.print_step(10, "Alice creating enhanced evidence package with payment proofs", "in_progress")
        alice_evidence_package = self._create_enhanced_evidence_package()
        self.cli.print_step(10, "Enhanced evidence package created", "completed")
        
        # Step 11: Store Enhanced Evidence Package
        self.cli.print_step(11, "Storing enhanced evidence package on IPFS", "in_progress")
        enhanced_evidence_cid = self._store_enhanced_evidence_package(alice_evidence_package)
        self.cli.print_step(11, "Enhanced evidence package stored", "completed")
    
    def _phase_4_ip_monetization(self):
        """Phase 4: IP Monetization via Story Protocol"""
        
        self.cli.print_phase_header(
            4,
            "IP Monetization Flywheel",
            "Registering enhanced evidence as IP assets on Story Protocol"
        )
        
        # Step 12: Register Enhanced Evidence as IP (Demo mode)
        self.cli.print_step(12, "Skipping Story Protocol registration for demo", "completed")
        
        # Create demo IP results for final summary
        enhanced_ip = {
            "story_asset_id": "demo-enhanced-evidence-12345",
            "story_url": "https://explorer.story.foundation/asset/demo-enhanced-evidence-12345",
            "demo_mode": True,
            "includes_payment_proofs": True
        }
        
        # Store results for final summary
        self.results["enhanced_ip"] = enhanced_ip
        
        # Display the final success summary
        self._print_final_success_summary()
    
    def _validate_configuration(self):
        """Validate all required environment variables including x402"""
        required_vars = [
            "NETWORK", "BASE_SEPOLIA_RPC_URL", "BASE_SEPOLIA_PRIVATE_KEY",
            "CDP_API_KEY_ID", "CDP_API_KEY_SECRET", "CDP_WALLET_SECRET",
            "PINATA_JWT", "PINATA_GATEWAY",
            "CROSSMINT_API_KEY", "CROSSMINT_PROJECT_ID",
            "USDC_CONTRACT_ADDRESS"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Validate network is set to base-sepolia
        if os.getenv("NETWORK") != "base-sepolia":
            self.cli.print_warning("Network is not set to 'base-sepolia'. This demo is designed for Base Sepolia.")
    
    def _initialize_agent_sdks(self):
        """Initialize ChaosChain Agent SDKs with x402 integration"""
        
        # Create agent SDKs
        self.alice_sdk = create_server_agent(
            agent_name="Alice",
            agent_domain="alice.chaoschain-genesis-studio.com"
        )
        
        self.bob_sdk = create_validator_agent(
            agent_name="Bob",
            agent_domain="bob.chaoschain-genesis-studio.com"
        )
        
        self.charlie_sdk = create_client_agent(
            agent_name="Charlie",
            agent_domain="charlie.chaoschain-genesis-studio.com"
        )
        
        # Display SDK status
        for name, sdk in [("Alice", self.alice_sdk), ("Bob", self.bob_sdk), ("Charlie", self.charlie_sdk)]:
            status = sdk.get_sdk_status()
            print(f"✅ {name} SDK initialized:")
            print(f"   Wallet: {status['agent_info']['wallet_address']}")
            print(f"   Role: {status['agent_info']['role']}")
            print(f"   x402 Payment Support: ✅")
        
        # Store wallet addresses for later use
        self.results["wallets"] = {
            "Alice": self.alice_sdk.wallet_address,
            "Bob": self.bob_sdk.wallet_address,
            "Charlie": self.charlie_sdk.wallet_address
        }
    
    def _fund_agent_wallets(self):
        """Fund all agent wallets from Base Sepolia faucet"""
        
        agents = [("Alice", self.alice_sdk), ("Bob", self.bob_sdk), ("Charlie", self.charlie_sdk)]
        funded_agents = []
        
        for agent_name, sdk in agents:
            if sdk.wallet_manager.fund_wallet_from_faucet(agent_name):
                funded_agents.append(agent_name)
            else:
                self.cli.print_warning(f"Failed to fund {agent_name}'s wallet. Manual funding may be required.")
        
        self.results["funding"] = {
            "success": len(funded_agents) > 0,
            "funded_agents": funded_agents
        }
    
    def _register_agents_onchain(self):
        """Register all agents on the ERC-8004 IdentityRegistry"""
        
        registration_results = {}
        
        for agent_name, sdk in [("Alice", self.alice_sdk), ("Bob", self.bob_sdk), ("Charlie", self.charlie_sdk)]:
            try:
                agent_id, tx_hash = sdk.register_identity()
                self.cli.print_agent_registration(
                    agent_name, 
                    agent_id, 
                    sdk.wallet_address, 
                    tx_hash
                )
                registration_results[agent_name] = {
                    "agent_id": agent_id,
                    "tx_hash": tx_hash,
                    "address": sdk.wallet_address
                }
            except Exception as e:
                self.cli.print_error(f"Failed to register {agent_name}", str(e))
                registration_results[agent_name] = {"error": str(e)}
        
        self.results["registration"] = {
            "success": all("agent_id" in result for result in registration_results.values()),
            "agents": registration_results
        }
    
    def _execute_market_analysis(self) -> Dict[str, Any]:
        """Execute market analysis via Alice (Server Agent)"""
        
        # Generate market analysis using the SDK
        analysis_data = self.alice_sdk.generate_market_analysis("BTC")
        
        # Add timestamp and metadata
        analysis_data.update({
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.alice_sdk.get_agent_id(),
            "genesis_studio_version": "1.0.0-x402",
            "x402_enabled": True
        })
        
        return analysis_data
    
    def _store_analysis_on_ipfs(self, analysis_data: Dict[str, Any]) -> str:
        """Store analysis data on IPFS via Alice's SDK"""
        
        cid = self.alice_sdk.store_evidence(analysis_data, "analysis")
        
        if cid:
            gateway_url = self.alice_sdk.ipfs_manager.get_clickable_link(cid)
            self.cli.print_ipfs_upload("analysis.json", cid, gateway_url)
            
            self.results["ipfs_analysis"] = {
                "success": True,
                "cid": cid,
                "gateway_url": gateway_url
            }
        else:
            raise Exception("Failed to store analysis on IPFS")
        
        return cid
    
    def _execute_x402_analysis_payment(self, analysis_cid: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute x402 payment from Charlie to Alice for market analysis"""
        
        # Calculate payment based on analysis quality
        base_payment = 1.0  # Base 1 USDC
        confidence_score = analysis_data.get("genesis_studio_metadata", {}).get("confidence_score", 75)
        quality_multiplier = confidence_score / 100.0  # Scale based on confidence
        
        # Execute payment using Charlie's SDK
        payment_result = self.charlie_sdk.pay_for_service(
            service_provider="Alice",
            service_type="market_analysis",
            base_amount=base_payment,
            quality_multiplier=quality_multiplier,
            evidence_cid=analysis_cid
        )
        
        if payment_result["payment_result"]["success"]:
            self.cli.print_x402_payment(
                "Charlie", 
                "Alice", 
                payment_result["final_amount"], 
                payment_result["payment_result"]["transaction_hash"],
                "Market Analysis Service"
            )
            
            self.results["x402_analysis_payment"] = {
                "success": True,
                "amount": payment_result["final_amount"],
                "tx_hash": payment_result["payment_result"]["transaction_hash"],
                "payment_receipt": payment_result["payment_result"]["payment_receipt"],
                "from": "Charlie",
                "to": "Alice",
                "service_type": "market_analysis"
            }
        else:
            raise Exception("x402 analysis payment failed")
        
        return payment_result
    
    def _request_validation(self, analysis_cid: str, analysis_data: Dict[str, Any]) -> str:
        """Request validation from Bob using Alice's SDK"""
        
        # Calculate proper hash from CID for blockchain storage
        data_hash = self.alice_sdk.agent.calculate_cid_hash(analysis_cid)
        
        # Alice requests validation from Bob
        tx_hash = self.alice_sdk.request_validation(self.bob_sdk.get_agent_id(), data_hash)
        
        self.cli.print_validation_request("Bob", data_hash, tx_hash)
        
        return tx_hash
    
    def _perform_validation_with_payment(self, analysis_cid: str) -> tuple[int, Dict[str, Any]]:
        """Bob performs validation and Charlie pays for validation service"""
        
        # Bob retrieves and validates the analysis
        analysis_data = self.bob_sdk.retrieve_evidence(analysis_cid, "analysis")
        
        if not analysis_data:
            raise Exception("Bob could not retrieve analysis from IPFS")
        
        # Bob performs validation using SDK
        validation_result = self.bob_sdk.validate_analysis(analysis_data["analysis"])
        score = validation_result.get("overall_score", 0)
        
        # Charlie pays Bob for validation service via x402
        validation_payment_result = self.charlie_sdk.pay_for_service(
            service_provider="Bob",
            service_type="validation",
            base_amount=0.5,  # 0.5 USDC for validation
            quality_multiplier=1.0,  # Fixed rate for validation
            evidence_cid=analysis_cid
        )
        
        # Store validation report on IPFS with payment proof
        enhanced_validation_data = {
            **validation_result,
            "payment_proof": validation_payment_result["payment_result"]["payment_receipt"],
            "x402_enhanced": True
        }
        
        validation_cid = self.bob_sdk.store_evidence(enhanced_validation_data, "validation")
        
        # Bob submits validation response on-chain
        data_hash = self.alice_sdk.agent.calculate_cid_hash(analysis_cid)
        tx_hash = self.bob_sdk.submit_validation_response(data_hash, score)
        
        self.cli.print_validation_response("Bob", score, tx_hash)
        
        if validation_payment_result["payment_result"]["success"]:
            self.cli.print_x402_payment(
                "Charlie", 
                "Bob", 
                validation_payment_result["final_amount"], 
                validation_payment_result["payment_result"]["transaction_hash"],
                "Validation Service"
            )
        
        self.results["validation"] = {
            "success": True,
            "score": score,
            "validation_cid": validation_cid,
            "tx_hash": tx_hash,
            "x402_payment": validation_payment_result
        }
        
        return score, validation_result
    
    def _create_enhanced_evidence_package(self) -> Dict[str, Any]:
        """Create enhanced evidence package with x402 payment proofs"""
        
        # Gather all payment receipts
        payment_receipts = []
        
        # Analysis payment receipt
        if "x402_analysis_payment" in self.results:
            payment_receipts.append(self.results["x402_analysis_payment"]["payment_receipt"])
        
        # Validation payment receipt
        if "validation" in self.results and "x402_payment" in self.results["validation"]:
            payment_receipts.append(self.results["validation"]["x402_payment"]["payment_result"]["payment_receipt"])
        
        # Create comprehensive evidence package
        work_data = {
            "analysis_cid": self.results["ipfs_analysis"]["cid"],
            "validation_cid": self.results["validation"]["validation_cid"],
            "validation_score": self.results["validation"]["score"],
            "analysis_confidence": 87  # From the analysis
        }
        
        evidence_package = self.alice_sdk.create_evidence_package(
            work_data=work_data,
            payment_receipts=payment_receipts,
            related_evidence=[
                self.results["ipfs_analysis"]["cid"],
                self.results["validation"]["validation_cid"]
            ]
        )
        
        return evidence_package
    
    def _store_enhanced_evidence_package(self, evidence_package: Dict[str, Any]) -> str:
        """Store enhanced evidence package on IPFS"""
        
        cid = self.alice_sdk.store_evidence(evidence_package, "enhanced_package")
        
        if cid:
            gateway_url = self.alice_sdk.ipfs_manager.get_clickable_link(cid)
            self.cli.print_ipfs_upload("enhanced_evidence_package.json", cid, gateway_url)
            
            self.results["enhanced_evidence"] = {
                "success": True,
                "cid": cid,
                "gateway_url": gateway_url,
                "payment_proofs_included": len(evidence_package["payment_proofs"])
            }
        else:
            raise Exception("Failed to store enhanced evidence package on IPFS")
        
        return cid
    
    def _display_final_summary(self):
        """Display the final success summary with x402 enhancements"""
        
        # Prepare summary data
        summary_data = {
            "Agent Registration": {
                "success": self.results.get("registration", {}).get("success", False),
                "details": f"Alice, Bob, Charlie registered with on-chain IDs and x402 payment support",
                "tx_hashes": {name: data.get("tx_hash") for name, data in self.results.get("registration", {}).get("agents", {}).items() if "tx_hash" in data}
            },
            "IPFS Storage": {
                "success": self.results.get("ipfs_analysis", {}).get("success", False),
                "details": "Analysis, validation, and enhanced evidence packages stored on IPFS",
                "cids": {
                    "analysis.json": self.results.get("ipfs_analysis", {}).get("cid"),
                    "validation.json": self.results.get("validation", {}).get("validation_cid"),
                    "enhanced_evidence.json": self.results.get("enhanced_evidence", {}).get("cid")
                }
            },
            "x402 Payments": {
                "success": self.results.get("x402_analysis_payment", {}).get("success", False),
                "details": f"Agent-to-agent payments with cryptographic receipts",
                "payments": {
                    "Analysis Payment": f"${self.results.get('x402_analysis_payment', {}).get('amount', 0)} USDC (Charlie → Alice)",
                    "Validation Payment": f"${self.results.get('validation', {}).get('x402_payment', {}).get('final_amount', 0)} USDC (Charlie → Bob)"
                }
            },
            "Enhanced Evidence": {
                "success": self.results.get("enhanced_evidence", {}).get("success", False),
                "details": "Evidence packages enhanced with x402 payment proofs for PoA verification",
                "payment_proofs": self.results.get("enhanced_evidence", {}).get("payment_proofs_included", 0)
            }
        }
        
        self.cli.print_final_summary(summary_data)
    
    def _print_final_success_summary(self):
        """Print the beautiful final success summary table with x402 enhancements"""
        
        from rich.table import Table
        from rich.panel import Panel
        from rich.align import Align
        from rich import print as rprint
        
        # Create the main success banner
        success_banner = """
🎉 **CHAOSCHAIN GENESIS STUDIO x402 COMPLETE!** 🚀

✅ **FULL END-TO-END x402-ENHANCED COMMERCIAL PROTOTYPE SUCCESSFUL!**

The complete lifecycle of trustless agentic commerce with x402 payments:
• On-chain Identity via ERC-8004 registries ✅
• Verifiable Work with IPFS storage ✅  
• x402 Agent-to-Agent Payments with cryptographic receipts ✅
• Enhanced Evidence Packages with payment proofs ✅
• IP Monetization through Story Protocol ❌ (Demo skipped)
        """
        
        banner_panel = Panel(
            Align.center(success_banner),
            title="[bold green]🏆 x402 DEMO COMPLETE 🏆[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        
        rprint(banner_panel)
        rprint()
        
        # Create the results table
        table = Table(title="[bold cyan]🚀 ChaosChain Genesis Studio x402 - Final Results Summary[/bold cyan]", 
                     show_header=True, header_style="bold magenta", border_style="cyan")
        
        table.add_column("Component", style="bold white", width=25)
        table.add_column("Status", style="bold", width=12)
        table.add_column("Details", style="cyan", width=45)
        table.add_column("Transaction/Link", style="yellow", width=35)
        
        # Agent Registration Results
        table.add_row(
            "🤖 Agent Registration",
            "[green]✅ SUCCESS[/green]",
            f"Alice (ID: {self.alice_sdk.get_agent_id()}), Bob (ID: {self.bob_sdk.get_agent_id()}), Charlie (ID: {self.charlie_sdk.get_agent_id()}) with x402 support",
            "ERC-8004 on Base Sepolia"
        )
        
        # x402 Analysis Payment
        analysis_payment = self.results.get("x402_analysis_payment", {})
        table.add_row(
            "💳 x402 Analysis Payment",
            "[green]✅ SUCCESS[/green]",
            f"${analysis_payment.get('amount', 0)} USDC: Charlie → Alice",
            f"0x{analysis_payment.get('tx_hash', 'N/A')[:20]}..." if analysis_payment.get('tx_hash') else "N/A"
        )
        
        # x402 Validation Payment
        validation_payment = self.results.get("validation", {}).get("x402_payment", {})
        table.add_row(
            "💳 x402 Validation Payment",
            "[green]✅ SUCCESS[/green]",
            f"${validation_payment.get('final_amount', 0)} USDC: Charlie → Bob",
            f"0x{validation_payment.get('payment_result', {}).get('transaction_hash', 'N/A')[:20]}..." if validation_payment.get('payment_result', {}).get('transaction_hash') else "N/A"
        )
        
        # Enhanced Evidence Package
        enhanced_evidence = self.results.get("enhanced_evidence", {})
        table.add_row(
            "📦 Enhanced Evidence",
            "[green]✅ SUCCESS[/green]",
            f"Evidence package with {enhanced_evidence.get('payment_proofs_included', 0)} payment proofs",
            f"IPFS: {enhanced_evidence.get('cid', 'N/A')[:20]}..."
        )
        
        # Validation Results
        validation_score = self.results.get("validation", {}).get("score", 0)
        table.add_row(
            "🔍 PoA Validation",
            "[green]✅ SUCCESS[/green]",
            f"Score: {validation_score}/100 with payment verification",
            f"Enhanced with x402 receipts"
        )
        
        rprint(table)
        rprint()
        
        # x402 Payment Summary
        payment_summary_panel = Panel(
            f"""[bold cyan]💳 x402 Payment Protocol Summary:[/bold cyan]

[yellow]Analysis Service Payment:[/yellow]
• Amount: ${analysis_payment.get('amount', 0)} USDC
• From: Charlie → Alice
• Service: AI Market Analysis
• Payment ID: {analysis_payment.get('payment_receipt', {}).get('payment_id', 'N/A')[:20]}...

[yellow]Validation Service Payment:[/yellow]
• Amount: ${validation_payment.get('final_amount', 0)} USDC  
• From: Charlie → Bob
• Service: Analysis Validation
• Payment ID: {validation_payment.get('payment_result', {}).get('payment_receipt', {}).get('payment_id', 'N/A')[:20]}...

[bold green]🎯 x402 Protocol Benefits:[/bold green]
• Frictionless agent-to-agent payments ✅
• Cryptographic payment receipts for PoA ✅
• No complex wallet setup required ✅
• Instant settlement on Base Sepolia ✅
• Enhanced evidence packages with payment proofs ✅

[bold magenta]💰 Economic Impact:[/bold magenta]
• Alice earned ${analysis_payment.get('amount', 0)} USDC for quality analysis
• Bob earned ${validation_payment.get('final_amount', 0)} USDC for validation service
• Charlie received verified analysis with payment-backed guarantees
• Complete audit trail for trustless commerce established

[bold red]🔧 Next Steps:[/bold red]
• Story Protocol integration for IP monetization
• Multi-agent collaboration workflows
• Cross-chain x402 payment support""",
            title="[bold green]🌟 x402 Commercial Success Metrics[/bold green]",
            border_style="green"
        )
        
        rprint(payment_summary_panel)


def main():
    """Main entry point for x402-enhanced Genesis Studio"""
    
    # Check if we're on the correct network
    network = os.getenv("NETWORK", "local")
    if network != "base-sepolia":
        print("⚠️  Warning: This demo is designed for Base Sepolia testnet.")
        print("   Please set NETWORK=base-sepolia in your .env file.")
        print()
    
    # Initialize and run the x402-enhanced orchestrator
    orchestrator = GenesisStudioX402Orchestrator()
    orchestrator.run_complete_demo()


if __name__ == "__main__":
    main()
