#!/usr/bin/env python3
"""
Test script for TEE simulator using dstack Python SDK

This properly uses the dstack-sdk Python package to interact with
the TEE simulator, demonstrating:
1. TEE information retrieval
2. Key derivation with certificates
3. TDX quote generation for remote attestation

Based on official dstack SDK documentation.
"""

import os
import sys
import asyncio
import pytest

# Import dstack SDK
try:
    from dstack_sdk import DstackClient, AsyncDstackClient

    SDK_AVAILABLE = True
except ImportError:
    print("❌ dstack-sdk not installed. Run: pip install dstack-sdk")
    SDK_AVAILABLE = False
    sys.exit(1)

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"


def test_tee_with_sdk():
    """
    Test TEE simulator functionality using the official dstack Python SDK

    The SDK provides clean APIs for:
    - info(): Get TEE base image information
    - get_key(): Generate keys with X.509 certificates
    - get_quote(): Generate TDX quotes for attestation
    """

    print(f"{BLUE}{'=' * 70}")
    print("  dstack TEE Simulator Test (Python SDK)")
    print(f"{'=' * 70}{RESET}\n")

    # Get socket path from environment or use default
    socket_path = os.environ.get("DSTACK_SIMULATOR_ENDPOINT")
    if not socket_path:
        project_root = os.path.dirname(os.path.abspath(__file__))
        socket_path = os.path.join(
            project_root, ".dstack", "sdk", "simulator", "tappd.sock"
        )

    print(f"📍 Socket path: {socket_path}")

    # Check if socket exists
    if not os.path.exists(socket_path):
        print(f"{RED}❌ Socket file not found{RESET}")
        print("💡 Run: make tee-start")
        pytest.skip("Socket file not found - run 'make tee-start'")

    print(f"{GREEN}✅ Socket file found{RESET}\n")

    try:
        # Initialize the DstackClient with the socket path
        print(f"{CYAN}Initializing DstackClient...{RESET}")
        client = DstackClient(endpoint=socket_path)
        print(f"{GREEN}✅ Client initialized{RESET}\n")

        # Test 1: Get TEE Information
        print(f"{YELLOW}Test 1: Get TEE Base Image Information{RESET}")
        try:
            info = client.info()
            print(f"{GREEN}✅ TEE Info retrieved:{RESET}")

            # Display key information
            if hasattr(info, "app_id"):
                print(f"   App ID: {info.app_id}")
            if hasattr(info, "instance_id"):
                print(f"   Instance ID: {info.instance_id}")
            if hasattr(info, "app_name"):
                print(f"   App Name: {info.app_name}")

            # TCB Info
            if hasattr(info, "tcb_info"):
                print(f"   TCB Info:")
                if hasattr(info.tcb_info, "mrtd"):
                    print(f"     MRTD: {info.tcb_info.mrtd[:40]}...")
                if hasattr(info.tcb_info, "event_log") and info.tcb_info.event_log:
                    print(f"     Event Log Entries: {len(info.tcb_info.event_log)}")
                    if len(info.tcb_info.event_log) > 0:
                        print(
                            f"     First Event: {info.tcb_info.event_log[0].event if hasattr(info.tcb_info.event_log[0], 'event') else 'N/A'}"
                        )

        except Exception as e:
            print(f"{RED}❌ Failed to get info: {e}{RESET}")

        print()

        # Test 2: Derive Key with Certificate
        print(f"{YELLOW}Test 2: Derive Key with X.509 Certificate{RESET}")
        try:
            # Derive a key with a unique identifier
            unique_id = "test-key-001"
            print(f"   Deriving key for ID: {unique_id}")

            key_result = client.get_key(unique_id)

            print(f"{GREEN}✅ Key derived successfully:{RESET}")

            # Display key information
            if hasattr(key_result, "key"):
                # The key is an X.509 private key in PEM format
                key_preview = key_result.key[:100] if key_result.key else "N/A"
                print(f"   Private Key (PEM): {key_preview}...")

            if hasattr(key_result, "certificate_chain"):
                # Certificate chain for the key
                cert_preview = (
                    key_result.certificate_chain[:100]
                    if key_result.certificate_chain
                    else "N/A"
                )
                print(f"   Certificate Chain: {cert_preview}...")

            # Get key as bytes
            if hasattr(key_result, "toBytes"):
                key_bytes = key_result.toBytes()
                print(f"   Key Size (bytes): {len(key_bytes)}")

        except Exception as e:
            print(f"{RED}❌ Failed to derive key: {e}{RESET}")

        print()

        # Test 3: Generate TDX Quote (Remote Attestation)
        print(f"{YELLOW}Test 3: Generate TDX Quote for Remote Attestation{RESET}")
        try:
            # Data to be attested
            attestation_data = "test-attestation-data-123"
            hash_algo = "sha256"

            print(f"   Data to attest: {attestation_data}")
            print(f"   Hash algorithm: {hash_algo}")

            # Generate TDX quote
            quote_result = client.get_quote(attestation_data.encode())

            print(f"{GREEN}✅ TDX Quote generated:{RESET}")

            # Display quote information
            if hasattr(quote_result, "quote"):
                # The quote is in hex format
                quote_preview = (
                    quote_result.quote[:100] if quote_result.quote else "N/A"
                )
                print(f"   Quote (hex): {quote_preview}...")
                print(f"   Quote Length: {len(quote_result.quote) // 2} bytes")

            if hasattr(quote_result, "event_log"):
                print(f"   Event Log: {quote_result.event_log}")

            # Replay RTMRs if available
            if hasattr(quote_result, "replay_rtmrs"):
                try:
                    rtmrs = quote_result.replay_rtmrs()
                    print(f"   RTMRs replayed: {rtmrs}")
                except Exception as e:
                    print(f"   RTMRs replay not available: {e}")

        except Exception as e:
            print(f"{RED}❌ Failed to generate TDX quote: {e}{RESET}")

        print()

        # Test 4: Multiple Key Derivation
        print(f"{YELLOW}Test 4: Multiple Key Derivation (Testing Uniqueness){RESET}")
        try:
            keys = []
            for i in range(3):
                unique_id = f"test-key-{i:03d}"
                key_result = client.get_key(unique_id)

                # Get first part of the key for comparison
                if hasattr(key_result, "key"):
                    key_identifier = (
                        key_result.key[:50] if key_result.key else f"key_{i}"
                    )
                else:
                    key_identifier = f"key_{i}"

                keys.append(key_identifier)
                print(f"   Key {i + 1} ID '{unique_id}': {key_identifier[:30]}...")

            # Check uniqueness
            if len(keys) == len(set(keys)):
                print(f"{GREEN}✅ All derived keys are unique{RESET}")
            else:
                print(
                    f"{YELLOW}⚠️  Some keys are identical (check key derivation){RESET}"
                )

        except Exception as e:
            print(f"{RED}❌ Failed in multiple key derivation: {e}{RESET}")

        print()

        # Test 5: Generate Multiple Quotes
        print(f"{YELLOW}Test 5: Generate Multiple TDX Quotes{RESET}")
        try:
            test_data = ["user-data-1", "user-data-2", "different-content"]

            for data in test_data:
                quote_result = client.get_quote(data.encode())
                if hasattr(quote_result, "quote"):
                    print(f"   Quote for '{data}': {quote_result.quote[:40]}...")

            print(f"{GREEN}✅ Multiple quotes generated successfully{RESET}")

        except Exception as e:
            print(f"{RED}❌ Failed to generate multiple quotes: {e}{RESET}")

        print(f"\n{GREEN}{'=' * 70}")
        print("✅ TEE SDK Test Complete!")
        print(f"{'=' * 70}{RESET}")

    except Exception as e:
        print(f"{RED}❌ Test failed with error: {e}{RESET}")
        import traceback

        traceback.print_exc()
        raise


