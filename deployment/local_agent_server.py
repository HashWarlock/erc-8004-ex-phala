#!/usr/bin/env python3
"""
Local Agent Server

Run agent locally with HTTP API for interaction and verification.
Demonstrates TEE-derived key signing without requiring on-chain registration.
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
from eth_account.messages import encode_defunct
from eth_utils import keccak
import uvicorn

from src.agent.base import AgentConfig, RegistryAddresses
from src.templates.server_agent import ServerAgent
from src.agent.tee_auth import TEEAuthenticator


# Request/Response Models
class SignRequest(BaseModel):
    message: str


class TaskRequest(BaseModel):
    task_id: str
    query: str
    data: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None


# Initialize FastAPI
app = FastAPI(
    title="ERC-8004 TEE Agent Server",
    description="Local agent server with TEE-derived key verification",
    version="1.0.0"
)

# Global agent instance
agent: Optional[ServerAgent] = None
tee_auth: Optional[TEEAuthenticator] = None


@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup."""
    global agent, tee_auth

    print("=" * 80)
    print("STARTING LOCAL AGENT SERVER")
    print("=" * 80)

    # Get domain from environment or use localhost
    domain = os.getenv("AGENT_DOMAIN", "localhost:8000")
    salt = os.getenv("AGENT_SALT", "local-development-salt")

    print(f"\n📍 Agent Domain: {domain}")
    print(f"🔐 Salt: {salt}")

    # Initialize TEE authenticator
    print("\n🔑 Initializing TEE authentication...")
    tee_auth = TEEAuthenticator(
        domain=domain,
        salt=salt,
        use_tee=True  # Use real TEE
    )

    address = await tee_auth.derive_address()
    print(f"✅ Agent Address: {address}")

    # Get attestation
    print("\n📜 Generating TEE attestation...")
    attestation = await tee_auth.get_attestation()
    if "quote" in attestation:
        quote_size = len(attestation.get("quote", ""))
        print(f"✅ Attestation generated: {quote_size} bytes")

    # Create agent configuration
    from src.agent.base import AgentRole

    config = AgentConfig(
        domain=domain,
        salt=salt,
        role=AgentRole.SERVER,
        chain_id=84532,  # Base Sepolia
        rpc_url="https://sepolia.base.org",
        use_tee_auth=True,
        private_key=tee_auth.private_key
    )

    # Registry addresses (new contracts from environment or defaults)
    identity_addr = os.getenv("IDENTITY_REGISTRY_ADDRESS", "0x19fad4adD9f8C4A129A078464B22E1506275FbDd")
    reputation_addr = os.getenv("REPUTATION_REGISTRY_ADDRESS", "0xA13497975fd3f6cA74081B074471C753b622C903")
    validation_addr = os.getenv("VALIDATION_REGISTRY_ADDRESS", "0x6e24aA15e134AF710C330B767018d739CAeCE293")
    tee_verifier_addr = os.getenv("TEE_VERIFIER_ADDRESS", "0x1b841e88ba786027f39ecf9Cd160176b22E3603c")

    registries = RegistryAddresses(
        identity=identity_addr,
        reputation=reputation_addr,
        validation=validation_addr,
        tee_verifier=tee_verifier_addr
    )

    # Initialize agent
    print("\n🤖 Initializing agent...")
    agent = ServerAgent(config, registries)

    # Generate agent card
    print("\n📋 Generating agent card...")
    agent_card = await agent._create_agent_card()

    print("\n" + "=" * 80)
    print("✅ AGENT SERVER READY")
    print("=" * 80)
    print(f"\nAgent Name: {agent_card['name']}")
    print(f"Agent Address: {address}")
    print(f"Domain: {domain}")
    print(f"\nCapabilities:")
    for cap in agent_card.get('capabilities', []):
        print(f"  • {cap['name']}: {cap['description'][:60]}...")
    print("\n" + "=" * 80)


@app.get("/")
async def root():
    """Root endpoint with server info."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    agent_address = await agent._get_agent_address()

    return {
        "name": "ERC-8004 TEE Agent Server",
        "status": "operational",
        "domain": agent.config.domain,
        "address": agent_address,
        "endpoints": {
            "status": "/api/status",
            "sign": "/api/sign",
            "process": "/api/process",
            "card": "/api/card",
            "attestation": "/api/attestation"
        }
    }


@app.get("/api/status")
async def get_status():
    """Get agent status and identity information."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    agent_address = await agent._get_agent_address()

    return {
        "status": "operational",
        "agent": {
            "domain": agent.config.domain,
            "address": agent_address,
            "agent_id": agent.agent_id,
            "is_registered": agent.is_registered,
            "chain_id": agent.config.chain_id
        },
        "tee": {
            "enabled": True,
            "endpoint": tee_auth.tee_endpoint if tee_auth else None
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/sign")
async def sign_message(request: SignRequest):
    """
    Sign a message with TEE-derived key.

    This endpoint demonstrates the agent's cryptographic identity.
    """
    if not agent or not tee_auth:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        # Create message hash
        message_bytes = request.message.encode('utf-8')
        message_hash = keccak(message_bytes)

        # Sign with TEE key
        signature = await tee_auth.sign_with_tee(message_hash)

        # Also create EIP-191 signature for wallet compatibility
        signable_message = encode_defunct(text=request.message)
        signed_message = tee_auth.account.sign_message(signable_message)

        return {
            "message": request.message,
            "message_hash": "0x" + message_hash.hex(),
            "signature": "0x" + signature.hex(),
            "eip191_signature": signed_message.signature.hex(),
            "signer_address": await agent._get_agent_address(),
            "domain": agent.config.domain,
            "timestamp": datetime.utcnow().isoformat(),
            "verification": {
                "note": "Use eth_account.Account.recover_message() to verify EIP-191 signature",
                "expected_address": await agent._get_agent_address()
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signing failed: {str(e)}")


@app.post("/api/process")
async def process_task(request: TaskRequest):
    """
    Process a task with the agent.

    Demonstrates agent's analytical capabilities.
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        task_data = {
            "task_id": request.task_id,
            "query": request.query,
            "data": request.data or {},
            "parameters": request.parameters or {}
        }

        result = await agent.process_task(task_data)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task processing failed: {str(e)}")


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
    """Get TEE attestation for the agent."""
    if not tee_auth:
        raise HTTPException(status_code=503, detail="TEE auth not initialized")

    try:
        attestation = await tee_auth.get_attestation()

        # Format for API response
        response = {
            "agent_address": attestation.get("agent_address"),
            "endpoint": attestation.get("endpoint"),
            "application_data": attestation.get("application_data"),
            "quote_size": len(attestation.get("quote", "")),
            "event_log_size": len(attestation.get("event_log", "")),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Include full quote if requested
        if attestation.get("quote"):
            response["quote_preview"] = attestation["quote"][:100] + "..." if len(attestation["quote"]) > 100 else attestation["quote"]

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get attestation: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


def main():
    """Run the agent server."""
    # Get configuration
    host = os.getenv("AGENT_HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_PORT", "8000"))

    print("\n🚀 Starting agent server...")
    print(f"📍 Listening on {host}:{port}")
    print(f"📖 API docs available at http://localhost:{port}/docs\n")

    # Run server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
