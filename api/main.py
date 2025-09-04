#!/usr/bin/env python3
"""
FastAPI Application for ERC-8004 Agent Services

This module provides REST API endpoints for interacting with the trustless agent system.
"""

from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any
import os
import logging
from datetime import datetime

# Import models and WebSocket support
from api.models import MarketAnalysisRequest, AnalysisResponse
from api.websocket import setup_websocket_routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import agents
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.server_agent import ServerAgent
from agents.validator_agent import ValidatorAgent
from agents.client_agent import ClientAgent
from agents.tee_server_agent import TEEServerAgent
from agents.tee_validator_agent import TEEValidatorAgent
from agents.tee_client_agent import TEEClientAgent

# Global agent instances
agents: Dict[str, Any] = {}

# Security
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting ERC-8004 Agent API Service...")

    # Initialize agents based on environment configuration
    use_tee = os.getenv("USE_TEE_AUTH", "false").lower() == "true"

    try:
        if use_tee:
            logger.info("Initializing TEE-enabled agents...")

            # Initialize TEE agents
            agents["server"] = TEEServerAgent(
                agent_domain=os.getenv("SERVER_AGENT_DOMAIN", "alice.example.com"),
                salt=os.getenv("SERVER_AGENT_SALT", "server-secret-salt-2024"),
            )

            agents["validator"] = TEEValidatorAgent(
                agent_domain=os.getenv("VALIDATOR_AGENT_DOMAIN", "bob.example.com"),
                salt=os.getenv("VALIDATOR_AGENT_SALT", "validator-secret-salt-2024"),
            )

            agents["client"] = TEEClientAgent(
                agent_domain=os.getenv("CLIENT_AGENT_DOMAIN", "charlie.example.com"),
                salt=os.getenv("CLIENT_AGENT_SALT", "client-secret-salt-2024"),
            )
        else:
            logger.info("Initializing traditional agents...")

            # Initialize traditional agents
            agents["server"] = ServerAgent(
                agent_domain=os.getenv("SERVER_AGENT_DOMAIN", "alice.example.com"),
                private_key=os.getenv("SERVER_AGENT_PRIVATE_KEY"),
            )

            agents["validator"] = ValidatorAgent(
                agent_domain=os.getenv("VALIDATOR_AGENT_DOMAIN", "bob.example.com"),
                private_key=os.getenv("VALIDATOR_AGENT_PRIVATE_KEY"),
            )

            agents["client"] = ClientAgent(
                agent_domain=os.getenv("CLIENT_AGENT_DOMAIN", "charlie.example.com"),
                private_key=os.getenv("CLIENT_AGENT_PRIVATE_KEY"),
            )

        # Register agents if not already registered
        for agent_type, agent in agents.items():
            if not agent.agent_id:
                logger.info(f"Registering {agent_type} agent...")
                agent.register_agent()
                logger.info(
                    f"{agent_type.capitalize()} agent registered with ID: {agent.agent_id}"
                )

        logger.info("All agents initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}")
        raise

    yield

    # Cleanup
    logger.info("Shutting down ERC-8004 Agent API Service...")


# Create FastAPI app
app = FastAPI(
    title="ERC-8004 Agent API",
    description="REST API for interacting with trustless agents on the ERC-8004 standard",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup WebSocket routes
setup_websocket_routes(app)


# Authentication dependency
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """Verify API token"""
    token = credentials.credentials
    expected_token = os.getenv("API_TOKEN")

    if not expected_token:
        # No token configured, allow access (development mode)
        return "development"

    if token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return "authenticated"


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": {
            agent_type: {
                "initialized": agent is not None,
                "agent_id": agent.agent_id if agent else None,
            }
            for agent_type, agent in agents.items()
        },
    }


# Agent info endpoints
@app.get("/agents")
async def get_agents(auth: str = Depends(verify_token)):
    """Get information about all agents"""
    return {
        agent_type: {
            "agent_id": agent.agent_id,
            "domain": agent.agent_domain,
            "address": agent.address,
            "card": agent.get_agent_card(),
        }
        for agent_type, agent in agents.items()
    }


@app.get("/agents/{agent_type}")
async def get_agent(agent_type: str, auth: str = Depends(verify_token)):
    """Get information about a specific agent"""
    if agent_type not in agents:
        raise HTTPException(
            status_code=404, detail=f"Agent type '{agent_type}' not found"
        )

    agent = agents[agent_type]
    return {
        "agent_id": agent.agent_id,
        "domain": agent.agent_domain,
        "address": agent.address,
        "card": agent.get_agent_card(),
    }


