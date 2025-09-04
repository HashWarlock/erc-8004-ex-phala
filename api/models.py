#!/usr/bin/env python3
"""
Pydantic Models for API Request/Response Validation

This module defines the data models for API endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

# Request Models


class MarketAnalysisRequest(BaseModel):
    """Request model for market analysis"""

    symbol: str = Field(default="BTC", description="Trading symbol to analyze")
    timeframe: str = Field(default="1d", description="Timeframe for analysis")
    indicators: List[str] = Field(
        default=["trend", "volume", "sentiment"],
        description="Technical indicators to include",
    )


class ValidationRequest(BaseModel):
    """Request model for analysis validation"""

    analysis_data: Dict[str, Any] = Field(..., description="Analysis data to validate")
    server_agent_id: Optional[int] = Field(default=1, description="ID of server agent")


class FeedbackAuthorizationRequest(BaseModel):
    """Request model for feedback authorization"""

    server_agent_id: int = Field(..., description="ID of server agent to authorize")


class FeedbackSubmissionRequest(BaseModel):
    """Request model for feedback submission"""

    server_agent_id: int = Field(..., description="ID of server agent")
    score: int = Field(..., ge=0, le=100, description="Feedback score (0-100)")
    comment: Optional[str] = Field(default="", description="Optional feedback comment")


class WorkflowRequest(BaseModel):
    """Request model for complete workflow execution"""

    symbol: str = Field(default="BTC", description="Trading symbol")
    timeframe: str = Field(default="1d", description="Timeframe")


# Response Models


class AgentInfo(BaseModel):
    """Agent information model"""

    agent_id: int
    domain: str
    address: str
    card: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: str
    agents: Dict[str, Dict[str, Any]]


class AnalysisResponse(BaseModel):
    """Market analysis response"""

    status: str
    analysis: Dict[str, Any]
    agent_id: int
    timestamp: str


class ValidationResponse(BaseModel):
    """Validation response"""

    status: str
    validation: Dict[str, Any]
    agent_id: int
    timestamp: str


class FeedbackAuthorizationResponse(BaseModel):
    """Feedback authorization response"""

    status: str
    transaction_hash: Optional[str]
    agent_id: int
    timestamp: str


class FeedbackSubmissionResponse(BaseModel):
    """Feedback submission response"""

    status: str
    feedback: Dict[str, Any]
    agent_id: int
    timestamp: str


class ReputationResponse(BaseModel):
    """Reputation query response"""

    status: str
    reputation: Dict[str, Any]
    agent_id: int
    timestamp: str


class WorkflowResponse(BaseModel):
    """Complete workflow response"""

    status: str
    workflow: Dict[str, Any]
    timestamp: str


class AttestationResponse(BaseModel):
    """TEE attestation response"""

    status: str
    attestation: Dict[str, Any]
    agent_id: int
    timestamp: str


class ErrorResponse(BaseModel):
    """Error response model"""

    detail: str
    status_code: int = 500
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# WebSocket Models


class WebSocketMessage(BaseModel):
    """Base WebSocket message"""

    type: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class AnalysisUpdateMessage(WebSocketMessage):
    """Market analysis update message"""

    type: str = "analysis_update"
    symbol: str
    status: str
    data: Optional[Dict[str, Any]] = None


class ValidationUpdateMessage(WebSocketMessage):
    """Validation update message"""

    type: str = "validation_update"
    server_id: int
    score: int
    status: str


class FeedbackUpdateMessage(WebSocketMessage):
    """Feedback update message"""

    type: str = "feedback_update"
    server_id: int
    score: int
    comment: str = ""


class AgentEventMessage(WebSocketMessage):
    """General agent event message"""

    agent: str
    data: Dict[str, Any]


# Configuration for all models
model_config = ConfigDict(
    json_schema_extra={"example": {"symbol": "BTC", "timeframe": "1d"}}
)
