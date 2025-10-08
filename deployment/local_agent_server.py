#!/usr/bin/env python3
"""
Local Agent Server

Run agent locally with HTTP API for interaction and verification.
Demonstrates TEE-derived key signing without requiring on-chain registration.
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
from datetime import datetime
from typing import Dict, Any, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from eth_account.messages import encode_defunct
from eth_utils import keccak
import uvicorn

from src.agent.base import AgentConfig, RegistryAddresses
from src.templates.server_agent import ServerAgent
from src.agent.tee_auth import TEEAuthenticator
from src.agent.tee_verifier import TEEVerifier


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

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), '..', 'static')
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Global agent instance
agent: Optional[ServerAgent] = None
tee_auth: Optional[TEEAuthenticator] = None
tee_verifier: Optional[TEEVerifier] = None


@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup."""
    global agent, tee_auth, tee_verifier

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
    identity_addr = os.getenv("IDENTITY_REGISTRY_ADDRESS", "0x8506e13d47faa2DC8c5a0dD49182e74A6131a0e3")
    reputation_addr = os.getenv("REPUTATION_REGISTRY_ADDRESS", "0xA13497975fd3f6cA74081B074471C753b622C903")
    validation_addr = os.getenv("VALIDATION_REGISTRY_ADDRESS", "0x6e24aA15e134AF710C330B767018d739CAeCE293")
    tee_verifier_addr = os.getenv("TEE_VERIFIER_ADDRESS", "0x481ce1a6EEC3016d1E61725B1527D73Df1c393a5")

    registries = RegistryAddresses(
        identity=identity_addr,
        reputation=reputation_addr,
        validation=validation_addr,
        tee_verifier=tee_verifier_addr
    )

    # Initialize agent
    print("\n🤖 Initializing agent...")
    agent = ServerAgent(config, registries)

    # Initialize TEE verifier
    tee_registry_addr = os.getenv("TEE_REGISTRY_ADDRESS", "0x03eCA4d903Adc96440328C2E3a18B71EB0AFa60D")
    tee_verifier = TEEVerifier(
        w3=agent._registry_client.w3,
        tee_registry_address=tee_registry_addr,
        account=tee_auth.account,
        verifier_address=tee_verifier_addr
    )

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
    """Root endpoint - redirect to funding page."""
    return FileResponse(os.path.join(static_path, 'funding.html'))


@app.get("/funding")
async def funding_page():
    """Funding page."""
    return FileResponse(os.path.join(static_path, 'funding.html'))


@app.get("/dashboard")
async def dashboard_page():
    """Dashboard page."""
    return FileResponse(os.path.join(static_path, 'dashboard.html'))


@app.get("/api/wallet")
async def get_wallet():
    """Get wallet address and balance for funding."""
    if not agent or not tee_auth:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    agent_address = await agent._get_agent_address()
    balance_wei = agent._registry_client.w3.eth.get_balance(agent_address)
    balance_eth = agent._registry_client.w3.from_wei(balance_wei, 'ether')
    min_balance = 0.001  # Minimum ETH for gas

    return {
        "address": agent_address,
        "balance": str(balance_eth),
        "balance_wei": str(balance_wei),
        "qr_code_data": f"ethereum:{agent_address}?chainId={agent.config.chain_id}",
        "chain_id": agent.config.chain_id,
        "chain_name": "Base Sepolia",
        "funded": float(balance_eth) >= min_balance,
        "minimum_balance": str(min_balance)
    }


