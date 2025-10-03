"""TEE Verification and Registration"""

import hashlib
from typing import Dict, Any
from web3 import Web3
from eth_account import Account


class TEEVerifier:
    def __init__(self, w3: Web3, verifier_address: str, tee_registry_address: str, account: Account):
        self.w3 = w3
        self.verifier_address = verifier_address
        self.tee_registry_address = tee_registry_address
        self.account = account

        # Mock verifier ABI
        self.verifier_abi = [{
            "inputs": [
                {"name": "agentId", "type": "uint256"},
                {"name": "teeArch", "type": "string"},
                {"name": "codeMeasurement", "type": "bytes32"},
                {"name": "pubkey", "type": "bytes"},
                {"name": "attestation", "type": "bytes"}
            ],
            "name": "verifyAndRegister",
            "outputs": [{"name": "", "type": "uint256"}],
            "type": "function",
            "stateMutability": "nonpayable"
        }]

        self.verifier_contract = w3.eth.contract(
            address=Web3.to_checksum_address(verifier_address),
            abi=self.verifier_abi
        )

    def compute_code_measurement(self, code_hash: str) -> bytes:
        """Compute code measurement from source hash."""
        return bytes.fromhex(code_hash[2:]) if code_hash.startswith('0x') else bytes.fromhex(code_hash)

    async def register_tee_key(
        self,
        agent_id: int,
        tee_arch: str,
        pubkey: bytes,
        attestation: bytes
    ) -> Dict[str, Any]:
        """Register TEE key on-chain."""

        # Compute code measurement (mock: use attestation hash)
        code_measurement = hashlib.sha256(attestation[:100]).digest()

        # Build transaction
        tx = self.verifier_contract.functions.verifyAndRegister(
            agent_id,
            tee_arch,
            code_measurement,
            pubkey,
            attestation
        ).build_transaction({
            'chainId': self.w3.eth.chain_id,
            'gas': 500000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address)
        })

        # Sign and send
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        print(f"📤 TEE registration tx: {tx_hash.hex()}")

        # Wait for receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status != 1:
            raise RuntimeError(f"TEE registration failed: {receipt}")

        # Extract key ID from logs
        key_id = int.from_bytes(receipt['logs'][0]['topics'][1], 'big') if receipt['logs'] else 0

        return {
            "key_id": key_id,
            "tx_hash": tx_hash.hex(),
            "code_measurement": "0x" + code_measurement.hex(),
            "tee_arch": tee_arch,
            "verified": True
        }
