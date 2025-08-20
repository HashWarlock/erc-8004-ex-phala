"""
ERC-8004 Agents Package

This package contains AI agents that demonstrate the ERC-8004 Trustless Agents standard.
"""

from .base_agent import ERC8004BaseAgent
from .server_agent import ServerAgent
from .validator_agent import ValidatorAgent

__all__ = ['ERC8004BaseAgent', 'ServerAgent', 'ValidatorAgent'] 