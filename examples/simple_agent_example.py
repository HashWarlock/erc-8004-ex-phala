#!/usr/bin/env python3
"""
ChaosChain Agent SDK - Simple Example

This example demonstrates how developers can easily create agents that integrate
with the ChaosChain protocol using the unified SDK.

Usage:
    python examples/simple_agent_example.py
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import agents
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))

from chaoschain_agent_sdk import create_server_agent, create_client_agent

# Load environment variables
load_dotenv()

def main():
    """Simple example of using the ChaosChain Agent SDK"""
    
    print("🚀 ChaosChain Agent SDK - Simple Example")
    print("=" * 50)
    
    try:
        # Step 1: Create a server agent (Alice)
        print("\n📝 Step 1: Creating Server Agent (Alice)")
        alice = create_server_agent(
            agent_name="Alice",
            agent_domain="alice.example.com"
        )
        
        # Step 2: Register Alice's identity
        print("\n🆔 Step 2: Registering Alice's Identity")
        agent_id, tx_hash = alice.register_identity()
        print(f"✅ Alice registered with Agent ID: {agent_id}")
        
        # Step 3: Generate market analysis
        print("\n📊 Step 3: Generating Market Analysis")
        analysis = alice.generate_market_analysis("BTC")
        confidence = analysis.get("genesis_studio_metadata", {}).get("confidence_score", "N/A")
        print(f"✅ Analysis completed with {confidence}% confidence")
        
        # Step 4: Store evidence on IPFS
        print("\n📁 Step 4: Storing Evidence on IPFS")
        cid = alice.store_evidence(analysis, "analysis")
        print(f"✅ Evidence stored at IPFS CID: {cid}")
        
        # Step 5: Create a client agent (Charlie)
        print("\n👤 Step 5: Creating Client Agent (Charlie)")
        charlie = create_client_agent(
            agent_name="Charlie",
            agent_domain="charlie.example.com"
        )
        
        # Step 6: Register Charlie's identity
        print("\n🆔 Step 6: Registering Charlie's Identity")
        charlie_id, charlie_tx = charlie.register_identity()
        print(f"✅ Charlie registered with Agent ID: {charlie_id}")
        
        # Step 7: Charlie pays Alice for the analysis
        print("\n💳 Step 7: Charlie Pays Alice via x402")
        payment_result = charlie.pay_for_service(
            service_provider="Alice",
            service_type="market_analysis",
            base_amount=1.0,
            quality_multiplier=confidence / 100.0 if confidence != "N/A" else 1.0,
            evidence_cid=cid
        )
        
        if payment_result["payment_result"]["success"]:
            print(f"✅ Payment successful: ${payment_result['final_amount']} USDC")
            print(f"   Transaction: {payment_result['payment_result']['transaction_hash']}")
        else:
            print(f"❌ Payment failed: {payment_result['payment_result'].get('error', 'Unknown error')}")
        
        # Step 8: Create enhanced evidence package
        print("\n📦 Step 8: Creating Enhanced Evidence Package")
        evidence_package = alice.create_evidence_package(
            work_data={"analysis_cid": cid, "confidence": confidence},
            payment_receipts=[payment_result["payment_result"]["payment_receipt"]] if payment_result["payment_result"]["success"] else [],
            related_evidence=[cid]
        )
        
        enhanced_cid = alice.store_evidence(evidence_package, "enhanced_package")
        print(f"✅ Enhanced evidence package stored at: {enhanced_cid}")
        
        # Step 9: Display SDK status
        print("\n📊 Step 9: SDK Status Summary")
        alice_status = alice.get_sdk_status()
        charlie_status = charlie.get_sdk_status()
        
        print(f"\n🤖 Alice (Server Agent):")
        print(f"   Agent ID: {alice_status['agent_info']['agent_id']}")
        print(f"   Wallet: {alice_status['agent_info']['wallet_address']}")
        print(f"   Role: {alice_status['agent_info']['role']}")
        
        print(f"\n👤 Charlie (Client Agent):")
        print(f"   Agent ID: {charlie_status['agent_info']['agent_id']}")
        print(f"   Wallet: {charlie_status['agent_info']['wallet_address']}")
        print(f"   Role: {charlie_status['agent_info']['role']}")
        
        print(f"\n💳 Payment Summary:")
        alice_payments = alice.get_payment_history()
        charlie_payments = charlie.get_payment_history()
        print(f"   Alice received {len([p for p in alice_payments if p['to_agent'] == 'Alice'])} payments")
        print(f"   Charlie made {len([p for p in charlie_payments if p['from_agent'] == 'Charlie'])} payments")
        
        print("\n🎉 Example completed successfully!")
        print("\n" + "=" * 50)
        print("🔗 Key Benefits Demonstrated:")
        print("✅ Simple agent creation with unified SDK")
        print("✅ Automatic ERC-8004 identity registration")
        print("✅ AI-powered market analysis generation")
        print("✅ IPFS evidence storage")
        print("✅ x402 frictionless payments")
        print("✅ Enhanced evidence packages with payment proofs")
        print("✅ Complete audit trail for trustless commerce")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        print("\n💡 Make sure you have:")
        print("   • Configured your .env file with all required variables")
        print("   • Set NETWORK=base-sepolia")
        print("   • Funded your operator wallet with Base Sepolia ETH")
        print("   • Valid API keys for Pinata, Coinbase AgentKit, etc.")

if __name__ == "__main__":
    main()