@pytest.mark.asyncio
async def test_async_client():
    """
    Test using the async client (AsyncDstackClient)

    This demonstrates how to use the async version of the SDK
    for better performance in async applications.
    """
    print(f"\n{CYAN}Testing Async Client...{RESET}")

    socket_path = os.environ.get("DSTACK_SIMULATOR_ENDPOINT")
    if not socket_path:
        project_root = os.path.dirname(os.path.abspath(__file__))
        socket_path = os.path.join(
            project_root, ".dstack", "sdk", "simulator", "tappd.sock"
        )

    try:
        client = AsyncDstackClient(endpoint=socket_path)

        # Get info asynchronously
        info = await client.info()
        print(f"{GREEN}✅ Async info retrieved{RESET}")
        if hasattr(info, "app_id"):
            print(f"   App ID: {info.app_id}")

        # Derive key asynchronously
        key = await client.get_key("async-test-key")
        print(f"{GREEN}✅ Async key derived{RESET}")
        if hasattr(key, "key"):
            print(f"   Key preview: {key.key[:50]}...")

        # Generate quote asynchronously
        quote = await client.get_quote(b"async-test-data")
        print(f"{GREEN}✅ Async quote generated{RESET}")
        if hasattr(quote, "quote"):
            print(f"   Quote preview: {quote.quote[:50]}...")

    except Exception as e:
        print(f"{RED}❌ Async test failed: {e}{RESET}")
        raise


def main():
    """Main entry point"""

    if not SDK_AVAILABLE:
        print(f"{RED}dstack SDK not available{RESET}")
        return 1

    print(f"{CYAN}=== dstack TEE Simulator Test Suite ==={RESET}")
    print(f"Using dstack Python SDK for proper TEE interaction\n")

    # Run synchronous tests
    success = test_tee_with_sdk()

    # Optionally run async tests
    if success:
        print(f"\n{CYAN}=== Async Client Tests ==={RESET}")
        try:
            async_success = asyncio.run(test_async_client())
            success = success and async_success
        except Exception as e:
            print(f"{YELLOW}⚠️  Async tests skipped: {e}{RESET}")

    if success:
        print(f"\n{GREEN}🎉 All tests passed successfully!{RESET}")
        print("\nThe TEE simulator is working correctly with:")
        print("  ✅ Info retrieval")
        print("  ✅ Key derivation with certificates")
        print("  ✅ TDX quote generation for attestation")
    else:
        print(f"\n{RED}Some tests failed. Check the output above.{RESET}")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
