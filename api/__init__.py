"""
ERC-8004 Agent API Package

FastAPI-based REST API for trustless agent interactions.
"""

from .main import app
from .models import *
from .websocket import manager, broadcast_agent_event

__all__ = ["app", "manager", "broadcast_agent_event"]