@app.get("/api/status")
async def get_status():
    """Get agent status - check on-chain."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    agent_address = await agent._get_agent_address()

    # Check on-chain registration (ERC-721 based, check by address only)
    address_check = await agent._registry_client.check_agent_registration(agent_address=agent_address)

    is_registered = False
    agent_id = None
    tee_verified = False

    if address_check["registered"]:
        is_registered = True
        agent_id = address_check["agent_id"]
        agent.agent_id = agent_id
        agent.is_registered = True

        if tee_verifier:
            tee_verified = await tee_verifier.check_tee_registered(agent_id, agent_address)

    return {
        "status": "operational",
        "agent": {
            "domain": agent.config.domain,
            "address": agent_address,
            "agent_id": agent_id,
            "is_registered": is_registered,
            "tee_verified": tee_verified,
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


@app.post("/api/register")
async def register_agent():
    """Register agent on-chain."""
    if not agent or not tee_auth:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    agent_address = await agent._get_agent_address()

    # Check if already registered (ERC-721 based, check by address only)
    address_check = await agent._registry_client.check_agent_registration(agent_address=agent_address)

    if address_check["registered"]:
        agent_id = address_check["agent_id"]
        agent.agent_id = agent_id
        agent.is_registered = True
        return {
            "success": True,
            "agent_id": agent_id,
            "already_registered": True,
            "domain": agent.config.domain,
            "address": agent_address
        }

    # Check balance
    balance_wei = agent._registry_client.w3.eth.get_balance(agent_address)
    balance_eth = float(agent._registry_client.w3.from_wei(balance_wei, 'ether'))

    if balance_eth < 0.001:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Try to register
    try:
        agent_id = await agent._registry_client.register_agent(agent.config.domain, agent_address)
        agent.agent_id = agent_id
        agent.is_registered = True
        return {
            "success": True,
            "agent_id": agent_id,
            "domain": agent.config.domain,
            "address": agent_address
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/tee/register")
async def register_tee():
    """Register TEE with mock proof."""
    global agent, tee_auth, tee_verifier

    if not agent or not tee_auth or not tee_verifier:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    if not agent.is_registered or not agent.agent_id:
        raise HTTPException(status_code=400, detail="Agent must be registered first")

    attestation = await tee_auth.get_attestation()

    # Check if attestation failed
    if "error" in attestation:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get TEE attestation: {attestation.get('error')}"
        )

    # Check if TEE is disabled
    if attestation.get("mode") == "development":
        raise HTTPException(
            status_code=400,
            detail="TEE is disabled. Cannot register without TEE attestation."
        )

    # Validate required fields
    if "quote" not in attestation or "event_log" not in attestation:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid attestation structure. Missing required fields. Got: {list(attestation.keys())}"
        )

    agent_address = await agent._get_agent_address()

    agent_domain = os.getenv('AGENT_DOMAIN', '')

    # Strip protocol prefixes
    for prefix in ['https://', 'http://', 'ipfs://', 'ipns://']:
        if agent_domain.startswith(prefix):
            agent_domain = agent_domain[len(prefix):]

    print(f"🔍 AGENT_DOMAIN: {agent_domain}")

    app_id = agent_domain.split('-')[0] if '-' in agent_domain else agent_domain.split('.')[0]
    dstack_domain = agent_domain.split('.', 1)[1] if '.' in agent_domain else ''

    print(f"🔍 app_id: {app_id}")
    print(f"🔍 dstack_domain: {dstack_domain}")

    tdx_quote = attestation['quote']
    event_log = attestation['event_log']

    try:
        result = await tee_verifier.register_tee_key(
            agent_id=agent.agent_id,
            agent_address=agent_address,
            tdx_quote=tdx_quote,
            app_id=app_id,
            dstack_domain=dstack_domain,
            event_log=event_log,
        )

        if result.get("already_registered"):
            return {"success": True, "already_registered": True, "agent_id": agent.agent_id, "pubkey": result["pubkey"]}

        return {
            "success": True,
            "tx_hash": result["tx_hash"],
            "agent_id": agent.agent_id,
            "pubkey": result["pubkey"],
            "explorer_url": f"https://sepolia.basescan.org/tx/{result['tx_hash']}"
        }
    except Exception as e:
        import traceback
        print(f"TEE registration error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"TEE registration failed: {str(e)}")


@app.post("/api/metadata/update")
async def update_metadata():
    """Update on-chain metadata."""
    if not agent or not agent.is_registered or not agent.agent_id:
        raise HTTPException(status_code=400, detail="Agent not registered")

    agent_address = await agent._get_agent_address()

    # Verify ownership
    owner = agent._registry_client.identity_contract.functions.ownerOf(agent.agent_id).call()
    if owner.lower() != agent_address.lower():
        raise HTTPException(status_code=403, detail="Not owner")

    # Set metadata
    metadata_value = f"https://{agent.config.domain}/agent.json".encode()

    tx = agent._registry_client.identity_contract.functions.setMetadata(
        agent.agent_id,
        "agent_card_uri",
        metadata_value
    ).build_transaction({
        'chainId': agent._registry_client.chain_id,
        'gas': 200000,
        'gasPrice': agent._registry_client.w3.eth.gas_price,
        'nonce': agent._registry_client.w3.eth.get_transaction_count(agent_address)
    })

    signed = agent._registry_client.account.sign_transaction(tx)
    tx_hash = agent._registry_client.w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = agent._registry_client.w3.eth.wait_for_transaction_receipt(tx_hash)

    return {
        "success": True,
        "tx_hash": tx_hash.hex(),
        "agent_id": agent.agent_id
    }


@app.get("/.well-known/agent-card.json")
@app.get("/a2a/card")
async def agent_card():
    """ERC-8004: Agent card at standard path."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return await agent._create_agent_card()


@app.get("/agent.json")
async def agent_registration():
    """ERC-8004 registration-v1 format."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    from src.agent.agent_card import build_erc8004_registration

    agent_address = await agent._get_agent_address()
    identity_registry = os.getenv("IDENTITY_REGISTRY_ADDRESS", "0x8506e13d47faa2DC8c5a0dD49182e74A6131a0e3")

    return build_erc8004_registration(
        domain=agent.config.domain,
        agent_address=agent_address,
        agent_id=agent.agent_id if agent.is_registered else None,
        identity_registry=identity_registry,
        chain_id=agent.config.chain_id,
        config_path="agent_config.json"
    )


tasks = {}

@app.post("/tasks")
async def create_task(request: Dict[str, Any]):
    """A2A: Create task."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    task_id = request.get("taskId") or str(__import__('uuid').uuid4())
    context_id = request.get("contextId") or task_id

    tasks[task_id] = {
        "taskId": task_id,
        "contextId": context_id,
        "status": "pending",
        "artifacts": []
    }

    # Execute async
    asyncio.create_task(execute_task(task_id, request))

    return {"taskId": task_id, "status": "pending"}

@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """A2A: Get task status."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

async def execute_task(task_id: str, request: Dict[str, Any]):
    tasks[task_id]["status"] = "running"
    try:
        result = await agent.process_task(request)
        tasks[task_id].update({
            "status": "completed",
            "artifacts": [{"type": "result", "data": result}]
        })
    except Exception as e:
        tasks[task_id].update({
            "status": "failed",
            "error": str(e)
        })


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
