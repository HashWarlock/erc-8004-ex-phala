#!/usr/bin/env python3
"""
Computer Control Agent Server

TEE-secured agent with computer control capabilities via sandbox API.
Extends the base agent server with system control operations.
"""

import sys
import os
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from src.agent.base import AgentConfig, RegistryAddresses
from src.templates.computer_control_agent import ComputerControlAgent
from src.agent.tee_auth import TEEAuthenticator


# Request Models
class ControlRequest(BaseModel):
    task_id: str
    type: str  # shell, file_read, file_write, code_python, etc.
    command: Optional[str] = None
    path: Optional[str] = None
    content: Optional[str] = None
    code: Optional[str] = None
    directory: Optional[str] = None
    pattern: Optional[str] = None
    timeout: Optional[int] = 60
    async_exec: Optional[bool] = False


# Initialize FastAPI
app = FastAPI(
    title="ERC-8004 Computer Control Agent",
    description="TEE-secured agent with computer control via sandbox API",
    version="1.0.0"
)

# Global agent instance
agent: Optional[ComputerControlAgent] = None
tee_auth: Optional[TEEAuthenticator] = None


@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup."""
    global agent, tee_auth

    print("=" * 80)
    print("STARTING COMPUTER CONTROL AGENT")
    print("=" * 80)

    # Configuration
    domain = os.getenv("AGENT_DOMAIN", "localhost:8000")
    salt = os.getenv("AGENT_SALT", "computer-control-salt")
    sandbox_url = os.getenv("SANDBOX_URL", "http://localhost:8080")

    print(f"\n📍 Agent Domain: {domain}")
    print(f"🔐 Salt: {salt}")
    print(f"🖥️  Sandbox URL: {sandbox_url}")

    # Initialize TEE authenticator
    print("\n🔑 Initializing TEE authentication...")
    tee_auth = TEEAuthenticator(
        domain=domain,
        salt=salt,
        use_tee=True
    )

    address = await tee_auth.derive_address()
    print(f"✅ Agent Address: {address}")

    # Create agent configuration
    config = AgentConfig(
        domain=domain,
        chain_id=84532,  # Base Sepolia
        rpc_url="https://sepolia.base.org",
        private_key=tee_auth.private_key
    )

    # Registry addresses
    registries = RegistryAddresses(
        identity_registry="0x000c5A70B7269c5eD4238DcC6576e598614d3f70",
        reputation_registry=None,
        validation_registry=None
    )

    # Initialize computer control agent
    print("\n🤖 Initializing computer control agent...")
    agent = ComputerControlAgent(config, registries, sandbox_url=sandbox_url)
    await agent.initialize()

    # Generate agent card
    print("\n📋 Generating agent card...")
    agent_card = await agent._create_agent_card()

    print("\n" + "=" * 80)
    print("✅ COMPUTER CONTROL AGENT READY")
    print("=" * 80)
    print(f"\nAgent Name: {agent_card['name']}")
    print(f"Agent Address: {address}")
    print(f"Domain: {domain}")
    print(f"Sandbox: {sandbox_url}")
    print(f"\nCapabilities:")
    for cap in agent_card.get('capabilities', []):
        print(f"  • {cap['name']}: {cap['description'][:60]}...")
    print("\n" + "=" * 80)


@app.get("/")
async def root():
    """Root endpoint with server info."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    return {
        "name": "ERC-8004 Computer Control Agent",
        "status": "operational",
        "domain": agent.config.domain,
        "address": agent.agent_address,
        "sandbox_url": agent.sandbox_url,
        "endpoints": {
            "status": "/api/status",
            "control": "/api/control",
            "card": "/api/card",
            "attestation": "/api/attestation"
        }
    }


@app.get("/api/status")
async def get_status():
    """Get agent status."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    return {
        "status": "operational",
        "agent": {
            "domain": agent.config.domain,
            "address": agent.agent_address,
            "agent_id": agent.agent_id,
            "is_registered": agent.is_registered,
            "chain_id": agent.config.chain_id
        },
        "computer_control": {
            "enabled": agent.sandbox_client is not None,
            "sandbox_url": agent.sandbox_url,
            "session_id": agent.session_id
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/control")
async def control_computer(request: ControlRequest):
    """
    Execute computer control operations.

    Supported types:
    - shell: Execute shell commands
    - file_read: Read file contents
    - file_write: Write file contents
    - file_list: List directory contents
    - file_search: Search file contents
    - code_python: Execute Python code
    - code_nodejs: Execute Node.js code
    - system_info: Get system information
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        # Build task data
        task_data = {
            "task_id": request.task_id,
            "type": request.type
        }

        # Add type-specific parameters
        if request.command:
            task_data["command"] = request.command
            task_data["async"] = request.async_exec
        if request.path:
            task_data["path"] = request.path
        if request.content:
            task_data["content"] = request.content
        if request.code:
            task_data["code"] = request.code
            task_data["timeout"] = request.timeout
        if request.directory:
            task_data["directory"] = request.directory
        if request.pattern:
            task_data["pattern"] = request.pattern

        # Process task
        result = await agent.process_task(task_data)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Control operation failed: {str(e)}")


@app.get("/api/card")
async def get_agent_card():
    """Get ERC-8004 compliant agent card."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        card = await agent._create_agent_card()
        return card
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate card: {str(e)}")


@app.get("/api/attestation")
async def get_attestation():
    """Get TEE attestation."""
    if not tee_auth:
        raise HTTPException(status_code=503, detail="TEE auth not initialized")

    try:
        attestation = await tee_auth.get_attestation()

        response = {
            "agent_address": attestation.get("agent_address"),
            "endpoint": attestation.get("endpoint"),
            "application_data": attestation.get("application_data"),
            "quote_size": len(attestation.get("quote", "")),
            "timestamp": datetime.utcnow().isoformat()
        }

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get attestation: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


def main():
    """Run the computer control agent server."""
    host = os.getenv("AGENT_HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_PORT", "8000"))

    print("\n🚀 Starting computer control agent...")
    print(f"📍 Listening on {host}:{port}")
    print(f"📖 API docs at http://localhost:{port}/docs\n")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
