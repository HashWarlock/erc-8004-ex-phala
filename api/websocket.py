#!/usr/bin/env python3
"""
WebSocket Support for Real-time Agent Updates

This module provides WebSocket endpoints for real-time agent communication.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Any
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "server": set(),
            "validator": set(),
            "client": set(),
            "all": set(),
        }

    async def connect(self, websocket: WebSocket, channel: str = "all"):
        """Accept and track new WebSocket connection"""
        await websocket.accept()
        self.active_connections[channel].add(websocket)
        if channel != "all":
            self.active_connections["all"].add(websocket)
        logger.info(f"WebSocket connected to channel: {channel}")

    def disconnect(self, websocket: WebSocket, channel: str = "all"):
        """Remove WebSocket connection"""
        self.active_connections[channel].discard(websocket)
        if channel != "all":
            self.active_connections["all"].discard(websocket)
        logger.info(f"WebSocket disconnected from channel: {channel}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket"""
        await websocket.send_text(message)

    async def broadcast(self, message: str, channel: str = "all"):
        """Broadcast message to all connections in channel"""
        disconnected = set()
        for connection in self.active_connections[channel]:
            try:
                await connection.send_text(message)
            except:
                disconnected.add(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn, channel)


# Global connection manager
manager = ConnectionManager()


def setup_websocket_routes(app):
    """Add WebSocket routes to FastAPI app"""

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """General WebSocket endpoint for all updates"""
        await manager.connect(websocket, "all")
        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                message = json.loads(data)

                # Echo back with timestamp
                response = {
                    "type": "echo",
                    "original": message,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                await manager.send_personal_message(json.dumps(response), websocket)

        except WebSocketDisconnect:
            manager.disconnect(websocket, "all")

    @app.websocket("/ws/{agent_type}")
    async def agent_websocket(websocket: WebSocket, agent_type: str):
        """WebSocket endpoint for specific agent type updates"""
        if agent_type not in ["server", "validator", "client"]:
            await websocket.close(code=1008, reason="Invalid agent type")
            return

        await manager.connect(websocket, agent_type)
        try:
            while True:
                # Keep connection alive
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle different message types
                if message.get("type") == "subscribe":
                    response = {
                        "type": "subscribed",
                        "channel": agent_type,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    await manager.send_personal_message(json.dumps(response), websocket)

        except WebSocketDisconnect:
            manager.disconnect(websocket, agent_type)


async def broadcast_agent_event(event_type: str, agent_type: str, data: Any):
    """Broadcast agent events to WebSocket clients"""
    message = {
        "type": event_type,
        "agent": agent_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Broadcast to specific agent channel and all channel
    await manager.broadcast(json.dumps(message), agent_type)


async def broadcast_analysis_update(symbol: str, status: str, data: Any = None):
    """Broadcast market analysis updates"""
    message = {
        "type": "analysis_update",
        "symbol": symbol,
        "status": status,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await manager.broadcast(json.dumps(message), "server")


async def broadcast_validation_update(server_id: int, score: int, status: str):
    """Broadcast validation updates"""
    message = {
        "type": "validation_update",
        "server_id": server_id,
        "score": score,
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await manager.broadcast(json.dumps(message), "validator")


async def broadcast_feedback_update(server_id: int, score: int, comment: str = ""):
    """Broadcast feedback updates"""
    message = {
        "type": "feedback_update",
        "server_id": server_id,
        "score": score,
        "comment": comment,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await manager.broadcast(json.dumps(message), "client")
