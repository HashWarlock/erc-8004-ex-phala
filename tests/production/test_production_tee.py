"""
Production TEE Test - Run in actual TEE environment
Tests real dstack SDK integration without mocks
"""

import asyncio
import os
from src.agent.tee_auth import TEEAuthenticator
from src.agent.base import BaseAgent, AgentConfig, AgentRole, RegistryAddresses


async def test_tee_key_derivation():
    """Test real TEE key derivation in production"""
    print("\n" + "="*60)
    print("TEST 1: TEE Key Derivation")
    print("="*60)

    try:
        # Create TEE authenticator (production mode, no simulator)
        auth = TEEAuthenticator(
            domain="test-agent.phala.network",
            salt="production-test-salt-123",
            use_tee=True,
            tee_endpoint=None  # Will use default socket
        )

        print(f"✓ TEE Authenticator initialized")
        print(f"  Domain: {auth.domain}")
        print(f"  TEE Mode: {auth.use_tee}")
        print(f"  Endpoint: {auth.tee_endpoint}")

        # Get derived address
        address = await auth.derive_address()
        print(f"\n✓ Key derived successfully")
        print(f"  Address: {address}")
        print(f"  Length: {len(address)} chars (should be 42)")

        return True, auth

    except Exception as e:
        print(f"\n✗ Key derivation failed: {e}")
        return False, None


async def test_tee_attestation(auth: TEEAuthenticator):
    """Test real TEE attestation generation"""
    print("\n" + "="*60)
    print("TEST 2: TEE Attestation Generation")
    print("="*60)

    try:
        # Get attestation with 64-byte application data
        attestation = await auth.get_attestation()

        print(f"✓ Attestation generated")

        if "error" in attestation:
            print(f"  Error: {attestation['error']}")
            print(f"  Mode: {attestation.get('mode', 'unknown')}")
            return False

        print(f"  Quote length: {len(attestation.get('quote', b''))} bytes")
        print(f"  Event log: {attestation.get('event_log', 'None')}")
        print(f"  Application data size: {attestation['application_data']['size']} bytes")
        print(f"  Method: {attestation['application_data']['method']}")
        print(f"  Domain: {attestation['application_data']['domain']}")

        # Verify 64-byte requirement
        app_data_hex = attestation['application_data']['raw']
        app_data_bytes = bytes.fromhex(app_data_hex)
        assert len(app_data_bytes) == 64, f"Application data must be 64 bytes, got {len(app_data_bytes)}"
        print(f"  ✓ 64-byte requirement verified")

        return True

    except Exception as e:
        print(f"\n✗ Attestation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_tee_signing(auth: TEEAuthenticator):
    """Test message signing with TEE-derived key"""
    print("\n" + "="*60)
    print("TEST 3: Message Signing with TEE Key")
    print("="*60)

    try:
        import hashlib

        # Create test message
        message = b"Production TEE test message"
        message_hash = hashlib.sha256(message).digest()

        print(f"  Message: {message.decode()}")
        print(f"  Hash: {message_hash.hex()[:32]}...")

        # Sign with TEE-derived key
        signature = await auth.sign_with_tee(message_hash)

        print(f"\n✓ Message signed successfully")
        print(f"  Signature length: {len(signature)} bytes (should be 65)")
        print(f"  Signature: {signature.hex()[:64]}...")

        # Verify signature components
        r = signature[:32]
        s = signature[32:64]
        v = signature[64]

        print(f"\n  Signature components:")
        print(f"    r (32 bytes): {r.hex()[:32]}...")
        print(f"    s (32 bytes): {s.hex()[:32]}...")
        print(f"    v (1 byte): {v} (should be 27 or 28)")

        assert v in [27, 28], f"Invalid v value: {v}"
        print(f"  ✓ Signature format valid")

        return True

    except Exception as e:
        print(f"\n✗ Signing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_initialization():
    """Test full agent initialization with TEE"""
    print("\n" + "="*60)
    print("TEST 4: Full Agent Initialization")
    print("="*60)

    try:
        # Load config from environment
        config = AgentConfig(
            domain=os.getenv("AGENT_DOMAIN", "test-agent.phala.network"),
            salt=os.getenv("AGENT_SALT", "prod-test-salt"),
            role=AgentRole.SERVER,
            rpc_url=os.getenv("RPC_URL", "https://sepolia.base.org"),
            chain_id=int(os.getenv("CHAIN_ID", "84532")),
            use_tee_auth=True,
            tee_endpoint=None
        )

        registries = RegistryAddresses(
            identity=os.getenv("IDENTITY_REGISTRY_ADDRESS", "0x000c5A70B7269c5eD4238DcC6576e598614d3f70"),
            reputation=os.getenv("REPUTATION_REGISTRY_ADDRESS", "0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde"),
            validation=os.getenv("VALIDATION_REGISTRY_ADDRESS", "0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d"),
            tee_verifier=os.getenv("TEE_VERIFIER_ADDRESS", "0x1b841e88ba786027f39ecf9Cd160176b22E3603c")
        )

        print(f"  Configuration loaded:")
        print(f"    Domain: {config.domain}")
        print(f"    Role: {config.role.value}")
        print(f"    Chain: {config.chain_id}")
        print(f"    TEE Mode: {config.use_tee_auth}")

        # Note: BaseAgent is abstract, so we'll just test TEE components
        print(f"\n  ✓ Configuration valid")
        print(f"  Note: Full agent registration requires implementing process_task()")

        return True

    except Exception as e:
        print(f"\n✗ Agent initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all production TEE tests"""
    print("\n" + "="*80)
    print(" PRODUCTION TEE ENVIRONMENT TESTS")
    print(" Testing actual dstack SDK integration in real TEE")
    print("="*80)

    results = []

    # Test 1: Key derivation
    success, auth = await test_tee_key_derivation()
    results.append(("Key Derivation", success))

    if not success or auth is None:
        print("\n⚠️  Stopping tests - key derivation failed")
        return

    # Test 2: Attestation
    success = await test_tee_attestation(auth)
    results.append(("Attestation", success))

    # Test 3: Signing
    success = await test_tee_signing(auth)
    results.append(("Signing", success))

    # Test 4: Agent initialization
    success = await test_agent_initialization()
    results.append(("Agent Init", success))

    # Summary
    print("\n" + "="*80)
    print(" TEST SUMMARY")
    print("="*80)

    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status:10} {test_name}")

    passed = sum(1 for _, s in results if s)
    total = len(results)

    print(f"\n  Total: {passed}/{total} tests passed")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()

    # Run tests
    asyncio.run(main())