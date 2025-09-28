#!/usr/bin/env python3
"""
Generate TEE Keys

Generate and manage keys for TEE agents.
"""

import os
import sys
import json
import secrets
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.append(str(Path(__file__).parent.parent))

from eth_account import Account
from dotenv import load_dotenv, set_key


def generate_keys():
    """Generate keys for TEE agent."""

    print("🔑 ERC-8004 TEE Agent Key Generation")
    print("=" * 40)

    # Load existing environment
    load_dotenv()
    env_file = Path('.env')

    # Check for existing keys
    existing_salt = os.getenv('AGENT_SALT')
    if existing_salt and existing_salt != 'default-salt':
        print(f"⚠️  Existing salt found: {existing_salt[:20]}...")
        overwrite = input("Generate new keys? This will overwrite existing! (y/N): ").strip().lower()
        if overwrite != 'y':
            print("❌ Key generation cancelled")
            return

    print("\nSelect key generation mode:")
    print("1. TEE Mode (deterministic, salt-based)")
    print("2. Development Mode (random private key)")
    print("3. Both (TEE + fallback key)")

    mode = input("\nChoice (1/2/3) [3]: ").strip() or '3'

    keys = {}

    # Generate based on mode
    if mode in ['1', '3']:
        # Generate salt for TEE
        salt = generate_salt()
        keys['salt'] = salt
        print(f"\n✅ Generated salt: {salt[:20]}...")

        # Derive address from salt (simulation)
        derived_address = derive_address_from_salt(salt)
        keys['tee_address'] = derived_address
        print(f"📍 Derived TEE address: {derived_address}")

    if mode in ['2', '3']:
        # Generate private key for development
        private_key, address = generate_private_key()
        keys['private_key'] = private_key
        keys['dev_address'] = address
        print(f"\n✅ Generated private key: {private_key[:20]}...")
        print(f"📍 Development address: {address}")

    # Generate domain if not set
    domain = os.getenv('AGENT_DOMAIN', '')
    if not domain or domain == 'localhost':
        domain = input("\nAgent domain (e.g., myagent.com) [localhost]: ").strip() or 'localhost'
        keys['domain'] = domain

    # Update .env file
    print("\n📝 Updating .env file...")
    update_env_file(env_file, keys)

    # Save keys securely
    save_keys_backup(keys)

    print("\n" + "=" * 40)
    print("✅ Key generation complete!")
    print("=" * 40)

    if 'salt' in keys:
        print(f"Salt: {keys['salt'][:30]}...")
        print(f"TEE Address: {keys.get('tee_address')}")

    if 'private_key' in keys:
        print(f"\n⚠️  IMPORTANT: Keep your private key secure!")
        print(f"Private key saved to .env (for development only)")

    print(f"\nDomain: {keys.get('domain', os.getenv('AGENT_DOMAIN'))}")
    print("\nNext steps:")
    print("1. Review and update .env file")
    print("2. Run deployment: python scripts/deploy_agent.py")


def generate_salt() -> str:
    """Generate a secure random salt."""
    return secrets.token_hex(32)


def generate_private_key() -> tuple[str, str]:
    """Generate a new private key and address."""
    account = Account.create()
    return account.key.hex(), account.address


def derive_address_from_salt(salt: str) -> str:
    """
    Derive an address from salt (simulation).

    In production, this would use TEE's key derivation.
    """
    # This is a simulation - actual TEE would derive this securely
    # Create deterministic account from salt
    seed = int.from_bytes(salt.encode()[:32], 'big')
    account = Account.from_key(hex(seed % (2**256)))
    return account.address


def update_env_file(env_file: Path, keys: Dict[str, Any]):
    """Update .env file with new keys."""

    if not env_file.exists():
        # Create new .env file
        with open(env_file, 'w') as f:
            f.write("# ERC-8004 TEE Agent Configuration\n\n")

    # Update keys
    if 'salt' in keys:
        set_key(str(env_file), 'AGENT_SALT', keys['salt'])

    if 'private_key' in keys:
        set_key(str(env_file), 'PRIVATE_KEY', keys['private_key'])

    if 'domain' in keys:
        set_key(str(env_file), 'AGENT_DOMAIN', keys['domain'])

    # Set TEE mode based on what was generated
    if 'salt' in keys and 'private_key' not in keys:
        set_key(str(env_file), 'USE_TEE_AUTH', 'true')
    elif 'private_key' in keys and 'salt' not in keys:
        set_key(str(env_file), 'USE_TEE_AUTH', 'false')
        set_key(str(env_file), 'DEBUG', 'true')

    print("✅ Updated .env file")


def save_keys_backup(keys: Dict[str, Any]):
    """Save backup of generated keys."""

    backup_file = Path('.keys.backup.json')

    # Don't save private key in backup
    safe_keys = {k: v for k, v in keys.items() if k != 'private_key'}

    if 'private_key' in keys:
        safe_keys['has_private_key'] = True
        safe_keys['dev_address'] = keys.get('dev_address')

    with open(backup_file, 'w') as f:
        json.dump(safe_keys, f, indent=2)

    # Set restrictive permissions
    os.chmod(backup_file, 0o600)

    print(f"📄 Key backup saved to {backup_file}")


def verify_keys():
    """Verify existing keys are properly configured."""

    load_dotenv()

    print("\n🔍 Verifying key configuration...")

    salt = os.getenv('AGENT_SALT')
    private_key = os.getenv('PRIVATE_KEY')
    use_tee = os.getenv('USE_TEE_AUTH', 'true').lower() == 'true'

    if use_tee:
        if not salt or salt == 'default-salt':
            print("❌ TEE mode enabled but no valid salt found")
            return False
        print(f"✅ TEE salt configured: {salt[:20]}...")
    else:
        if not private_key:
            print("❌ Development mode enabled but no private key found")
            return False
        print(f"✅ Private key configured: {private_key[:20]}...")

    domain = os.getenv('AGENT_DOMAIN', 'localhost')
    print(f"✅ Domain: {domain}")

    return True


def main():
    """Main entry point."""

    if len(sys.argv) > 1 and sys.argv[1] == 'verify':
        verify_keys()
    else:
        try:
            generate_keys()
        except KeyboardInterrupt:
            print("\n❌ Key generation cancelled")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()