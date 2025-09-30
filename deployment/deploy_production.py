#!/usr/bin/env python3
"""
Production Deployment Script for Base Sepolia

Handles full agent deployment lifecycle:
1. Check TEE environment
2. Derive agent address
3. Check funding status
4. Register on-chain
5. Verify registration
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.agent.base import AgentConfig, AgentRole, RegistryAddresses, create_agent
from src.agent.tee_auth import TEEAuthenticator


class ProductionDeployer:
    """Handles production agent deployment to Base Sepolia."""

    def __init__(self, env_file: str = ".env.production"):
        """Initialize deployer with environment configuration."""
        self.env_file = env_file
        load_dotenv(env_file)

        self.deployment_id = f"deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.deployment_log = []

    def log(self, message: str, level: str = "INFO"):
        """Log deployment message."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.deployment_log.append(log_entry)
        print(log_entry)

    async def check_tee_environment(self) -> bool:
        """Verify TEE environment is ready."""
        self.log("=" * 80)
        self.log("STEP 1: Checking TEE Environment")
        self.log("=" * 80)

        try:
            # Check socket exists
            socket_path = "/var/run/dstack.sock"
            if not os.path.exists(socket_path):
                self.log(f"TEE socket not found at {socket_path}", "ERROR")
                return False

            self.log(f"✓ TEE socket found: {socket_path}")

            # Test key derivation
            test_auth = TEEAuthenticator(
                domain="test.example.com",
                salt="test-check",
                use_tee=True
            )

            test_addr = await test_auth.derive_address()
            self.log(f"✓ TEE key derivation working: {test_addr}")

            return True

        except Exception as e:
            self.log(f"TEE environment check failed: {e}", "ERROR")
            return False

    def load_configuration(self) -> tuple[AgentConfig, RegistryAddresses]:
        """Load agent configuration from environment."""
        self.log("\n" + "=" * 80)
        self.log("STEP 2: Loading Configuration")
        self.log("=" * 80)

        # Get agent domain
        dstack_app_id = os.getenv("DSTACK_APP_ID", "")
        dstack_gateway = os.getenv("DSTACK_GATEWAY_DOMAIN", "phala.network")
        agent_domain = f"https://{dstack_app_id}.{dstack_gateway}" if dstack_app_id else "agent.phala.network"

        # Get agent configuration
        agent_type_str = os.getenv("AGENT_TYPE", "server").lower()
        agent_role = getattr(AgentRole, agent_type_str.upper(), AgentRole.SERVER)

        config = AgentConfig(
            domain=agent_domain,
            salt=os.getenv("AGENT_SALT", "default-salt-change-this"),
            role=agent_role,
            rpc_url=os.getenv("RPC_URL", "https://sepolia.base.org"),
            chain_id=int(os.getenv("CHAIN_ID", "84532")),
            use_tee_auth=os.getenv("USE_TEE_AUTH", "true").lower() == "true",
            tee_endpoint=os.getenv("DSTACK_SIMULATOR_ENDPOINT")
        )

        registries = RegistryAddresses(
            identity=os.getenv("IDENTITY_REGISTRY_ADDRESS"),
            reputation=os.getenv("REPUTATION_REGISTRY_ADDRESS"),
            validation=os.getenv("VALIDATION_REGISTRY_ADDRESS"),
            tee_verifier=os.getenv("TEE_VERIFIER_ADDRESS")
        )

        self.log(f"✓ Domain: {config.domain}")
        self.log(f"✓ Salt: {config.salt[:20]}...")
        self.log(f"✓ Role: {config.role.value}")
        self.log(f"✓ Chain: Base Sepolia ({config.chain_id})")
        self.log(f"✓ RPC: {config.rpc_url}")
        self.log(f"✓ TEE Mode: {config.use_tee_auth}")

        return config, registries

    async def derive_agent_address(self, config: AgentConfig) -> str:
        """Derive TEE-secured agent address."""
        self.log("\n" + "=" * 80)
        self.log("STEP 3: Deriving Agent Address from TEE")
        self.log("=" * 80)

        auth = TEEAuthenticator(
            domain=config.domain,
            salt=config.salt,
            use_tee=config.use_tee_auth,
            tee_endpoint=config.tee_endpoint
        )

        address = await auth.derive_address()
        self.log(f"✓ Agent Address: {address}")
        self.log(f"  (Derived from domain + salt via TEE)")

        return address

    async def check_funding(self, config: AgentConfig, address: str) -> Dict[str, Any]:
        """Check if agent address has sufficient funding."""
        self.log("\n" + "=" * 80)
        self.log("STEP 4: Checking Funding Status")
        self.log("=" * 80)

        from web3 import Web3

        w3 = Web3(Web3.HTTPProvider(config.rpc_url))

        if not w3.is_connected():
            self.log(f"Failed to connect to RPC: {config.rpc_url}", "ERROR")
            return {"funded": False, "balance": 0, "error": "RPC connection failed"}

        balance_wei = w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance_wei, 'ether')

        # Estimate gas needed (rough estimate)
        gas_price = w3.eth.gas_price
        estimated_gas = 500000  # Registration gas limit
        estimated_cost_wei = gas_price * estimated_gas
        estimated_cost_eth = w3.from_wei(estimated_cost_wei, 'ether')

        funded = balance_wei > estimated_cost_wei

        self.log(f"  Balance: {balance_eth} ETH")
        self.log(f"  Estimated Cost: {estimated_cost_eth} ETH")
        self.log(f"  Gas Price: {w3.from_wei(gas_price, 'gwei')} gwei")

        if funded:
            self.log(f"✓ Address is funded")
        else:
            self.log(f"✗ Address needs funding", "WARNING")
            self.log(f"  Send at least {estimated_cost_eth} ETH to: {address}", "WARNING")
            self.log(f"  Get testnet ETH: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet", "WARNING")

        return {
            "funded": funded,
            "balance": balance_eth,
            "balance_wei": balance_wei,
            "estimated_cost": estimated_cost_eth,
            "estimated_cost_wei": estimated_cost_wei,
            "address": address
        }

    async def register_agent(
        self,
        config: AgentConfig,
        registries: RegistryAddresses,
        funding_info: Dict[str, Any]
    ) -> Optional[int]:
        """Register agent on Base Sepolia."""
        self.log("\n" + "=" * 80)
        self.log("STEP 5: Registering Agent On-Chain")
        self.log("=" * 80)

        if not funding_info["funded"]:
            self.log("Skipping registration - address not funded", "WARNING")
            return None

        try:
            # Create agent
            agent = create_agent(
                config.role.value,
                config,
                registries
            )

            self.log(f"  Creating {config.role.value} agent...")

            # Register
            self.log(f"  Submitting registration transaction...")
            self.log(f"  (This may take 30-60 seconds)")

            agent_id = await agent.register()

            self.log(f"✓ Agent registered successfully!")
            self.log(f"  Agent ID: {agent_id}")

            return agent_id

        except Exception as e:
            self.log(f"Registration failed: {e}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")
            return None

    async def verify_registration(
        self,
        config: AgentConfig,
        registries: RegistryAddresses,
        agent_id: int
    ) -> bool:
        """Verify agent registration on-chain."""
        self.log("\n" + "=" * 80)
        self.log("STEP 6: Verifying Registration")
        self.log("=" * 80)

        try:
            agent = create_agent(
                config.role.value,
                config,
                registries
            )

            agent.agent_id = agent_id
            info = await agent.get_agent_info()

            self.log(f"✓ Agent verified on-chain")
            self.log(f"  Domain: {info.get('domain')}")
            self.log(f"  Address: {info.get('address')}")
            self.log(f"  Active: {info.get('isActive')}")

            return True

        except Exception as e:
            self.log(f"Verification failed: {e}", "ERROR")
            return False

    async def generate_attestation(
        self,
        config: AgentConfig,
        registries: RegistryAddresses
    ) -> Optional[Dict[str, Any]]:
        """Generate TEE attestation."""
        self.log("\n" + "=" * 80)
        self.log("STEP 7: Generating TEE Attestation")
        self.log("=" * 80)

        try:
            agent = create_agent(
                config.role.value,
                config,
                registries
            )

            attestation = await agent.get_attestation()

            if "error" in attestation:
                self.log(f"Attestation error: {attestation['error']}", "WARNING")
                return None

            self.log(f"✓ Attestation generated")
            self.log(f"  Quote size: {len(attestation.get('quote', b''))} bytes")
            self.log(f"  App data: {attestation['application_data']['size']} bytes")

            return attestation

        except Exception as e:
            self.log(f"Attestation generation failed: {e}", "ERROR")
            return None

    def save_deployment_report(
        self,
        config: AgentConfig,
        address: str,
        funding_info: Dict[str, Any],
        agent_id: Optional[int],
        attestation: Optional[Dict[str, Any]]
    ):
        """Save deployment report."""
        report = {
            "deployment_id": self.deployment_id,
            "timestamp": datetime.now().isoformat(),
            "config": {
                "domain": config.domain,
                "salt": config.salt,
                "role": config.role.value,
                "chain_id": config.chain_id,
                "tee_enabled": config.use_tee_auth
            },
            "address": address,
            "funding": {
                "funded": funding_info["funded"],
                "balance_eth": str(funding_info["balance"])
            },
            "registration": {
                "agent_id": agent_id,
                "success": agent_id is not None
            },
            "attestation": {
                "generated": attestation is not None,
                "size": len(attestation.get('quote', b'')) if attestation else 0
            },
            "logs": self.deployment_log
        }

        report_file = f"deployment/reports/{self.deployment_id}.json"
        os.makedirs("deployment/reports", exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        self.log(f"\nDeployment report saved: {report_file}")

        return report

    async def deploy(self) -> Dict[str, Any]:
        """Execute full deployment workflow."""
        self.log(f"\n{'='*80}")
        self.log(f"ERC-8004 AGENT PRODUCTION DEPLOYMENT")
        self.log(f"Base Sepolia - {self.deployment_id}")
        self.log(f"{'='*80}\n")

        # Step 1: Check TEE
        if not await self.check_tee_environment():
            self.log("\nDeployment failed: TEE environment not ready", "ERROR")
            return {"success": False, "error": "TEE environment check failed"}

        # Step 2: Load config
        config, registries = self.load_configuration()

        # Step 3: Derive address
        address = await self.derive_agent_address(config)

        # Step 4: Check funding
        funding_info = await self.check_funding(config, address)

        # Step 5: Register (if funded)
        agent_id = None
        if funding_info["funded"]:
            agent_id = await self.register_agent(config, registries, funding_info)

        # Step 6: Verify (if registered)
        if agent_id:
            await self.verify_registration(config, registries, agent_id)

        # Step 7: Generate attestation
        attestation = await self.generate_attestation(config, registries)

        # Save report
        report = self.save_deployment_report(
            config,
            address,
            funding_info,
            agent_id,
            attestation
        )

        # Final summary
        self.log("\n" + "=" * 80)
        self.log("DEPLOYMENT SUMMARY")
        self.log("=" * 80)
        self.log(f"Agent Address: {address}")
        self.log(f"Funded: {'✓' if funding_info['funded'] else '✗'}")
        self.log(f"Registered: {'✓' if agent_id else '✗'} {f'(ID: {agent_id})' if agent_id else ''}")
        self.log(f"Attestation: {'✓' if attestation else '✗'}")
        self.log("=" * 80)

        if not funding_info["funded"]:
            self.log("\n⚠️  ACTION REQUIRED:")
            self.log(f"   Send ETH to: {address}")
            self.log(f"   Amount: At least {funding_info['estimated_cost']} ETH")
            self.log(f"   Faucet: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet")
            self.log(f"   Then run this script again to register.")

        if agent_id:
            self.log("\n✅ DEPLOYMENT SUCCESSFUL!")
            self.log(f"   Your agent is live on Base Sepolia")
            self.log(f"   Agent ID: {agent_id}")

        return report


async def main():
    """Main entry point."""
    deployer = ProductionDeployer()
    report = await deployer.deploy()

    return report


if __name__ == "__main__":
    asyncio.run(main())