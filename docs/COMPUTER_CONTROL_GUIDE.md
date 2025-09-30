# Computer Control Agent Guide

TEE-secured ERC-8004 agent with computer control capabilities via sandbox API.

---

## Overview

The Computer Control Agent extends the base ERC-8004 agent protocol with system control capabilities through the [aio-sandbox](https://sandbox.agent-infra.com) API. It provides:

- **Shell command execution** with security constraints
- **File operations** (read, write, search, list)
- **Code execution** (Python, Node.js)
- **System monitoring** and information
- **TEE-secured operations** with cryptographic verification
- **ERC-8004 compliance** for on-chain coordination

---

## Installation

### 1. Install Python Dependencies

```bash
# Core dependencies (already installed)
pip install web3 eth-account

# Sandbox API client
pip install aio-sandbox

# Web server
pip install fastapi uvicorn[standard]
```

### 2. Start Sandbox Instance

The agent requires a sandbox API endpoint:

```bash
# Option 1: Use public sandbox
export SANDBOX_URL="https://sandbox.agent-infra.com"

# Option 2: Run local sandbox (if available)
# Follow instructions at: https://sandbox.agent-infra.com/guide
export SANDBOX_URL="http://localhost:8080"
```

### 3. Configure Environment

```bash
# Agent configuration
export AGENT_DOMAIN="localhost:8000"
export AGENT_SALT="your-unique-salt-here"  # Change this!

# Sandbox configuration
export SANDBOX_URL="http://localhost:8080"

# Server configuration
export AGENT_HOST="0.0.0.0"
export AGENT_PORT="8000"
```

---

## Quick Start

### Run Demo Script

```bash
cd /home/gem/erc-8004-ex-phala
python examples/computer_control_demo.py
```

This demonstrates:
- Agent initialization with TEE
- Shell command execution
- File operations
- Code execution (Python & Node.js)
- System information gathering
- Agent card generation

### Start HTTP Server

```bash
python deployment/computer_control_server.py
```

Access at:
- API: `http://localhost:8000/api/control`
- Docs: `http://localhost:8000/docs`
- Status: `http://localhost:8000/api/status`

---

## API Reference

### Base URL
```
http://localhost:8000
```

### Endpoints

#### `POST /api/control`

Execute computer control operations.

**Request Body:**
```json
{
  "task_id": "unique-task-id",
  "type": "operation-type",
  "command": "optional-command",
  "path": "optional-file-path",
  "content": "optional-file-content",
  "code": "optional-code",
  "directory": "optional-directory",
  "pattern": "optional-search-pattern",
  "timeout": 60,
  "async_exec": false
}
```

**Operation Types:**

1. **`shell`** - Execute shell commands
2. **`file_read`** - Read file contents
3. **`file_write`** - Write file contents
4. **`file_list`** - List directory contents
5. **`file_search`** - Search file contents
6. **`code_python`** - Execute Python code
7. **`code_nodejs`** - Execute Node.js code
8. **`system_info`** - Get system information

---

## Usage Examples

### 1. Shell Command Execution

**Request:**
```bash
curl -X POST http://localhost:8000/api/control \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "shell-001",
    "type": "shell",
    "command": "ls -la | head -10"
  }'
```

**Response:**
```json
{
  "task_id": "shell-001",
  "agent_id": null,
  "type": "shell",
  "status": "completed",
  "output": "total 64\ndrwxr-xr-x 10 user user 4096...",
  "exit_code": 0
}
```

### 2. Write File

**Request:**
```bash
curl -X POST http://localhost:8000/api/control \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "file-001",
    "type": "file_write",
    "path": "/tmp/test.txt",
    "content": "Hello from TEE Agent!"
  }'
```

**Response:**
```json
{
  "task_id": "file-001",
  "agent_id": null,
  "type": "file_write",
  "status": "completed",
  "path": "/tmp/test.txt",
  "bytes_written": 22
}
```

### 3. Read File

**Request:**
```bash
curl -X POST http://localhost:8000/api/control \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "file-002",
    "type": "file_read",
    "path": "/tmp/test.txt"
  }'
```

**Response:**
```json
{
  "task_id": "file-002",
  "agent_id": null,
  "type": "file_read",
  "status": "completed",
  "content": "Hello from TEE Agent!",
  "path": "/tmp/test.txt"
}
```

### 4. List Directory

**Request:**
```bash
curl -X POST http://localhost:8000/api/control \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "file-003",
    "type": "file_list",
    "directory": "/tmp"
  }'
```

**Response:**
```json
{
  "task_id": "file-003",
  "agent_id": null,
  "type": "file_list",
  "status": "completed",
  "directory": "/tmp",
  "files": ["test.txt", "other_file.log", ...]
}
```

### 5. Search Files

**Request:**
```bash
curl -X POST http://localhost:8000/api/control \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "file-004",
    "type": "file_search",
    "pattern": "error",
    "path": "/var/log"
  }'
```

**Response:**
```json
{
  "task_id": "file-004",
  "agent_id": null,
  "type": "file_search",
  "status": "completed",
  "pattern": "error",
  "matches": [
    {"file": "/var/log/syslog", "line": 42, "text": "Error occurred..."}
  ]
}
```

### 6. Execute Python Code

**Request:**
```bash
curl -X POST http://localhost:8000/api/control \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "code-001",
    "type": "code_python",
    "code": "import datetime\nprint(datetime.datetime.now())",
    "timeout": 60
  }'
```

**Response:**
```json
{
  "task_id": "code-001",
  "agent_id": null,
  "type": "code_python",
  "status": "completed",
  "output": "2025-10-01 12:34:56.789",
  "execution_time": 0.123
}
```

### 7. Execute Node.js Code

**Request:**
```bash
curl -X POST http://localhost:8000/api/control \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "code-002",
    "type": "code_nodejs",
    "code": "console.log(\"Node version:\", process.version);",
    "timeout": 60
  }'
```

**Response:**
```json
{
  "task_id": "code-002",
  "agent_id": null,
  "type": "code_nodejs",
  "status": "completed",
  "output": "Node version: v18.17.0"
}
```

### 8. Get System Information

**Request:**
```bash
curl -X POST http://localhost:8000/api/control \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "system-001",
    "type": "system_info"
  }'
```

**Response:**
```json
{
  "task_id": "system-001",
  "agent_id": null,
  "type": "system_info",
  "status": "completed",
  "system_info": {
    "os": "Linux 6.9.0-dstack",
    "cpu": "Intel(R) Xeon(R) CPU...",
    "memory": "total: 16GB, used: 8GB, free: 8GB",
    "disk": "/dev/sda1: 500GB total, 200GB used",
    "uptime": "up 5 days, 3:42"
  }
}
```

---

## Python Client Example

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def execute_command(task_id: str, command: str):
    """Execute shell command."""
    response = requests.post(
        f"{BASE_URL}/api/control",
        json={
            "task_id": task_id,
            "type": "shell",
            "command": command
        }
    )
    return response.json()

def write_file(task_id: str, path: str, content: str):
    """Write file."""
    response = requests.post(
        f"{BASE_URL}/api/control",
        json={
            "task_id": task_id,
            "type": "file_write",
            "path": path,
            "content": content
        }
    )
    return response.json()

def execute_python(task_id: str, code: str):
    """Execute Python code."""
    response = requests.post(
        f"{BASE_URL}/api/control",
        json={
            "task_id": task_id,
            "type": "code_python",
            "code": code,
            "timeout": 60
        }
    )
    return response.json()

# Examples
if __name__ == "__main__":
    # Execute command
    result = execute_command("test-1", "pwd")
    print(f"Current directory: {result['output']}")

    # Write file
    result = write_file("test-2", "/tmp/agent_test.txt", "Hello!")
    print(f"Wrote {result['bytes_written']} bytes")

    # Execute code
    result = execute_python("test-3", """
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
print(f"Mean: {arr.mean()}")
""")
    print(f"Code output: {result['output']}")
```

---

## Agent Card (ERC-8004)

The computer control agent generates an ERC-8004 compliant agent card:

```bash
curl http://localhost:8000/api/card
```

**Response:**
```json
{
  "name": "TEE Computer Control Agent - localhost:8000",
  "description": "TEE-secured agent with computer control capabilities...",
  "version": "1.0.0",
  "capabilities": [
    {
      "name": "shell-execution",
      "description": "Execute shell commands with security constraints"
    },
    {
      "name": "file-operations",
      "description": "Read, write, and search files on the system"
    },
    {
      "name": "code-execution",
      "description": "Run Python and Node.js code in isolated environments"
    },
    {
      "name": "system-monitoring",
      "description": "Monitor system resources and status"
    }
  ],
  "transport": {
    "type": "http",
    "endpoint": "https://localhost:8000",
    "authentication": {
      "type": "eip712",
      "required": false
    }
  },
  "trustModels": [
    {
      "type": "tee-attestation",
      "provider": "phala-network",
      "endpoint": "https://localhost:8000/api/attestation"
    }
  ],
  "infrastructure": {
    "platform": "phala-network",
    "tee_type": "intel-tdx",
    "attestation_provider": "dstack",
    "deployment": "local"
  },
  "metadata": {
    "role": "computer-control",
    "sandbox_url": "http://localhost:8080",
    "supported_operations": [
      "shell",
      "file_read",
      "file_write",
      "file_list",
      "file_search",
      "code_python",
      "code_nodejs",
      "system_info"
    ],
    "security": {
      "tee_secured": true,
      "sandboxed": true,
      "resource_limits": true
    }
  }
}
```

---

## Security Features

### 1. TEE-Secured Keys
- Keys derived deterministically from domain + salt
- Private keys never leave Intel TDX enclave
- Cryptographic proof of identity

### 2. Sandboxed Execution
- All operations run through sandbox API
- Resource limits enforced
- Isolated execution environments

### 3. Attestation
- Remote attestation via Intel TDX
- Verifiable execution environment
- Proof of TEE operation

### 4. Access Control
- Task-level authorization (future)
- Rate limiting (future)
- Audit logging (future)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                Computer Control Agent Server                │
│                    (FastAPI + uvicorn)                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  HTTP API Endpoints:                                        │
│  • POST /api/control   - Computer control operations       │
│  • GET  /api/status    - Agent status                      │
│  • GET  /api/card      - ERC-8004 agent card               │
│  • GET  /api/attestation - TEE attestation                 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ComputerControlAgent:                                      │
│  • Extends BaseAgent                                        │
│  • 8 operation types                                        │
│  • Task routing and processing                              │
│  • ERC-8004 compliance                                      │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  AioClient (aio-sandbox):                                   │
│  • Shell operations                                         │
│  • File operations                                          │
│  • Code execution (Python, Node.js)                         │
│  • MCP integration                                          │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TEE Layer (dstack):                                        │
│  • Key derivation                                           │
│  • Remote attestation                                       │
│  • Secure operations                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Sandbox Environment                      │
│           (https://sandbox.agent-infra.com)                 │
├─────────────────────────────────────────────────────────────┤
│  • Isolated execution                                       │
│  • Resource management                                      │
│  • Security enforcement                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Configuration

### Environment Variables

```bash
# Agent identity
AGENT_DOMAIN="localhost:8000"           # Agent domain
AGENT_SALT="your-unique-salt-here"      # Key derivation salt (CHANGE THIS!)

# Sandbox connection
SANDBOX_URL="http://localhost:8080"     # Sandbox API endpoint

# Server configuration
AGENT_HOST="0.0.0.0"                    # Bind address
AGENT_PORT="8000"                       # Listen port

# Blockchain (for future on-chain registration)
RPC_URL="https://sepolia.base.org"
CHAIN_ID="84532"
IDENTITY_REGISTRY_ADDRESS="0x000c5A70B7269c5eD4238DcC6576e598614d3f70"
```

### Custom Configuration File

Create `.env.computer_control`:

```bash
# Copy from example
cp .env.example .env.computer_control

# Edit configuration
nano .env.computer_control

# Load and run
source .env.computer_control
python deployment/computer_control_server.py
```

---

## Troubleshooting

### "aio-sandbox not installed"

**Solution:**
```bash
pip install aio-sandbox
```

### "Sandbox client not initialized"

**Causes:**
- Sandbox not running at `SANDBOX_URL`
- Network connectivity issues
- Import error (aio-sandbox not installed)

**Solutions:**
1. Check sandbox is running:
   ```bash
   curl $SANDBOX_URL/health
   ```

2. Verify URL is correct:
   ```bash
   echo $SANDBOX_URL
   ```

3. Install aio-sandbox:
   ```bash
   pip install aio-sandbox
   ```

### "Connection refused"

**Solution:** Start sandbox instance at the configured URL.

### "Command execution failed"

**Causes:**
- Invalid command syntax
- Insufficient permissions
- Resource limits exceeded

**Solutions:**
1. Test command locally first
2. Check sandbox logs
3. Verify resource limits

### "TEE not detected"

**Impact:** Agent still works but uses standard key derivation instead of TEE.

**Solution:** Run in Phala TEE environment or use dstack simulator.

---

## Advanced Usage

### Custom Operation Types

Extend the agent with custom operations:

```python
# In src/templates/computer_control_agent.py

async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
    task_type = task_data.get("type")

    # Add custom operation
    if task_type == "custom_operation":
        return await self._custom_operation(task_data)

    # ... existing code ...

async def _custom_operation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Your custom operation."""
    # Implementation here
    pass
```

### Task Chaining

Execute multiple operations in sequence:

```python
import requests

tasks = [
    {"task_id": "1", "type": "file_write", "path": "/tmp/data.txt", "content": "test"},
    {"task_id": "2", "type": "shell", "command": "cat /tmp/data.txt"},
    {"task_id": "3", "type": "file_read", "path": "/tmp/data.txt"}
]

for task in tasks:
    result = requests.post("http://localhost:8000/api/control", json=task)
    print(f"Task {task['task_id']}: {result.json()['status']}")
```

### Integration with Other Agents

Use computer control agent as a service for other agents:

```python
from src.templates.computer_control_agent import ComputerControlAgent

# In another agent's code
async def use_computer_control(self):
    control_agent = ComputerControlAgent(config, registries)
    await control_agent.initialize()

    result = await control_agent.process_task({
        "task_id": "delegated-task",
        "type": "code_python",
        "code": "print('Hello from delegated task!')"
    })

    return result
```

---

## Files

- **Agent Class**: [src/templates/computer_control_agent.py](../src/templates/computer_control_agent.py)
- **Server**: [deployment/computer_control_server.py](../deployment/computer_control_server.py)
- **Demo**: [examples/computer_control_demo.py](../examples/computer_control_demo.py)
- **Base Agent**: [src/agent/base.py](../src/agent/base.py)
- **TEE Auth**: [src/agent/tee_auth.py](../src/agent/tee_auth.py)

---

## Status

✅ **Implemented:**
- ComputerControlAgent class
- 8 operation types
- HTTP API server
- Demo script
- ERC-8004 compliance
- TEE integration

⏳ **Future Enhancements:**
- Task authentication & authorization
- Rate limiting
- Audit logging
- Multi-agent coordination
- On-chain reputation tracking
- Payment integration

---

## Related Documentation

- [Local Agent Guide](LOCAL_AGENT_GUIDE.md) - Base agent server
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment
- [ERC-8004 Standard](https://eips.ethereum.org/EIPS/eip-8004) - Agent protocol
- [aio-sandbox Docs](https://sandbox.agent-infra.com) - Sandbox API

---

## Support

For issues or questions:
1. Check logs: `python deployment/computer_control_server.py`
2. Test sandbox: `curl $SANDBOX_URL/health`
3. Verify TEE: Check `/var/run/dstack.sock` exists
4. Review demo: `python examples/computer_control_demo.py`
