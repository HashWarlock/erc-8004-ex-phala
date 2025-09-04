"""
ERC-8004 Agents Package

This package contains AI agents that demonstrate the ERC-8004 Trustless Agents standard.
"""

from .base_agent import ERC8004BaseAgent
from .server_agent import ServerAgent
from .validator_agent import ValidatorAgent
from .client_agent import ClientAgent
from .tee_base_agent import ERC8004TEEAgent
from .tee_server_agent import TEEServerAgent
from .tee_validator_agent import TEEValidatorAgent
from .tee_client_agent import TEEClientAgent
from .eip712_signer import EIP712Signer, TEESecureSigner

__all__ = [
    "ERC8004BaseAgent",
    "ServerAgent",
    "ValidatorAgent",
    "ClientAgent",
    "ERC8004TEEAgent",
    "TEEServerAgent",
    "TEEValidatorAgent",
    "TEEClientAgent",
    "EIP712Signer",
    "TEESecureSigner",
]
