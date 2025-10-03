"""TEE Verification and Registration"""

import hashlib
from typing import Dict, Any
from web3 import Web3
from eth_account import Account


class TEEVerifier:
    def __init__(self, w3: Web3, tee_registry_address: str, account: Account, verifier_address: str = None):
        self.w3 = w3
        self.tee_registry_address = tee_registry_address
        self.account = account
        self.verifier_address = verifier_address or account.address

        # TEE Registry ABI
        self.registry_abi = [
            {
                "inputs": [
                    {"name": "agentId", "type": "uint256"},
                    {"name": "teeArch", "type": "bytes32"},
                    {"name": "codeMeasurement", "type": "bytes32"},
                    {"name": "pubkey", "type": "address"},
                    {"name": "codeConfigUri", "type": "string"},
                    {"name": "verifier", "type": "address"},
                    {"name": "proof", "type": "bytes"}
                ],
                "name": "addKey",
                "outputs": [],
                "type": "function",
                "stateMutability": "nonpayable"
            },
            {
                "inputs": [{"name": "agentId", "type": "uint256"}, {"name": "pubkey", "type": "address"}],
                "name": "hasKey",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function",
                "stateMutability": "view"
            }
        ]

        self.registry_contract = w3.eth.contract(
            address=Web3.to_checksum_address(tee_registry_address),
            abi=self.registry_abi
        )

    def pubkey_to_address(self, pubkey: bytes) -> str:
        """Convert secp256k1 pubkey to Ethereum address."""
        if len(pubkey) == 64:
            pubkey = b'\x04' + pubkey
        pubkey_hash = Web3.keccak(pubkey[1:])
        return Web3.to_checksum_address('0x' + pubkey_hash[-20:].hex())

    async def register_tee_key(
        self,
        agent_id: int,
        tee_arch: str,
        pubkey: bytes,
        attestation: bytes,
        code_config_uri: str = ""
    ) -> Dict[str, Any]:
        """Register TEE key on-chain."""

        # Convert teeArch to bytes32
        tee_arch_bytes = Web3.to_bytes(text=tee_arch).ljust(32, b'\x00')

        # Compute code measurement from attestation
        code_measurement = hashlib.sha256(attestation[:100]).digest()

        # Convert pubkey to address
        pubkey_address = self.pubkey_to_address(pubkey)

        # Build transaction
        tx = self.registry_contract.functions.addKey(
            agent_id,
            tee_arch_bytes,
            code_measurement,
            pubkey_address,
            code_config_uri,
            Web3.to_checksum_address(self.verifier_address),
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

        return {
            "tx_hash": tx_hash.hex(),
            "code_measurement": "0x" + code_measurement.hex(),
            "tee_arch": tee_arch,
            "pubkey_address": pubkey_address,
            "verified": True
        }
