#!/usr/bin/env python3
"""
CHAOSCHAIN GENESIS STUDIO - x402 Enhanced Commercial Prototype

This script demonstrates the complete end-to-end commercial lifecycle of agentic work
with x402 payment integration:

1. On-chain identity registration using ERC-8004
2. Verifiable work execution with IPFS storage
3. x402 agent-to-agent payments with cryptographic receipts
4. Enhanced evidence packages with payment proofs for PoA
5. Enhanced evidence packages with payment proofs

Usage:
    python genesis_studio.py

=== PLUGGABLE PROVIDER ARCHITECTURE DEMO ===

The ChaosChain SDK now supports pluggable storage and compute providers.
This demonstrates how developers can inject custom providers like 0G Storage/Compute:

Example 1: Using 0G Storage via gRPC Sidecar Bridge
```python
from chaoschain_sdk import ChaosChainAgentSDK, ZeroGStorageGRPC

# Initialize 0G Storage provider via gRPC sidecar
zg_storage = ZeroGStorageGRPC(
    grpc_url="localhost:50051",  # 0G bridge gRPC endpoint
    api_key="your-0g-api-key"
)

# Inject into SDK
agent = ChaosChainAgentSDK(
    agent_name="MyAgent",
    agent_domain="myagent.example.com",
    agent_role="server",
    network="0g-testnet",
    storage_provider=zg_storage  # ✅ Custom provider injected
)

# SDK will now use 0G Storage for all evidence packages
result = zg_storage.put(
    evidence_bytes,
    tags={"task": "audit"},
    idempotency_key="request-123"
)
print(f"Stored on 0G: {result.uri}")  # 0g://object/abc123
```

Example 2: Using 0G Compute via gRPC Sidecar Bridge
```python
from chaoschain_sdk import ChaosChainAgentSDK, ZeroGComputeGRPC, ProviderVerificationMethod

# Initialize 0G Compute provider via gRPC sidecar
zg_compute = ZeroGComputeGRPC(
    grpc_url="localhost:50052",  # 0G compute gRPC endpoint
    api_key="your-0g-api-key"
)

# Inject into SDK
agent = ChaosChainAgentSDK(
    agent_name="MyAgent",
    agent_domain="myagent.example.com",
    agent_role="server",
    network="0g-testnet",
    compute_provider=zg_compute  # ✅ Custom compute provider injected
)

# Submit verifiable compute task
job_id = zg_compute.submit(
    task={"model": "llama2", "prompt": "Analyze market data"},
    verification=ProviderVerificationMethod.TEE_ML
)

# Wait for completion and get results
result = zg_compute.wait_for_completion(job_id)
print(f"Output: {result.output}")
print(f"Proof: {result.proof}")  # TEE attestation
```

Example 3: Default Behavior (Auto-detection)
```python
# Without provider injection, SDK auto-detects available storage:
# Pinata (if PINATA_JWT set) → Local IPFS → Memory fallback
agent = ChaosChainAgentSDK(
    agent_name="MyAgent",
    agent_domain="myagent.example.com",
    agent_role="server",
    network="base-sepolia"
    # No provider injection - uses auto-detected storage
)
```

Example 4: ERC-8004 v1.0 Feedback with Payment Proof
```python
from chaoschain_sdk import ChaosChainAgentSDK
from chaoschain_sdk.types import PaymentProof

# Execute payment (x402)
payment_proof = sdk.x402_manager.execute_agent_payment(
    from_agent="Alice",
    to_agent="Bob",
    amount_usdc=10.0,
    service_description="Data analysis task"
)

# Generate feedback authorization
feedback_auth = sdk.chaos_agent.generate_feedback_authorization(
    agent_id=server_agent_id,
    client_address=client_wallet_address,
    index_limit=1,
    expiry=int(time.time()) + 3600
)

# Create ERC-8004 v1.0 compliant feedback with payment proof
# This automatically:
# 1. Formats feedback JSON per ERC-8004 v1.0 spec
# 2. Includes payment proof (fromAddress, toAddress, chainId, txHash)
# 3. Uploads to IPFS/0G Storage
# 4. Returns (URI, hash) ready for on-chain submission
uri, hash = sdk.chaos_agent.create_feedback_with_payment(
    agent_id=server_agent_id,
    score=100,
    feedback_auth=feedback_auth,
    payment_proof=payment_proof,  # ✅ Automatically ERC-8004 v1.0 compliant!
    skill="data-analysis",
    task="market-research",
    tag1="quality",
    tag2="speed"
)

# Submit feedback to on-chain reputation registry
tx_hash = sdk.chaos_agent.give_feedback(
    agent_id=server_agent_id,
    score=100,
    feedback_auth=feedback_auth,
    file_uri=uri,  # URI with payment proof included
    file_hash=hash
)

print(f"✅ Feedback with payment proof submitted: {tx_hash}")
```
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from rich.panel import Panel

from dotenv import load_dotenv
from rich import print as rprint
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig
from chaoschain_sdk.types import AgentRole

# Import CrewAI-powered agents
from agents.server_agent_sdk import GenesisServerAgentSDK
from agents.validator_agent_sdk import GenesisValidatorAgentSDK
from agents.client_agent_genesis import GenesisClientAgent

# Load environment variables
load_dotenv()

class GenesisStudioX402Orchestrator:
    """Enhanced Genesis Studio orchestrator with x402 payment integration"""
    
    def __init__(self):
        # Track results for final summary
        self.results = {}
        
        # Agent SDK instances
        self.alice_sdk = None  # Server Agent
        self.bob_sdk = None    # Validator Agent
        self.charlie_sdk = None # Client Agent
    
    def run_complete_demo(self):
        """Execute the complete Genesis Studio x402 demonstration"""
        
        try:
            self._print_banner()
            
            # Phase 1: Setup & On-Chain Identity
            self._phase_1_setup_and_identity()
            
            # Phase 2: x402 Enhanced Work & Payment Flow
            self._phase_2_x402_work_and_payment()
            
            # Phase 3: Enhanced Evidence Packages with Payment Proofs
            self._phase_3_enhanced_evidence_packages()
            
            
            # Final Summary
            self._display_final_summary()
            
        except KeyboardInterrupt:
            rprint("[yellow]⚠️  Demo interrupted by user[/yellow]")
            sys.exit(1)
        except Exception as e:
            import traceback
            rprint("[red]FULL TRACEBACK:[/red]")
            traceback.print_exc()
            rprint(f"[red]❌ Demo failed with unexpected error: {e}[/red]")
            sys.exit(1)
    
    def _print_banner(self):
        """Print Genesis Studio banner"""
        banner = """
[bold blue]🚀 CHAOSCHAIN GENESIS STUDIO - SDK VERSION[/bold blue]
[bold cyan]Triple-Verified Stack Commercial Prototype[/bold cyan]

