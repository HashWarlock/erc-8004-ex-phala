"""TEE Verification and Registration"""

from typing import Dict, Any
from web3 import Web3
from eth_account import Account


class TEEVerifier:
    def __init__(self, w3: Web3, tee_registry_address: str, account: Account, verifier_address: str):
        self.w3 = w3
        self.registry_address = Web3.to_checksum_address(tee_registry_address)
        self.account = account
        self.verifier_address = Web3.to_checksum_address(verifier_address)

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
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "agentId", "type": "uint256"}, {"name": "pubkey", "type": "address"}],
                "name": "hasKey",
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]

        self.registry_contract = w3.eth.contract(
            address=self.registry_address,
            abi=self.registry_abi
        )

    async def check_tee_registered(self, agent_id: int, pubkey_address: str) -> bool:
        """Check if TEE key already registered."""
        return self.registry_contract.functions.hasKey(agent_id, Web3.to_checksum_address(pubkey_address)).call()

    async def register_tee_key(
        self,
        agent_id: int,
        agent_address: str,
        mock_mode: bool = True
    ) -> Dict[str, Any]:
        """Register TEE key with mock proof."""

        # Mock proof data
        tee_arch = Web3.to_bytes(text="TDX_DSTACK").ljust(32, b'\x00')
        code_measurement = bytes.fromhex("d641ca7589adba8fcd079f923ebccee92195cb998cfdf8dcc500585bfdb06df6")
        pubkey = Web3.to_checksum_address(agent_address)
        code_config_uri = "ipfs://QmAAAAAAAAAAAAAAAAAAAAAAAAAAAz"
        proof = bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000012000000000000000000000000000000000000000000000000000000000000000c0d641ca7589adba8fcd079f923ebccee92195cb998cfdf8dcc500585bfdb06df600000000000000000000000070997970c51812dc3a010c7d01b50e0d17dc79c800000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000025697066733a2f2f516d4141414141414141414141414141414141414141414141414141417a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000041e5a94c9e2b74b70f25ac7ab88263a44543faf643034aa02f711fe60be1c826f6435ca3245f660192fc6c0a8483a21eeedccd8a3f66202121e23d79060cb7c62a1c00000000000000000000000000000000000000000000000000000000000000")

        # Check if already registered
        if await self.check_tee_registered(agent_id, pubkey):
            return {"success": True, "agent_id": agent_id, "pubkey": pubkey, "already_registered": True}

        tx = self.registry_contract.functions.addKey(
            agent_id,
            tee_arch,
            code_measurement,
            pubkey,
            code_config_uri,
            self.verifier_address,
            proof
        ).build_transaction({
            'chainId': self.w3.eth.chain_id,
            'gas': 500000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address)
        })

        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        print(f"📤 TEE tx: {tx_hash.hex()}")

        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status != 1:
            raise RuntimeError(f"TEE registration failed: tx={tx_hash.hex()}")

        return {
            "success": True,
            "tx_hash": tx_hash.hex(),
            "agent_id": agent_id,
            "pubkey": pubkey,
            "code_measurement": "0x" + code_measurement.hex()
        }