# Server agent endpoints
@app.post("/server/analyze", response_model=AnalysisResponse)
async def analyze_market(
    request: MarketAnalysisRequest, auth: str = Depends(verify_token)
):
    """Request market analysis from server agent"""
    agent = agents.get("server")
    if not agent:
        raise HTTPException(status_code=503, detail="Server agent not available")

    try:
        # Call the actual method name used by the agent
        if hasattr(agent, "perform_market_analysis"):
            analysis = agent.perform_market_analysis(request.symbol, request.timeframe)
        else:
            # Fallback for agents without the method
            analysis = {
                "symbol": request.symbol,
                "timeframe": request.timeframe,
                "analysis": "Market analysis not available for this agent type",
                "error": "Method not implemented",
            }

        # Broadcast update via WebSocket (fire and forget for now)
        # TODO: Implement proper async task for broadcasts
        # await broadcast_agent_event("analysis_started", "server", {
        #     "symbol": request.symbol,
        #     "timeframe": request.timeframe
        # })

        return AnalysisResponse(
            status="success",
            analysis=analysis,
            agent_id=agent.agent_id,
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Validator agent endpoints
@app.post("/validator/validate")
async def validate_analysis(request: Dict[str, Any], auth: str = Depends(verify_token)):
    """Validate an analysis using validator agent"""
    agent = agents.get("validator")
    if not agent:
        raise HTTPException(status_code=503, detail="Validator agent not available")

    try:
        analysis_data = request.get("analysis_data")
        if not analysis_data:
            raise ValueError("analysis_data is required")

        server_agent_id = request.get("server_agent_id", 1)

        # Create data hash for validation
        import hashlib
        import json

        data_hash = hashlib.sha256(
            json.dumps(analysis_data, sort_keys=True).encode()
        ).hexdigest()

        # Store the data temporarily for validator to retrieve
        import os

        os.makedirs("data", exist_ok=True)
        with open(f"data/{data_hash}.json", "w") as f:
            json.dump(analysis_data, f)

        # Validate using data hash
        validation = agent.validate_analysis(data_hash)

        return {
            "status": "success",
            "validation": validation,
            "agent_id": agent.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Client agent endpoints
@app.post("/client/feedback/authorize")
async def authorize_feedback(
    request: Dict[str, Any], auth: str = Depends(verify_token)
):
    """Have the server authorize a client to provide feedback"""
    # Get the server agent (it needs to authorize the client)
    server = agents.get("server")
    client = agents.get("client")

    if not server or not client:
        raise HTTPException(status_code=503, detail="Agents not available")

    try:
        # Server authorizes client to provide feedback
        tx_hash = server.authorize_client_feedback(client.agent_id)

        return {
            "status": "success",
            "transaction_hash": tx_hash,
            "authorizer": "server",
            "authorized": "client",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Authorization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/client/feedback/submit")
async def submit_feedback(request: Dict[str, Any], auth: str = Depends(verify_token)):
    """Submit feedback for a server agent"""
    agent = agents.get("client")
    if not agent:
        raise HTTPException(status_code=503, detail="Client agent not available")

    try:
        server_agent_id = request.get("server_agent_id")
        score = request.get("score")
        comment = request.get("comment", "")

        if not server_agent_id or score is None:
            raise ValueError("server_agent_id and score are required")

        feedback = agent.submit_feedback(server_agent_id, score, comment)

        return {
            "status": "success",
            "feedback": feedback,
            "agent_id": agent.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Feedback submission failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/client/reputation/{server_agent_id}")
async def get_reputation(server_agent_id: int, auth: str = Depends(verify_token)):
    """Get reputation information for a server agent"""
    agent = agents.get("client")
    if not agent:
        raise HTTPException(status_code=503, detail="Client agent not available")

    try:
        reputation = agent.check_server_reputation(server_agent_id)

        return {
            "status": "success",
            "reputation": reputation,
            "agent_id": agent.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Reputation check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Workflow endpoints
@app.post("/workflow/complete")
async def complete_workflow(request: Dict[str, Any], auth: str = Depends(verify_token)):
    """Execute complete analysis workflow"""
    try:
        symbol = request.get("symbol", "BTC")
        timeframe = request.get("timeframe", "1d")

        # Step 1: Market analysis
        server = agents.get("server")
        if hasattr(server, "perform_market_analysis"):
            analysis = server.perform_market_analysis(symbol, timeframe)
        else:
            raise HTTPException(
                status_code=501, detail="Market analysis not implemented"
            )

        # Step 2: Validation
        validator = agents.get("validator")
        # Create data hash for validation
        import hashlib
        import json

        data_hash = hashlib.sha256(
            json.dumps(analysis, sort_keys=True).encode()
        ).hexdigest()
        # Store the data for validator
        import os

        os.makedirs("data", exist_ok=True)
        with open(f"data/{data_hash}.json", "w") as f:
            json.dump(analysis, f)
        validation = validator.validate_analysis(data_hash)

        # Step 3: Feedback
        client = agents.get("client")
        score = client.evaluate_service_quality(analysis)

        # Server must authorize client to provide feedback
        server.authorize_client_feedback(client.agent_id)

        feedback = client.submit_feedback(
            server.agent_id, score, "API workflow execution"
        )

        return {
            "status": "success",
            "workflow": {
                "analysis": analysis,
                "validation": validation,
                "feedback": feedback,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# TEE attestation endpoint
@app.get("/attestation/{agent_type}")
async def get_attestation(agent_type: str, auth: str = Depends(verify_token)):
    """Get TEE attestation for an agent"""
    if agent_type not in agents:
        raise HTTPException(
            status_code=404, detail=f"Agent type '{agent_type}' not found"
        )

    agent = agents[agent_type]

    # Check if agent has TEE capabilities
    attestation = None

    if hasattr(agent, "get_tee_attestation"):
        try:
            attestation = agent.get_tee_attestation()
        except Exception as e:
            logger.error(f"Attestation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    elif hasattr(agent, "tee_client"):
        # It's a TEE agent, create attestation
        try:
            quote = agent.tee_client.get_quote("attestation request")
            attestation = {
                "has_attestation": True,
                "tee_endpoint": getattr(agent, "tee_endpoint", "/var/run/dstack.sock"),
                "quote": quote.quote if hasattr(quote, "quote") else str(quote),
            }
        except Exception as e:
            attestation = {"has_attestation": False, "error": str(e)}
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Agent '{agent_type}' does not support TEE attestation",
        )

    if attestation:
        return {
            "status": "success",
            "attestation": attestation,
            "agent_id": agent.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to generate attestation")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