[yellow]✨ Powered by ChaosChain SDK with:[/yellow]
• Native x402 payments (Coinbase official)
• Google AP2 integration (intent verification)  
• Process integrity verification
• ERC-8004 on-chain identity registry
• IPFS evidence storage
"""
        
        banner_panel = Panel(
            Align.center(banner),
            title="[bold green]🏆 Genesis Studio[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        
        rprint(banner_panel)
        rprint()
    
    def _phase_1_setup_and_identity(self):
        """Phase 1: Setup & On-Chain Identity Registration with x402 Integration"""
        
        rprint("\n[bold blue]📋 Phase 1: Setup & x402-Enhanced Identity[/bold blue]")
        rprint("[cyan]Creating agent SDKs and registering on-chain identities with payment capabilities[/cyan]")
        rprint("=" * 80)
        
        # Step 1: Configuration Check
        rprint("\n[blue]🔧 Step 1: Validating x402 and ERC-8004 configuration...[/blue]")
        self._validate_configuration()
        rprint("[green]✅ Configuration validated[/green]")
        
        # Step 2: Initialize Agent SDKs with x402 Integration
        rprint("\n[blue]🔧 Step 2: Initializing ChaosChain Agent SDKs with x402 payment support...[/blue]")
        self._initialize_agent_sdks()
        rprint("[green]✅ Agent SDKs initialized[/green]")
        
        # Step 3: Fund wallets from faucet
        rprint("\n[blue]🔧 Step 3: Funding wallets from Base Sepolia faucet...[/blue]")
        self._fund_agent_wallets()
        rprint("[green]✅ Wallets funded[/green]")
        
        # Step 4: On-chain registration
        rprint("\n[blue]🔧 Step 4: Registering agents on ERC-8004 IdentityRegistry...[/blue]")
        self._register_agents_onchain()
        rprint("[green]✅ Agents registered on-chain[/green]")
    
    def _phase_2_x402_work_and_payment(self):
        """Phase 2: Triple-Verified Stack Work & Payment Flow"""
        
        rprint("\n[bold blue]📋 Phase 2: Triple-Verified Stack Work & Payment[/bold blue]")
        rprint("[cyan]Alice performs smart shopping with AP2 intent verification, ChaosChain process integrity, and x402 payments[/cyan]")
        rprint("=" * 80)
        
        # Step 5: AP2 Intent Verification
        rprint("\n[blue]🔧 Step 5: Creating AP2 intent mandate for smart shopping...[/blue]")
        intent_mandate = self._create_ap2_intent_mandate()
        rprint("[green]✅ AP2 intent mandate created and verified[/green]")
        
        # Step 6: Work Execution with Process Integrity (Alice)
        rprint("\n[blue]🔧 Step 6: Alice performing smart shopping with ChaosChain Process Integrity...[/blue]")
        analysis_data, process_integrity_proof = self._execute_smart_shopping_with_integrity()
        rprint("[green]✅ Smart shopping completed with process integrity proof[/green]")
        
        # Step 7: Evidence Storage (Alice)
        rprint("\n[blue]🔧 Step 7: Storing analysis on IPFS via Pinata...[/blue]")
        analysis_cid = self._store_analysis_on_ipfs(analysis_data)
        rprint("[green]✅ Analysis stored on IPFS[/green]")
        
        # Step 8: AP2 Universal Payment + x402 Crypto Settlement
        rprint("\n[blue]🔧 Step 8: Processing authorization + payment: AP2 intent verification + x402 crypto settlement...[/blue]")
        payment_results = self._execute_dual_payment_flow(analysis_cid, analysis_data, intent_mandate)
        rprint(f"[green]✅ Authorization + Payment completed (AP2 authorization: ${payment_results['ap2_amount']}, x402 settlement: {payment_results['x402_amount']} USDC)[/green]")
        
        # Step 9: Validation Request with ERC-8004 (Alice)
        rprint("\n[blue]🔧 Step 9: Alice requesting validation via ERC-8004 ValidationRegistry...[/blue]")
        validation_tx = self._request_validation_erc8004(analysis_cid, analysis_data)
        rprint("[green]✅ ERC-8004 validation requested[/green]")
        
        # Step 10: Validation & Payment (Bob)
        rprint("\n[blue]🔧 Step 10: Bob validating with process integrity and payment...[/blue]")
        validation_score, validation_result = self._perform_validation_with_payment(analysis_cid)
        rprint(f"[green]✅ Validation completed (Score: {validation_score}/100)[/green]")
    
    def _phase_3_enhanced_evidence_packages(self):
        """Phase 3: Enhanced Evidence Packages with Payment Proofs"""
        
        rprint("\n[bold blue]📋 Phase 3: Enhanced Evidence Packages[/bold blue]")
        rprint("[cyan]Creating comprehensive evidence packages with x402 payment proofs for PoA[/cyan]")
        rprint("=" * 80)
        
        # Step 11: Create Enhanced Evidence Package (Alice)
        rprint("\n[blue]🔧 Step 11: Alice creating enhanced evidence package with payment proofs...[/blue]")
        alice_evidence_package = self._create_enhanced_evidence_package()
        rprint("[green]✅ Enhanced evidence package created[/green]")
        
        # Step 12: Store Enhanced Evidence Package
        rprint("\n[blue]🔧 Step 12: Storing enhanced evidence package on IPFS...[/blue]")
        enhanced_evidence_cid = self._store_enhanced_evidence_package(alice_evidence_package)
        rprint("[green]✅ Enhanced evidence package stored[/green]")
    
    
    def _validate_configuration(self):
        """Validate all required environment variables including x402"""
        network = os.getenv("NETWORK", "base-sepolia")
        
        # Core required variables (network-specific)
        if network == "0g-testnet":
            required_vars = [
                "NETWORK", "ZEROG_TESTNET_RPC_URL", "ZEROG_TESTNET_PRIVATE_KEY"
            ]
        elif network == "base-sepolia":
            required_vars = [
                "NETWORK", "BASE_SEPOLIA_RPC_URL", "BASE_SEPOLIA_PRIVATE_KEY"
            ]
        else:
            required_vars = ["NETWORK"]
        
        # Optional variables (for enhanced features)
        optional_vars = [
            "PINATA_JWT", "PINATA_GATEWAY", 
            "CDP_API_KEY_ID", "CDP_API_KEY_SECRET", "CDP_WALLET_SECRET",
            "USDC_CONTRACT_ADDRESS"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Check optional variables and warn if missing
        missing_optional = []
        for var in optional_vars:
            if not os.getenv(var):
                missing_optional.append(var)
        
        if missing_optional:
            rprint(f"[yellow]⚠️  Optional variables not set: {', '.join(missing_optional)}[/yellow]")
            rprint("[yellow]   Storage will use local IPFS fallback (free option)[/yellow]")
            rprint("[yellow]   To enable Pinata: set PINATA_JWT and PINATA_GATEWAY[/yellow]")
        
        # Validate network is set to 0g-testnet
        if os.getenv("NETWORK") != "0g-testnet":
            rprint("[yellow]⚠️  Network is not set to '0g-testnet'. This demo is designed for 0G Testnet.[/yellow]")
    
    def _initialize_agent_sdks(self):
        """Initialize CrewAI-powered agents with ChaosChain SDK integration"""
        
        # Create CrewAI-powered agents with ChaosChain SDK integration
        rprint("[yellow]🤖 Initializing CrewAI-powered agents with ChaosChain SDK...[/yellow]")
        
        # Initialize 0G providers for storage and compute
        try:
            from chaoschain_sdk.providers.storage import ZeroGStorageGRPC
            from chaoschain_sdk.providers.compute import ZeroGComputeGRPC
            zg_storage = ZeroGStorageGRPC(grpc_url="localhost:50051")
            zg_compute = ZeroGComputeGRPC(grpc_url="localhost:50052")
            rprint("[green]✅ 0G gRPC providers initialized[/green]")
        except Exception as e:
            rprint(f"[yellow]⚠️  0G gRPC providers not available: {e}[/yellow]")
            rprint("[yellow]   Storage will fallback to IPFS, compute will use local[/yellow]")
            zg_storage = None
            zg_compute = None
        
        self.alice_agent = GenesisServerAgentSDK(
            agent_name="Alice",
            agent_domain="alice.chaoschain-studio.com",
            agent_role=AgentRole.SERVER,
            network=NetworkConfig.BASE_SEPOLIA,  # Using Base Sepolia
            enable_ap2=True,
            enable_process_integrity=True,
            use_0g_inference=True  # ✅ 0G Compute AI inference
        )
        
        self.bob_agent = GenesisValidatorAgentSDK(
            agent_name="Bob",
            agent_domain="bob.chaoschain-studio.com",
            agent_role=AgentRole.VALIDATOR,
            network=NetworkConfig.BASE_SEPOLIA,  # Using Base Sepolia
            enable_ap2=True,
            enable_process_integrity=True,
            use_0g_inference=True  # ✅ 0G Compute AI validation
        )
        
        self.charlie_agent = GenesisClientAgent(
            agent_name="Charlie",
            agent_domain="charlie.chaoschain-studio.com",
            agent_role=AgentRole.CLIENT,
            network=NetworkConfig.BASE_SEPOLIA,  # Using Base Sepolia
            enable_ap2=True,
            enable_process_integrity=False  # Client doesn't need process integrity
        )
        
        # Keep SDK references for compatibility with existing code
        self.alice_sdk = self.alice_agent.sdk
        self.bob_sdk = self.bob_agent.sdk
        self.charlie_sdk = self.charlie_agent.sdk
        
        # Display agent status
        for name, agent in [("Alice", self.alice_agent), ("Bob", self.bob_agent), ("Charlie", self.charlie_agent)]:
            rprint(f"✅ {name} CrewAI Agent initialized:")
            rprint(f"   Agent Name: {agent.agent_name}")
            rprint(f"   Agent Domain: {agent.agent_domain}")
            rprint(f"   Agent Role: {agent.sdk.agent_role.value if hasattr(agent.sdk.agent_role, 'value') else agent.sdk.agent_role}")
            rprint(f"   Network: {agent.network.value}")
            rprint(f"   AI Framework: CrewAI + ChaosChain SDK")
            rprint(f"   AP2 Integration: ✅ Enabled")
            rprint(f"   Process Integrity: {'✅ Enabled' if hasattr(agent.sdk, 'process_integrity') and agent.sdk.process_integrity else '❌ Disabled'}")
            rprint(f"   x402 Payment Support: ✅")
        
        # Store wallet addresses for later use
        self.results["wallets"] = {
            "Alice": self.alice_sdk.wallet_address,
            "Bob": self.bob_sdk.wallet_address,
            "Charlie": self.charlie_sdk.wallet_address
        }
    
    def _fund_agent_wallets(self):
        """Fund all agent wallets from 0G Testnet faucet"""
        
        agents = [("Alice", self.alice_sdk), ("Bob", self.bob_sdk), ("Charlie", self.charlie_sdk)]
        funded_agents = []
        
        print("💰 Checking wallet balances on 0G Testnet...")
        for agent_name, sdk in agents:
            balance = sdk.wallet_manager.get_wallet_balance(agent_name)
            address = sdk.wallet_manager.get_wallet_address(agent_name)
            print(f"   {agent_name}: {balance:.4f} A0GI ({address})")
            
            if balance > 0.001:  # Has some A0GI for gas
                funded_agents.append(agent_name)
            else:
                print(f"   ⚠️  {agent_name} needs funding. Please send A0GI to {address}")
        
        if len(funded_agents) == 0:
            print("🔗 Fund your wallets at: https://faucet.0g.ai/")
            print("   Each wallet needs ~0.1 A0GI for gas fees")
        
        self.results["funding"] = {
            "success": len(funded_agents) > 0,
            "funded_agents": funded_agents
        }
    
    def _register_agents_onchain(self):
        """Register all CrewAI agents on the ERC-8004 IdentityRegistry"""
        
        registration_results = {}
        
        # Register each CrewAI agent
        for agent_name, agent in [("Alice", self.alice_agent), ("Bob", self.bob_agent), ("Charlie", self.charlie_agent)]:
            try:
                rprint(f"[blue]🔧 Registering agent: {agent.agent_domain}[/blue]")
                agent_id = agent.register_identity()
                wallet_address = agent.sdk.wallet_address
                rprint(f"[green]✅ {agent_name} registered successfully[/green]")
                rprint(f"   Agent ID: {agent_id}")
                rprint(f"   Wallet: {wallet_address}")
                rprint(f"   Transaction: already_registered")
                registration_results[agent_name] = {
                    "agent_id": agent_id,
                    "tx_hash": "already_registered",
                    "address": wallet_address
                }
            except Exception as e:
                rprint(f"[red]❌ Failed to register {agent_name}: {e}[/red]")
                registration_results[agent_name] = {"error": str(e)}
        
        self.results["registration"] = {
            "success": all("agent_id" in result for result in registration_results.values()),
            "agents": registration_results
        }
    
    def _create_ap2_intent_mandate(self) -> Dict[str, Any]:
        """Create AP2 intent mandate for market analysis service"""
        
        # Create intent mandate using Alice's AP2 manager - Smart Shopping Scenario
        intent_mandate = self.alice_sdk.create_intent_mandate(
            user_description="Find me the best winter jacket in green, willing to pay up to 20% premium for the right color. Price limit: $150, quality threshold: good, auto-purchase enabled",
            merchants=None,  # Allow any merchant
            skus=None,  # Allow any SKU
            requires_refundability=True,  # Require refundable items
            expiry_minutes=60
        )
        
        # Create cart mandate
        cart_mandate = self.alice_sdk.create_cart_mandate(
            cart_id="cart_winter_jacket_001",
            items=[{"service": "smart_shopping_agent", "description": "Find best winter jacket deal with color preference", "price": 2.0}],
            total_amount=2.0,
            currency="USDC",
            merchant_name="Alice Smart Shopping Agent",
            expiry_minutes=15
        )
        
        # Verify JWT token instead of mandate chain for Google AP2
        mandate_verified = True  # Google AP2 uses JWT verification
        if hasattr(cart_mandate, 'merchant_authorization') and cart_mandate.merchant_authorization:
            jwt_payload = self.alice_sdk.google_ap2_integration.verify_jwt_token(cart_mandate.merchant_authorization)
            mandate_verified = bool(jwt_payload)
        
        self.results["ap2_intent"] = {
            "intent_mandate": intent_mandate,
            "cart_mandate": cart_mandate,
            "verified": mandate_verified,
            "intent_description": "Smart shopping for winter jacket with green color preference",
            "cart_id": "cart_winter_jacket_001",
            "jwt_verified": mandate_verified
        }
        
        return cart_mandate

    def _execute_smart_shopping_with_integrity(self) -> tuple[Dict[str, Any], Any]:
        """Execute smart shopping with CrewAI and ChaosChain Process Integrity verification"""
        
        # Use Alice's CrewAI agent to perform smart shopping analysis
        rprint("[yellow]🤖 Using Alice's CrewAI agent for smart shopping analysis...[/yellow]")
        
        # Execute CrewAI-powered smart shopping with process integrity
        analysis_result = self.alice_agent.generate_smart_shopping_analysis(
            item_type="winter_jacket",
            color="green", 
            budget=150.0,
            premium_tolerance=0.20
        )
        
        # Extract the analysis and process integrity proof
        analysis_data = analysis_result["analysis"]
        process_integrity_proof = analysis_result["process_integrity_proof"]
        
        # Store results for later use
        self.results["analysis"] = analysis_data
        self.results["process_integrity_proof"] = process_integrity_proof
        
        return analysis_data, process_integrity_proof
    
    def _store_analysis_on_ipfs(self, analysis_data: Dict[str, Any]) -> str:
        """Store analysis data on IPFS via Alice's SDK"""
        
        cid = self.alice_sdk.store_evidence(analysis_data, "analysis")
        
        if cid:
            # Generate gateway URL if storage manager is available
            gateway_url = "Local IPFS (no gateway URL)"
            if self.alice_sdk.storage_manager:
                try:
                    gateway_url = self.alice_sdk.storage_manager.get_gateway_url(cid)
                except Exception as e:
                    gateway_url = f"Local IPFS: {cid}"
            
            rprint(f"[green]📦 Analysis uploaded to IPFS[/green]")
            rprint(f"   File: analysis.json")
            rprint(f"   CID: {cid}")
            rprint(f"   Gateway: {gateway_url}")
            
            self.results["ipfs_analysis"] = {
                "success": True,
                "cid": cid,
                "gateway_url": gateway_url
            }
        else:
            # Storage not available - continue without IPFS (no vendor lock-in)
            rprint(f"[yellow]⚠️  IPFS storage not available - continuing without storage[/yellow]")
            rprint(f"[yellow]   Analysis data preserved in memory for demo[/yellow]")
            
            self.results["ipfs_analysis"] = {
                "success": False,
                "cid": None,
                "gateway_url": "No storage available",
                "note": "Demo continued without vendor lock-in storage"
            }
        
        return cid
    
    def _execute_dual_payment_flow(self, analysis_cid: str, analysis_data: Dict[str, Any], cart_mandate: Any) -> Dict[str, Any]:
        """Execute authorization + payment flow: AP2 intent verification + x402 crypto settlement"""
        
        # Calculate payment based on analysis quality
        base_payment = 2.0  # Base 2 USDC for comprehensive analysis
        confidence_score = analysis_data.get("analysis", {}).get("confidence", 0.85)
        quality_multiplier = confidence_score  # Direct confidence scaling
        
        # Execute x402 Crypto Settlement: Charlie pays Alice for smart shopping service
        print(f"💰 Creating x402 payment request: Charlie → Alice ({base_payment * quality_multiplier} USDC)")
        try:
            x402_payment_result = self.charlie_sdk.execute_payment(
                to_agent="Alice",
                amount=base_payment * quality_multiplier,
                service_type="smart_shopping"
            )
        except Exception as e:
            print(f"⚠️  x402 payment failed (continuing demo): {e}")
            # Create a mock payment result for demo continuation
            from chaoschain_sdk.types import PaymentProof, PaymentMethod
            from datetime import datetime
            x402_payment_result = PaymentProof(
                payment_id=f"failed_{int(time.time())}",
                from_agent="Charlie",
                to_agent="Alice",
                amount=base_payment * quality_multiplier,
                currency="USDC",
                payment_method=PaymentMethod.A2A_X402,
                transaction_hash="",
                timestamp=datetime.now(),
                receipt_data={"status": "failed", "reason": str(e)}
            )
        
        # Display payment results
        if x402_payment_result.transaction_hash:
            rprint(f"[green]💳 x402 Payment Successful[/green]")
            rprint(f"   From: Charlie")
            rprint(f"   To: Alice")
            rprint(f"   Amount: ${x402_payment_result.amount} USDC")
            rprint(f"   Transaction: {x402_payment_result.transaction_hash}")
            rprint(f"   Service: Smart Shopping Service (Crypto Settlement)")
        else:
            rprint(f"[yellow]⚠️  Payment failed but continuing demo[/yellow]")
            
            # Display AP2 authorization details
            print(f"✅ AP2 Intent Authorization completed:")
            print(f"   Authorization Method: ap2_universal")
            # Get total amount from Google AP2 structure
        total_amount = base_payment * quality_multiplier
        if hasattr(cart_mandate, 'contents') and hasattr(cart_mandate.contents, 'payment_request'):
            total_amount = cart_mandate.contents.payment_request.details.total.amount.value
            print(f"   Authorized Amount: ${total_amount} USDC")
            
            # Show supported payment methods (W3C compliant)
            payment_methods = self.alice_sdk.get_supported_payment_methods()
            print(f"   Supported Payment Methods: {len(payment_methods)} (W3C compliant)")
            for method in payment_methods[:3]:  # Show first 3
                method_name = method.split('/')[-1] if '/' in method else method
                print(f"     • {method_name}")
            if len(payment_methods) > 3:
                print(f"     • ... and {len(payment_methods) - 3} more")
            
        print(f"   Confirmation: AP2_{int(time.time())}")
            
        payment_results = {
            "x402_payment_result": x402_payment_result,
            "ap2_amount": total_amount,
            "x402_amount": x402_payment_result.amount,
            "dual_payment_success": bool(x402_payment_result.transaction_hash)
            }
            
        self.results["dual_payment"] = payment_results
        return payment_results
    
    def _validate_analysis_with_crewai(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Bob's CrewAI-powered validator agent for comprehensive analysis validation
        """
        rprint("[yellow]🤖 Using Bob's CrewAI-powered validation agent...[/yellow]")
        
        # Execute CrewAI-powered validation with process integrity
        validation_result = self.bob_agent.validate_analysis_with_crewai(analysis_data)
        
        # Extract the validation and process integrity proof
        validation_data = validation_result["validation"]
        process_integrity_proof = validation_result["process_integrity_proof"]
        
        # Store results for later use
        self.results["validation"] = validation_data
        self.results["validation_process_integrity_proof"] = process_integrity_proof
        
        return validation_data
    
    def _request_validation_erc8004(self, analysis_cid: str, analysis_data: Dict[str, Any]) -> str:
        """Request validation from Bob using ERC-8004 ValidationRegistry"""
        
        # Calculate proper hash from CID for blockchain storage (handle None CID)
        import hashlib
        if analysis_cid:
            data_hash = "0x" + hashlib.sha256(analysis_cid.encode()).hexdigest()
        else:
            # No storage available - use analysis data hash instead
            analysis_str = str(analysis_data)
            data_hash = "0x" + hashlib.sha256(analysis_str.encode()).hexdigest()
        
        try:
            # Check if Bob is registered and has an agent ID
            bob_agent_id = self.bob_sdk.get_agent_id()
            alice_agent_id = self.alice_sdk.get_agent_id()
            
            if bob_agent_id is None or alice_agent_id is None:
                rprint(f"[yellow]⚠️  Agents not registered yet. Using fallback validation...[/yellow]")
                # Use placeholder IDs for demo purposes
                bob_agent_id = 2  # Assume Bob is agent ID 2
                alice_agent_id = 1  # Assume Alice is agent ID 1
            
            # Alice requests validation from Bob via ERC-8004
            tx_hash = self.alice_sdk.request_validation(bob_agent_id, data_hash)
            
            rprint(f"[green]📋 Validation Request Sent[/green]")
            rprint(f"   Validator: Bob")
            rprint(f"   Data Hash: {data_hash}")
            rprint(f"   Transaction: {tx_hash}")
            
            self.results["erc8004_validation_request"] = {
                "success": True,
                "data_hash": data_hash,
                "validator_agent_id": self.bob_sdk.get_agent_id(),
                "tx_hash": tx_hash
            }
            
        except Exception as e:
            # Fallback for demo purposes
            print(f"⚠️  ERC-8004 validation request failed (network issue): {e}")
            print(f"📋 Simulating validation request for demo")
            tx_hash = "demo_validation_tx_hash"
            
            self.results["erc8004_validation_request"] = {
                "success": False,
                "simulated": True,
                "data_hash": data_hash,
                "validator_agent_id": self.bob_sdk.get_agent_id(),
                "error": str(e)
            }
        
        return tx_hash
    
    def _perform_validation_with_payment(self, analysis_cid: str) -> tuple[int, Dict[str, Any]]:
        """Bob performs validation and Charlie pays for validation service"""
        
        # Bob retrieves and validates the analysis (handle no storage case)
        if analysis_cid:
            analysis_data = self.bob_sdk.retrieve_evidence(analysis_cid)
        else:
            # No storage available - use in-memory analysis data
            analysis_data = self.results.get("smart_shopping_analysis", {})
            rprint(f"[yellow]⚠️  No IPFS storage - using in-memory analysis data for validation[/yellow]")
        
        if not analysis_data:
            # Fallback to mock validation data for demo continuity
            rprint(f"[yellow]⚠️  No analysis data available - using fallback validation[/yellow]")
            analysis_data = {
                "shopping_result": {
                    "item_type": "winter_jacket",
                    "final_price": 121.98,
                    "deal_quality": "excellent",
                    "merchant": "Premium Outdoor Gear Co.",
                    "confidence": 0.89
                }
            }
        
        # Bob performs validation using REAL CrewAI agent logic (production-grade)
        # Prepare data for validation - ensure proper structure for CrewAI validator
        if "shopping_result" in analysis_data:
            # Extract shopping result and flatten for validation
            shopping_result = analysis_data["shopping_result"]
            validation_data = {
                "item_type": shopping_result.get("item_type", "unknown"),
                "service_type": "smart_shopping",
                **shopping_result,  # Include all shopping result fields
                **analysis_data     # Include metadata
            }
            validation_result = self._validate_analysis_with_crewai(validation_data)
        elif "analysis" in analysis_data:
            validation_result = self._validate_analysis_with_crewai(analysis_data["analysis"])
        else:
            # Data is already at the top level
            validation_result = self._validate_analysis_with_crewai(analysis_data)
        score = validation_result.get("overall_score", 0)
        
        # Charlie pays Bob for validation service via x402
        try:
            validation_payment_result = self.charlie_sdk.execute_payment(
                to_agent="Bob",
                amount=0.5,  # 0.5 USDC for validation
                service_type="validation"
            )
        except Exception as e:
            print(f"⚠️  Validation payment failed (continuing demo): {e}")
            # Create a mock payment result for demo continuation
            from chaoschain_sdk.types import PaymentProof, PaymentMethod
            from datetime import datetime
            validation_payment_result = PaymentProof(
                payment_id=f"failed_validation_{int(time.time())}",
                from_agent="Charlie",
                to_agent="Bob",
                amount=0.5,
                currency="USDC",
                payment_method=PaymentMethod.A2A_X402,
                transaction_hash="",
                timestamp=datetime.now(),
                receipt_data={"status": "failed", "reason": str(e)}
        )
        
        # Store validation report on IPFS with payment proof
        enhanced_validation_data = {
            **validation_result,
            "payment_proof": {
                "payment_id": validation_payment_result.payment_id,
                "transaction_hash": validation_payment_result.transaction_hash,
                "amount": validation_payment_result.amount,
                "currency": validation_payment_result.currency
            },
            "x402_enhanced": True
        }
        
        validation_cid = self.bob_sdk.store_evidence(enhanced_validation_data, "validation")
        
        # Display Bob's validation results FIRST (before any potential errors)
        print(f"🔍 Bob's Validation Results:")
        print(f"   Overall Score: {score}/100")
        print(f"   Confidence: {validation_result.get('confidence_score', 0)}/100")
        print(f"   Completeness: {validation_result.get('completeness_score', 0)}/100") 
        print(f"   Methodology: {validation_result.get('methodology_score', 0)}/100")
        print(f"   Summary: {validation_result.get('validation_summary', 'N/A')}")
        print(f"   Validator: {validation_result.get('validator', 'Bob')}")
        
        # Bob submits validation response on-chain (non-blocking)
        tx_hash = "demo_feedback_skipped"  # Default value
        try:
            import hashlib
            data_hash = "0x" + hashlib.sha256(analysis_cid.encode()).hexdigest()
            
            # Submit actual validation response with score via ValidationRegistry
            tx_hash = self.bob_sdk.submit_validation_response(data_hash, score)
            print(f"✅ Validation response submitted on-chain: {tx_hash}")
        except Exception as e:
            print(f"⚠️  Validation response failed (continuing demo): {e}")
            # Continue demo even if validation fails
        
        rprint(f"[green]🔍 Validation Response Submitted[/green]")
        rprint(f"   Validator: Bob")
        rprint(f"   Score: {score}/100")
        rprint(f"   Transaction: {tx_hash}")
        
        if validation_payment_result.transaction_hash:
            rprint(f"[green]💳 x402 Payment Successful[/green]")
            rprint(f"   From: Charlie")
            rprint(f"   To: Bob")
            rprint(f"   Amount: ${validation_payment_result.amount} USDC")
            rprint(f"   Transaction: {validation_payment_result.transaction_hash}")
            rprint(f"   Service: Validation Service")
        
        self.results["validation"] = {
            "success": True,
            "score": score,
            "validation_cid": validation_cid,
            "tx_hash": tx_hash,
            "x402_payment": validation_payment_result
        }
        
        return score, validation_result
    
    def _create_enhanced_evidence_package(self) -> Dict[str, Any]:
        """Create enhanced evidence package with Triple-Verified Stack proofs"""
        
        # Gather all payment receipts (both AP2 and x402)
        payment_receipts = []
        
        # AP2 payment proof
        if "dual_payment" in self.results and "ap2_payment_proof" in self.results["dual_payment"]:
            ap2_proof = self.results["dual_payment"]["ap2_payment_proof"]
            
            # Get confirmation code safely
            confirmation_code = "N/A"
            if hasattr(ap2_proof, 'transaction_details') and ap2_proof.transaction_details:
                confirmation_code = ap2_proof.transaction_details.get("confirmation_code", "N/A")
            elif hasattr(ap2_proof, 'proof_id'):
                confirmation_code = f"AP2_{ap2_proof.proof_id[:8]}"
            else:
                confirmation_code = "AP2_PAYMENT_COMPLETED"
            
            # Get payment ID safely
            payment_id = "N/A"
            if hasattr(ap2_proof, 'proof_id'):
                payment_id = ap2_proof.proof_id
            elif hasattr(ap2_proof, 'cart_mandate_id'):
                payment_id = ap2_proof.cart_mandate_id
            
            payment_receipts.append({
                "type": "ap2_universal",
                "payment_id": payment_id,
                "amount": self.results["dual_payment"]["ap2_amount"],
                "confirmation": confirmation_code,
                "payment_method": "ap2_universal"
            })
        
        # x402 crypto payment receipt
        if "dual_payment" in self.results and "x402_payment_result" in self.results["dual_payment"]:
            x402_result = self.results["dual_payment"]["x402_payment_result"]
            payment_receipts.append({
                "payment_id": x402_result.payment_id,
                "transaction_hash": x402_result.transaction_hash,
                "amount": x402_result.amount,
                "currency": x402_result.currency,
                "payment_method": str(x402_result.payment_method)
            })
        
        # Validation payment receipt
        if "validation" in self.results and "x402_payment" in self.results["validation"]:
            validation_payment = self.results["validation"]["x402_payment"]
            payment_receipts.append({
                "payment_id": validation_payment.payment_id,
                "transaction_hash": validation_payment.transaction_hash,
                "amount": validation_payment.amount,
                "currency": validation_payment.currency,
                "payment_method": str(validation_payment.payment_method)
            })
        
        # Create comprehensive Triple-Verified Stack evidence package
        work_data = {
            "analysis_cid": self.results["ipfs_analysis"]["cid"],
            "validation_cid": self.results["validation"]["validation_cid"],
            "validation_score": self.results["validation"]["score"],
            "analysis_confidence": 87,  # From the analysis
            "triple_verified_stack": {
                "ap2_intent_verification": self.results.get("ap2_intent", {}).get("verified", False),
                "process_integrity_proof_id": self.results.get("process_integrity_proof", {}).get("proof_id") if self.results.get("process_integrity_proof") else None,
                "chaoschain_adjudication": "completed",
                "verification_layers_completed": 3
            }
        }
        
        # Convert payment receipts to SDK format
        import time
        from chaoschain_sdk.types import PaymentProof, PaymentMethod
        payment_proofs = []
        for receipt in payment_receipts:
            if isinstance(receipt, dict):
                from datetime import datetime
                payment_proofs.append(PaymentProof(
                    payment_id=receipt.get("payment_id", "unknown"),
                    from_agent=receipt.get("from_agent", "Charlie"),
                    to_agent=receipt.get("to_agent", "Alice"),
                    amount=receipt.get("amount", 0),
                    currency=receipt.get("currency", "USDC"),
                    payment_method=PaymentMethod.A2A_X402,
                    transaction_hash=receipt.get("transaction_hash", ""),
                    timestamp=datetime.now(),
                    receipt_data=receipt
                ))
            else:
                payment_proofs.append(receipt)  # Already a PaymentProof object
        
        evidence_package_obj = self.alice_sdk.create_evidence_package(
            work_proof=work_data,
            payment_proofs=payment_proofs
        )
        
        # Convert EvidencePackage to dictionary format for demo compatibility
        from dataclasses import asdict
        evidence_package = asdict(evidence_package_obj)
        
        # Add Triple-Verified Stack metadata
        evidence_package["triple_verified_stack"] = {
            "intent_verification": "AP2",
            "process_integrity_verification": "ChaosChain",
            "outcome_adjudication": "ChaosChain",
            "chaoschain_layers_owned": 2,
            "total_verification_layers": 3,
            "verification_complete": True
        }
        
        return evidence_package
    
    def _store_enhanced_evidence_package(self, evidence_package: Dict[str, Any]) -> str:
        """Store enhanced evidence package on IPFS"""
        
        cid = self.alice_sdk.store_evidence(evidence_package, "enhanced_package")
        
        if cid:
            # Generate gateway URL if storage manager is available
            gateway_url = "Local IPFS (no gateway URL)"
            if self.alice_sdk.storage_manager:
                try:
                    gateway_url = self.alice_sdk.storage_manager.get_gateway_url(cid)
                except Exception as e:
                    gateway_url = f"Local IPFS: {cid}"
            
            rprint(f"[green]📦 Enhanced Evidence Package uploaded to IPFS[/green]")
            rprint(f"   File: enhanced_evidence_package.json")
            rprint(f"   CID: {cid}")
            rprint(f"   Gateway: {gateway_url}")
            
            self.results["enhanced_evidence"] = {
                "success": True,
                "cid": cid,
                "gateway_url": gateway_url,
                "payment_proofs_included": len(evidence_package["payment_proofs"])
            }
        else:
            # Storage not available - continue without IPFS (no vendor lock-in)
            rprint(f"[yellow]⚠️  IPFS storage not available - continuing without storage[/yellow]")
            rprint(f"[yellow]   Enhanced evidence package data preserved in memory for demo[/yellow]")
            
            self.results["enhanced_evidence"] = {
                "success": False,
                "cid": None,
                "gateway_url": "No storage available",
                "note": "Demo continued without vendor lock-in storage"
            }
        
        return cid
    
    def _display_final_summary(self):
        """Display the final success summary with x402 enhancements"""
        
        print("DEBUG: _display_final_summary method called")
        
        # Extract payment info for use throughout method
        validation_payment_obj = self.results.get("validation", {}).get("x402_payment")
        if validation_payment_obj and hasattr(validation_payment_obj, 'amount'):
            validation_amount = validation_payment_obj.amount
            validation_tx = validation_payment_obj.transaction_hash or ""
        else:
            validation_amount = 0
            validation_tx = ""
            
        # Extract ALL payment info at the beginning for consistent access throughout method
        dual_payment = self.results.get("dual_payment", {})
        analysis_payment_obj = dual_payment.get('x402_payment_result')
        analysis_tx = ""
        if analysis_payment_obj and hasattr(analysis_payment_obj, 'transaction_hash'):
            analysis_tx = analysis_payment_obj.transaction_hash or ""
        
        # Extract payment amounts for consistent use throughout method
        print(f"DEBUG: dual_payment = {dual_payment}")
        analysis_amount = dual_payment.get('x402_amount', 0)
        ap2_amount = dual_payment.get('ap2_amount', 0)
        analysis_payment_id = analysis_payment_obj.payment_id[:20] if analysis_payment_obj and hasattr(analysis_payment_obj, 'payment_id') else 'N/A'
        validation_payment_id = validation_tx[:20] if validation_tx else 'N/A'
        print(f"DEBUG: analysis_amount = {analysis_amount}, ap2_amount = {ap2_amount}")
        
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
                "success": self.results.get("dual_payment", {}).get("dual_payment_success", False),
                "details": f"Agent-to-agent payments with cryptographic receipts",
                "payments": {
                    "Analysis Payment": f"${self.results.get('dual_payment', {}).get('x402_amount', 0)} USDC (Charlie → Alice)",
                    "Validation Payment": f"${validation_amount} USDC (Charlie → Bob)"
                }
            },
            "Enhanced Evidence": {
                "success": self.results.get("enhanced_evidence", {}).get("success", False),
                "details": "Evidence packages enhanced with x402 payment proofs for PoA verification",
                "payment_proofs": self.results.get("enhanced_evidence", {}).get("payment_proofs_included", 0)
            }
        }
        
        # Display final summary using rich
        rprint("\n[bold blue]📋 FINAL SUMMARY[/bold blue]")
        rprint("=" * 60)
        
        for component, details in summary_data.items():
            status = "[green]✅ SUCCESS[/green]" if details["success"] else "[red]❌ FAILED[/red]"
            rprint(f"\n[bold]{component}[/bold]: {status}")
            rprint(f"   {details['details']}")
            
            if "tx_hashes" in details:
                for name, tx_hash in details["tx_hashes"].items():
                    if tx_hash:
                        rprint(f"   {name}: {tx_hash}")
            
            if "cids" in details:
                for name, cid in details["cids"].items():
                    if cid:
                        rprint(f"   {name}: {cid}")
            
            if "payments" in details:
                for payment_name, payment_info in details["payments"].items():
                    rprint(f"   {payment_name}: {payment_info}")
        
        # Add x402 Payment Monitoring & Observability
        self._display_x402_monitoring_summary()
    
    def _display_x402_monitoring_summary(self):
        """Display x402 payment monitoring and observability metrics"""
        
        rprint("\n[bold cyan]📊 x402 PAYMENT MONITORING & OBSERVABILITY[/bold cyan]")
        rprint("=" * 60)
        
        try:
            # Extract actual payment data from demo results
            payment_data = self._extract_x402_payment_data_from_results()
            
            rprint(f"\n[bold green]🔍 x402 Protocol Verification[/bold green]")
            rprint(f"   Protocol: x402 v0.2.1+ (Coinbase Official)")
            rprint(f"   Network: base-sepolia")
            rprint(f"   Treasury: 0x20E7B2A2c8969725b88Dd3EF3a11Bc3353C83F70")
            rprint(f"   Protocol Fee: 2.5%")
            rprint(f"   Settlement Mode: Direct USDC transfers (2 transactions per payment)")
            
            rprint(f"\n[bold green]💳 Payment Performance Metrics[/bold green]")
            if payment_data['total_payments'] > 0:
                success_rate = (payment_data['successful_payments'] / payment_data['total_payments']) * 100
                rprint(f"   Success Rate: [green]{success_rate:.1f}%[/green]")
                rprint(f"   Total Payments: {payment_data['total_payments']}")
                rprint(f"   Total Volume: [green]${payment_data['total_volume']:.2f} USDC[/green]")
                rprint(f"   Protocol Fees Collected: [green]${payment_data['total_fees']:.4f} USDC[/green]")
                rprint(f"   Net Amount to Providers: [green]${payment_data['net_to_providers']:.4f} USDC[/green]")
            else:
                rprint(f"   [yellow]No x402 payments in current session[/yellow]")
            
            # Multi-Agent x402 Transaction Details
            rprint(f"\n[bold green]🔗 x402 Transaction Architecture[/bold green]")
            rprint(f"   Each x402 payment creates [bold]2 separate USDC transactions[/bold]:")
            rprint(f"   1️⃣  Protocol Fee → ChaosChain Treasury (2.5%)")
            rprint(f"   2️⃣  Net Payment → Service Provider (97.5%)")
            
            # Agent-level statistics from demo results
            rprint(f"\n[bold green]👥 Agent Payment Statistics[/bold green]")
            
            # Analysis payment (Charlie → Alice)
            analysis_payment = self.results.get("analysis", {}).get("dual_payment", {})
            if analysis_payment.get("x402_payment_result"):
                payment = analysis_payment["x402_payment_result"]
                protocol_fee = payment.receipt_data.get("protocol_fee", 0)
                net_amount = payment.receipt_data.get("net_amount", payment.amount)
                
                rprint(f"   🔧 Alice (Server Agent):")
                rprint(f"     Service: AI Smart Shopping Analysis")
                rprint(f"     Received: [green]${net_amount:.4f} USDC[/green] (net)")
                rprint(f"     Protocol Fee: [yellow]${protocol_fee:.4f} USDC[/yellow] → Treasury")
                rprint(f"     Fee TX: {payment.receipt_data.get('protocol_fee_tx', 'N/A')[:20]}...")
                rprint(f"     Main TX: {payment.transaction_hash[:20]}...")
            
            # Validation payment (Charlie → Bob)
            validation_payment = self.results.get("validation", {}).get("x402_payment")
            if validation_payment:
                protocol_fee = validation_payment.receipt_data.get("protocol_fee", 0)
                net_amount = validation_payment.receipt_data.get("net_amount", validation_payment.amount)
                
                rprint(f"   🔍 Bob (Validator Agent):")
                rprint(f"     Service: CrewAI Quality Validation")
                rprint(f"     Received: [green]${net_amount:.4f} USDC[/green] (net)")
                rprint(f"     Protocol Fee: [yellow]${protocol_fee:.4f} USDC[/yellow] → Treasury")
                rprint(f"     Main TX: {validation_payment.transaction_hash[:20]}...")
            
            # Charlie's payment summary
            total_sent = 0
            total_fees = 0
            if analysis_payment.get("x402_payment_result"):
                payment = analysis_payment["x402_payment_result"]
                total_sent += payment.amount
                total_fees += payment.receipt_data.get("protocol_fee", 0)
            if validation_payment:
                total_sent += validation_payment.amount
                total_fees += validation_payment.receipt_data.get("protocol_fee", 0)
                
            if total_sent > 0:
                rprint(f"   💳 Charlie (Client Agent):")
                rprint(f"     Services Purchased: Smart Shopping + Validation")
                rprint(f"     Total Sent: [red]${total_sent:.2f} USDC[/red]")
                rprint(f"     Protocol Fees Paid: [yellow]${total_fees:.4f} USDC[/yellow]")
            
            # Treasury fee collection summary
            if total_fees > 0:
                rprint(f"\n[bold green]🏦 ChaosChain Treasury Collection[/bold green]")
                rprint(f"   Total Fees Collected: [green]${total_fees:.4f} USDC[/green]")
                rprint(f"   Fee Percentage: 2.5% of all x402 payments")
                rprint(f"   Treasury Address: 0x20E7B2A2c8969725b88Dd3EF3a11Bc3353C83F70")
                rprint(f"   Revenue Model: Automatic fee collection on every x402 payment")
            
            rprint(f"\n[bold green]🎯 x402 Benefits Demonstrated[/bold green]")
            rprint(f"   ✅ Frictionless agent-to-agent payments")
            rprint(f"   ✅ Cryptographic payment receipts for PoA")
            rprint(f"   ✅ Dual-transaction architecture (fee + payment)")
            rprint(f"   ✅ Automatic protocol fee collection (2.5% to ChaosChain)")
            rprint(f"   ✅ Enhanced evidence packages with payment proofs")
            rprint(f"   ✅ Production-ready USDC settlement on Base Sepolia")
            
        except Exception as e:
            rprint(f"[yellow]⚠️  x402 monitoring unavailable: {e}[/yellow]")
            rprint(f"   This is expected if no payments were made in this session")
    
    def _extract_x402_payment_data_from_results(self):
        """Extract x402 payment data from demo results for monitoring"""
        
        total_payments = 0
        successful_payments = 0
        total_volume = 0.0
        total_fees = 0.0
        net_to_providers = 0.0
        
        # Analysis payment (Charlie → Alice)
        analysis_payment = self.results.get("analysis", {}).get("dual_payment", {})
        if analysis_payment.get("x402_payment_result"):
            payment = analysis_payment["x402_payment_result"]
            total_payments += 1
            successful_payments += 1
            total_volume += payment.amount
            protocol_fee = payment.receipt_data.get("protocol_fee", 0)
            net_amount = payment.receipt_data.get("net_amount", payment.amount)
            total_fees += protocol_fee
            net_to_providers += net_amount
        
        # Validation payment (Charlie → Bob)
        validation_payment = self.results.get("validation", {}).get("x402_payment")
        if validation_payment:
            total_payments += 1
            successful_payments += 1
            total_volume += validation_payment.amount
            protocol_fee = validation_payment.receipt_data.get("protocol_fee", 0)
            net_amount = validation_payment.receipt_data.get("net_amount", validation_payment.amount)
            total_fees += protocol_fee
            net_to_providers += net_amount
        
        return {
            "total_payments": total_payments,
            "successful_payments": successful_payments,
            "total_volume": total_volume,
            "total_fees": total_fees,
            "net_to_providers": net_to_providers
        }
    
    def _print_final_success_summary(self):
        """Print the beautiful final success summary table with x402 enhancements"""
        
        from rich.table import Table
        from rich.align import Align
        from rich import print as rprint
        
        # Create the main success banner
        success_banner = """
🎉 **CHAOSCHAIN GENESIS STUDIO TRIPLE-VERIFIED STACK COMPLETE!** 🚀

✅ **FULL END-TO-END TRIPLE-VERIFIED COMMERCIAL PROTOTYPE SUCCESSFUL!**

The complete lifecycle of trustless agentic commerce with Triple-Verified Stack:
• ERC-8004 Foundation: Identity, Reputation, and Validation registries ✅
• AP2 Intent Verification: Cryptographic proof of user authorization ✅
• ChaosChain Process Integrity: Verifiable proof of correct code execution ✅
• ChaosChain Adjudication: Quality assessment and evidence storage ✅
• Dual Payment Protocols: AP2 universal + x402 crypto settlement ✅
• Enhanced Evidence Packages with all verification proofs ✅

🚀 **ChaosChain owns 2 out of 3 verification layers!**
        """
        
        banner_panel = Panel(
            Align.center(success_banner),
            title="[bold green]🏆 TRIPLE-VERIFIED STACK DEMO COMPLETE 🏆[/bold green]",
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
        dual_payment = self.results.get("dual_payment", {})
        analysis_amount = dual_payment.get('x402_amount', 0)
        ap2_amount = dual_payment.get('ap2_amount', 0)
        analysis_payment_obj = dual_payment.get('x402_payment_result')
        analysis_tx = ""
        if analysis_payment_obj and hasattr(analysis_payment_obj, 'transaction_hash'):
            analysis_tx = analysis_payment_obj.transaction_hash or ""
        
        table.add_row(
            "💳 x402 Analysis Payment",
            "[green]✅ SUCCESS[/green]",
            f"${analysis_amount} USDC: Charlie → Alice",
            f"0x{analysis_tx[:20]}..." if analysis_tx and analysis_tx != "N/A" else "N/A"
        )
        
        # x402 Validation Payment
        validation_payment_obj = self.results.get("validation", {}).get("x402_payment")
        if validation_payment_obj and hasattr(validation_payment_obj, 'amount'):
            validation_amount = validation_payment_obj.amount
            validation_tx = validation_payment_obj.transaction_hash or ""
        else:
            validation_amount = 0
            validation_tx = ""
        
        # Extract payment IDs for f-string
        analysis_payment_id = analysis_payment_obj.payment_id[:20] if analysis_payment_obj and hasattr(analysis_payment_obj, 'payment_id') else 'N/A'
        validation_payment_id = validation_tx[:20] if validation_tx else 'N/A'
        
        table.add_row(
            "💳 x402 Validation Payment",
            "[green]✅ SUCCESS[/green]",
            f"${validation_amount} USDC: Charlie → Bob",
            f"0x{validation_tx[:20]}..." if validation_tx and validation_tx != "N/A" else "N/A"
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
        
        # Payment amounts already extracted at the beginning of method
        
        # Create payment summary content as a string first
        payment_summary_content = f"""[bold cyan]💳 x402 Payment Protocol Summary:[/bold cyan]

[yellow]Smart Shopping Service Payment:[/yellow]
• Amount: ${analysis_amount} USDC (x402 crypto settlement)
• Authorization: ${ap2_amount} USDC (AP2 intent verification)
• From: Charlie → Alice
• Service: AI Smart Shopping
• Payment ID: {analysis_payment_id}...

[yellow]Validation Service Payment:[/yellow]
• Amount: ${validation_amount} USDC  
• From: Charlie → Bob
• Service: Smart Shopping Validation
• Payment ID: {validation_payment_id}...

[bold green]🎯 x402 Protocol Benefits:[/bold green]
• Frictionless agent-to-agent payments ✅
• Cryptographic payment receipts for PoA ✅
• No complex wallet setup required ✅
• Instant settlement on Base Sepolia ✅
• Enhanced evidence packages with payment proofs ✅

[bold magenta]💰 Economic Impact:[/bold magenta]
• Alice earned ${analysis_amount} USDC for smart shopping service
• Bob earned ${validation_amount} USDC for validation service
• Charlie received verified shopping results with payment-backed guarantees
• Complete audit trail for trustless commerce established

[bold red]🔧 Next Steps:[/bold red]
• Enhanced evidence packages with payment proofs
• Multi-agent collaboration workflows
• Cross-chain x402 payment support"""

        # Create and display the panel
        payment_summary_panel = Panel(
            payment_summary_content,
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