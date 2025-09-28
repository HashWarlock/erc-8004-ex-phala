# dstack SDK Corrections Summary

## Key Corrections Made

### 1. ✅ Client Initialization
**Fixed**: Properly handles simulator vs socket endpoints
```python
# Simulator (development)
if endpoint.startswith("http"):
    client = DstackClient(endpoint)  # e.g., "http://localhost:8090"
# Production (socket)
else:
    client = DstackClient()  # Uses /var/run/dstack.sock
```

### 2. ✅ Key Derivation
**Fixed**: Uses correct method signature and key extraction
```python
# Correct format: wallet/subcategory
key_result = client.get_key("wallet/erc8004-{domain}", salt)
# Use decode_key() to get raw bytes
private_key_bytes = key_result.decode_key()
```

### 3. ✅ Attestation with 64-byte Data
**Fixed**: Ensures application data is exactly 64 bytes
```python
# Multiple methods available:
# 1. Hash method (recommended): keccak256(data) + 32 bytes padding
# 2. Structured: domain(20) + address(42) + padding(2)
# 3. Simple padding: data padded to 64 bytes

application_data = self._create_attestation_data(method="hash")
assert len(application_data) == 64
quote_result = client.get_quote(application_data)
```

### 4. ✅ Helper Method for 64-byte Data
**Added**: `_create_attestation_data()` method with three strategies:

```python
def _create_attestation_data(self, method: str = "structured") -> bytes:
    if method == "hash":
        # Keccak256 hash (32 bytes) + padding (32 bytes) = 64 bytes
        data = f"{domain}:{address}:{salt}".encode()
        hash_bytes = keccak(data)  # 32 bytes
        return hash_bytes + (b'\x00' * 32)

    elif method == "structured":
        # domain(20) + address(42) + padding(2) = 64 bytes
        domain_bytes = domain[:20].ljust(20, b'\x00')
        address_bytes = address[:42].ljust(42, b'\x00')
        return domain_bytes + address_bytes + (b'\x00' * 2)

    else:  # "padded"
        # Simple padding to 64 bytes
        data = f"{domain}:{address}".encode()[:64]
        return data.ljust(64, b'\x00')
```

## Configuration Updates

### Environment Variables
```bash
# Development with simulator
DSTACK_SIMULATOR_ENDPOINT=http://localhost:8090

# Production (uses socket by default)
# No configuration needed, uses /var/run/dstack.sock
```

### Dependencies
```txt
dstack-sdk>=0.2.0  # Ensure latest version with get_key and get_quote
```

## API Usage Summary

| Operation | Correct Method | Returns | Notes |
|-----------|---------------|---------|-------|
| Initialize Client | `DstackClient()` or `DstackClient(url)` | Client instance | URL for simulator only |
| Derive Key | `client.get_key(path, purpose)` | Key object | Use `.decode_key()` for bytes |
| Get Attestation | `client.get_quote(data)` | Quote object | Data must be 64 bytes |
| Key Path Format | `wallet/{subcategory}` | - | Use wallet prefix for keys |

## Important Notes

1. **64-byte Requirement**: The `get_quote()` method requires exactly 64 bytes of application data
2. **Key Derivation Path**: Use `wallet/` prefix for deterministic key generation
3. **Simulator Endpoint**: Default development endpoint is `http://localhost:8090`
4. **Socket Path**: Production uses `/var/run/dstack.sock` by default
5. **Method Names**: Use `get_key()` and `get_quote()`, not `attest()` or other methods

## Testing

To verify the corrections work:

```python
# Test key derivation
client = DstackClient("http://localhost:8090")  # Simulator
key = client.get_key("wallet/test", "salt123")
private_key = key.decode_key()

# Test attestation with 64-byte data
data = b"test" * 16  # 64 bytes
quote = client.get_quote(data)
print(f"Quote: {quote.quote}")
print(f"Event log: {quote.event_log}")
```