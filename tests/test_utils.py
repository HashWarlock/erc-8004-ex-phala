"""
Test utilities for simulator-based testing

This module provides utilities to ensure tests run against real simulators
rather than using mock data.
"""

import os
import sys
import time
import requests
import subprocess
from typing import Optional, Tuple
from web3 import Web3


class SimulatorManager:
    """Manages simulator instances for testing"""

    def __init__(self):
        self.anvil_process: Optional[subprocess.Popen] = None
        self.tee_process: Optional[subprocess.Popen] = None
        self.anvil_url = "http://127.0.0.1:8545"
        self.tee_socket = os.getenv(
            "DSTACK_SIMULATOR_ENDPOINT", ".dstack/sdk/simulator/dstack.sock"
        )

    def check_anvil_running(self) -> bool:
        """Check if Anvil blockchain is running"""
        try:
            w3 = Web3(Web3.HTTPProvider(self.anvil_url))
            return w3.is_connected()
        except:
            return False

    def check_tee_running(self) -> bool:
        """Check if TEE simulator is running"""
        # Check if socket exists
        if os.path.exists(self.tee_socket):
            return True

        # Alternative: Check HTTP endpoint if available
        tee_http = os.getenv("TEE_SIMULATOR_HTTP", "http://localhost:8080")
        try:
            response = requests.get(f"{tee_http}/health", timeout=1)
            return response.status_code == 200
        except:
            return False

    def start_anvil(self, auto_mine: bool = True) -> bool:
        """Start Anvil if not running"""
        if self.check_anvil_running():
            print("✅ Anvil already running")
            return True

        print("🚀 Starting Anvil...")
        cmd = ["anvil", "--host", "0.0.0.0", "--chain-id", "31337"]
        if auto_mine:
            cmd.append("--block-time")
            cmd.append("1")

        try:
            self.anvil_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            # Wait for Anvil to start
            for _ in range(10):
                time.sleep(1)
                if self.check_anvil_running():
                    print("✅ Anvil started successfully")
                    return True

            print("❌ Anvil failed to start")
            return False
        except FileNotFoundError:
            print("❌ Anvil not found. Please install Foundry.")
            return False

    def start_tee_simulator(self) -> bool:
        """Start TEE simulator if not running"""
        if self.check_tee_running():
            print("✅ TEE simulator already running")
            return True

        print("🚀 Starting TEE simulator...")
        try:
            # Try to start dstack simulator
            self.tee_process = subprocess.Popen(
                ["make", "tee-start"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            )

            # Wait for TEE simulator to start
            for _ in range(10):
                time.sleep(1)
                if self.check_tee_running():
                    print("✅ TEE simulator started successfully")
                    return True

            print("⚠️  TEE simulator not available (non-critical for basic tests)")
            return False
        except:
            print("⚠️  Could not start TEE simulator (non-critical for basic tests)")
            return False

    def ensure_simulators_running(self, require_tee: bool = False) -> Tuple[bool, str]:
        """
        Ensure required simulators are running

        Args:
            require_tee: Whether TEE simulator is required

        Returns:
            Tuple of (success, error_message)
        """
        # Check/start Anvil (always required)
        if not self.check_anvil_running():
            if not self.start_anvil():
                return False, "Anvil blockchain is not running. Please run 'make chain-start'"

        # Check/start TEE if required
        if require_tee:
            if not self.check_tee_running():
                if not self.start_tee_simulator():
                    return (
                        False,
                        "TEE simulator is not running. Please run 'make tee-start'",
                    )

        return True, ""

    def deploy_contracts(self) -> bool:
        """Deploy contracts to Anvil"""
        print("📝 Deploying contracts...")
        try:
            result = subprocess.run(
                ["make", "deploy"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            )
            if result.returncode == 0:
                print("✅ Contracts deployed successfully")
                return True
            else:
                print(f"❌ Contract deployment failed: {result.stderr}")
                return False
        except:
            print("❌ Could not deploy contracts")
            return False

    def cleanup(self):
        """Stop simulators if we started them"""
        if self.anvil_process:
            print("🛑 Stopping Anvil...")
            self.anvil_process.terminate()
            self.anvil_process.wait()

        if self.tee_process:
            print("🛑 Stopping TEE simulator...")
            self.tee_process.terminate()
            self.tee_process.wait()


def require_simulators(require_tee: bool = False):
    """
    Pytest fixture decorator to ensure simulators are running

    Usage:
        @require_simulators()
        def test_something():
            # Test code here

        @require_simulators(require_tee=True)
        def test_with_tee():
            # Test code here
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            manager = SimulatorManager()
            success, error = manager.ensure_simulators_running(require_tee)
            if not success:
                pytest.skip(error)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_test_web3() -> Web3:
    """Get Web3 instance connected to test blockchain"""
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    if not w3.is_connected():
        raise ConnectionError(
            "Cannot connect to Anvil. Please ensure it's running with 'make chain-start'"
        )
    return w3


def get_test_tee_client():
    """Get TEE client connected to simulator"""
    from dstack_sdk import DstackClient

    endpoint = os.getenv(
        "DSTACK_SIMULATOR_ENDPOINT", ".dstack/sdk/simulator/dstack.sock"
    )

    if not os.path.exists(endpoint):
        raise ConnectionError(
            f"TEE simulator not running. Please run 'make tee-start'"
        )

    return DstackClient(endpoint=endpoint)


def fund_account(w3: Web3, address: str, amount_ether: float = 10):
    """Fund an account using Anvil's default funded account"""
    # Anvil's first default account with funds
    funded_account = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    funded_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

    # Send funds
    tx = {
        "from": funded_account,
        "to": address,
        "value": w3.to_wei(amount_ether, "ether"),
        "gas": 21000,
        "gasPrice": w3.eth.gas_price,
        "nonce": w3.eth.get_transaction_count(funded_account),
    }

    signed = w3.eth.account.sign_transaction(tx, funded_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)

    return tx_hash


# Pytest plugin to ensure simulators are running before tests
def pytest_configure(config):
    """Configure pytest to check simulators before running tests"""
    if not hasattr(config, "workerinput"):  # Only on main process
        manager = SimulatorManager()

        # Check if we're running tests that need simulators
        if any(
            arg.startswith("tests/")
            for arg in config.invocation_params.args
            if "unit" not in arg
        ):
            print("\n" + "=" * 60)
            print("🔍 Checking test environment...")

            # Check Anvil
            if not manager.check_anvil_running():
                print(
                    "⚠️  Anvil not running. Start it with 'make chain-start' or tests will be skipped"
                )

            # Check TEE (optional)
            if not manager.check_tee_running():
                print(
                    "⚠️  TEE simulator not running. Start it with 'make tee-start' for full test coverage"
                )

            print("=" * 60 + "\n")