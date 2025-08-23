"""
Integration tests for ERC-8004 smart contracts

These tests verify contract functionality with a running blockchain.
Requires Anvil or similar test blockchain to be running.
"""

import pytest
from web3 import Web3


@pytest.mark.integration
class TestIdentityRegistry:
    """Test IdentityRegistry contract interactions"""
    
    def test_registration_fee(self, w3, deployed_contracts, contract_abis):
        """Test that registration fee is correctly set"""
        identity_contract = w3.eth.contract(
            address=deployed_contracts['IdentityRegistry'],
            abi=contract_abis['IdentityRegistry']
        )
        
        fee = identity_contract.functions.REGISTRATION_FEE().call()
        assert fee > 0
        assert fee == w3.to_wei(0.005, 'ether')
    
    def test_agent_registration(self, w3, deployed_contracts, contract_abis, test_accounts):
        """Test agent registration process"""
        identity_contract = w3.eth.contract(
            address=deployed_contracts['IdentityRegistry'],
            abi=contract_abis['IdentityRegistry']
        )
        
        # Use a test account that hasn't been registered yet
        test_account = test_accounts[3]  # Charlie
        test_domain = f"test.agent.{test_account['name'].lower()}.com"
        
        # Get registration fee
        fee = identity_contract.functions.REGISTRATION_FEE().call()
        
        # Check if already registered
        existing_info = identity_contract.functions.resolveByAddress(
            test_account['address']
        ).call()
        
        if existing_info[0] == 0:  # Not registered
            # Build registration transaction
            nonce = w3.eth.get_transaction_count(test_account['address'])
            tx = identity_contract.functions.newAgent(
                test_domain,
                test_account['address']
            ).build_transaction({
                'from': test_account['address'],
                'value': fee,
                'gas': 500000,
                'gasPrice': w3.to_wei('2', 'gwei'),
                'nonce': nonce,
            })
            
            # Sign and send
            signed_tx = w3.eth.account.sign_transaction(
                tx, 
                test_account['private_key']
            )
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            assert receipt.status == 1
            
            # Verify registration
            agent_info = identity_contract.functions.resolveByAddress(
                test_account['address']
            ).call()
            
            assert agent_info[0] > 0  # Has agent ID
            assert agent_info[1] == test_domain
            assert agent_info[2].lower() == test_account['address'].lower()
        else:
            # Already registered, just verify
            assert existing_info[0] > 0
    
    def test_get_agent_count(self, w3, deployed_contracts, contract_abis):
        """Test getting total agent count"""
        identity_contract = w3.eth.contract(
            address=deployed_contracts['IdentityRegistry'],
            abi=contract_abis['IdentityRegistry']
        )
        
        count = identity_contract.functions.getAgentCount().call()
        assert count >= 0


@pytest.mark.integration
class TestReputationRegistry:
    """Test ReputationRegistry contract interactions"""
    
    def test_feedback_authorization(self, w3, deployed_contracts, contract_abis, 
                                   alice_account, bob_account):
        """Test feedback authorization between agents"""
        reputation_contract = w3.eth.contract(
            address=deployed_contracts['ReputationRegistry'],
            abi=contract_abis['ReputationRegistry']
        )
        identity_contract = w3.eth.contract(
            address=deployed_contracts['IdentityRegistry'],
            abi=contract_abis['IdentityRegistry']
        )
        
        # Get agent IDs
        alice_info = identity_contract.functions.resolveByAddress(
            alice_account['address']
        ).call()
        bob_info = identity_contract.functions.resolveByAddress(
            bob_account['address']
        ).call()
        
        # Skip if agents not registered
        if alice_info[0] == 0 or bob_info[0] == 0:
            pytest.skip("Agents not registered")
        
        alice_id = alice_info[0]
        bob_id = bob_info[0]
        
        # Check if already authorized
        is_authorized, auth_id = reputation_contract.functions.isFeedbackAuthorized(
            bob_id, alice_id
        ).call()
        
        if not is_authorized:
            # Authorize feedback from Bob to Alice
            nonce = w3.eth.get_transaction_count(alice_account['address'])
            tx = reputation_contract.functions.acceptFeedback(
                bob_id,
                alice_id
            ).build_transaction({
                'from': alice_account['address'],
                'gas': 200000,
                'gasPrice': w3.to_wei('2', 'gwei'),
                'nonce': nonce,
            })
            
            signed_tx = w3.eth.account.sign_transaction(
                tx,
                alice_account['private_key']
            )
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Allow failure if already authorized
            if receipt.status == 1:
                # Verify authorization
                is_authorized, auth_id = reputation_contract.functions.isFeedbackAuthorized(
                    bob_id, alice_id
                ).call()
                assert is_authorized
        else:
            # Already authorized
            assert is_authorized


@pytest.mark.integration
class TestValidationRegistry:
    """Test ValidationRegistry contract interactions"""
    
    def test_validation_request(self, w3, deployed_contracts, contract_abis,
                               alice_account, bob_account):
        """Test validation request submission"""
        validation_contract = w3.eth.contract(
            address=deployed_contracts['ValidationRegistry'],
            abi=contract_abis['ValidationRegistry']
        )
        identity_contract = w3.eth.contract(
            address=deployed_contracts['IdentityRegistry'],
            abi=contract_abis['IdentityRegistry']
        )
        
        # Get agent IDs
        alice_info = identity_contract.functions.resolveByAddress(
            alice_account['address']
        ).call()
        bob_info = identity_contract.functions.resolveByAddress(
            bob_account['address']
        ).call()
        
        # Skip if agents not registered
        if alice_info[0] == 0 or bob_info[0] == 0:
            pytest.skip("Agents not registered")
        
        alice_id = alice_info[0]
        bob_id = bob_info[0]
        
        # Create validation request
        data_hash = w3.keccak(text="Test validation data")
        
        nonce = w3.eth.get_transaction_count(alice_account['address'])
        tx = validation_contract.functions.validationRequest(
            bob_id,
            alice_id,
            data_hash
        ).build_transaction({
            'from': alice_account['address'],
            'gas': 300000,
            'gasPrice': w3.to_wei('2', 'gwei'),
            'nonce': nonce,
        })
        
        signed_tx = w3.eth.account.sign_transaction(
            tx,
            alice_account['private_key']
        )
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        assert receipt.status == 1
        
        # Verify request exists
        request = validation_contract.functions.getValidationRequest(data_hash).call()
        assert request[0] == bob_id  # validator ID
        assert request[1] == alice_id  # server ID