"""
Agent Card Generator - ERC-8004 Standard Format

Creates properly formatted agent cards according to the ERC-8004 specification.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class AgentCardBuilder:
    """
    Builder for creating ERC-8004 compliant agent cards.

    Follows the specification at:
    https://eips.ethereum.org/EIPS/eip-8004
    """

    def __init__(
        self,
        name: str,
        description: str,
        version: str = "1.0.0"
    ):
        """
        Initialize agent card builder.

        Args:
            name: Agent name
            description: Agent description
            version: Agent version
        """
        self.card = {
            "name": name,
            "description": description,
            "version": version,
            "capabilities": [],
            "transport": {},
            "registrations": [],
            "trustModels": [],
            "aiModel": None,
            "infrastructure": {}
        }

    def add_capability(
        self,
        name: str,
        description: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> 'AgentCardBuilder':
        """
        Add a capability to the agent card.

        Args:
            name: Capability name (e.g., "text-generation")
            description: Capability description
            parameters: Optional capability parameters

        Returns:
            Self for method chaining
        """
        capability = {
            "name": name,
            "description": description
        }
        if parameters:
            capability["parameters"] = parameters

        self.card["capabilities"].append(capability)
        return self

    def set_transport(
        self,
        transport_type: str,
        url: str,
        authentication: Optional[Dict[str, Any]] = None
    ) -> 'AgentCardBuilder':
        """
        Set transport configuration.

        Args:
            transport_type: Transport type ("http", "websocket", "grpc", etc.)
            url: Endpoint URL
            authentication: Optional authentication details

        Returns:
            Self for method chaining
        """
        self.card["transport"] = {
            "type": transport_type,
            "url": url
        }
        if authentication:
            self.card["transport"]["authentication"] = authentication

        return self

    def add_registration(
        self,
        agent_id: int,
        agent_address: str,
        signature: str,
        chain_id: Optional[int] = None
    ) -> 'AgentCardBuilder':
        """
        Add registration information.

        Args:
            agent_id: On-chain agent ID
            agent_address: CAIP-10 format address (e.g., "eip155:84532:0x...")
            signature: Registration signature
            chain_id: Optional chain ID for multi-chain

        Returns:
            Self for method chaining
        """
        registration = {
            "agentId": agent_id,
            "agentAddress": agent_address,
            "signature": signature
        }
        if chain_id:
            registration["chainId"] = chain_id

        self.card["registrations"].append(registration)
        return self

    def set_trust_models(self, trust_models: List[str]) -> 'AgentCardBuilder':
        """
        Set trust models used by the agent.

        Args:
            trust_models: List of trust model identifiers
                Valid values: "feedback", "inference-validation", "tee-attestation"

        Returns:
            Self for method chaining
        """
        self.card["trustModels"] = trust_models
        return self

    def set_ai_model(
        self,
        provider: str,
        model: str,
        version: str,
        capabilities: List[str],
        context_window: Optional[int] = None,
        training_cutoff: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> 'AgentCardBuilder':
        """
        Set AI model information.

        Args:
            provider: AI provider (e.g., "OpenAI", "Anthropic", "Custom")
            model: Model name (e.g., "gpt-4", "claude-3")
            version: Model version
            capabilities: List of capabilities (e.g., ["text", "vision"])
            context_window: Context window size in tokens
            training_cutoff: Training data cutoff date
            additional_info: Additional model-specific info

        Returns:
            Self for method chaining
        """
        self.card["aiModel"] = {
            "provider": provider,
            "model": model,
            "version": version,
            "capabilities": capabilities
        }

        if context_window:
            self.card["aiModel"]["contextWindow"] = context_window
        if training_cutoff:
            self.card["aiModel"]["trainingCutoff"] = training_cutoff
        if additional_info:
            self.card["aiModel"].update(additional_info)

        return self

    def set_infrastructure(
        self,
        hosting: str,
        region: Optional[str] = None,
        tee_enabled: bool = False,
        attestation_provider: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> 'AgentCardBuilder':
        """
        Set infrastructure information.

        Args:
            hosting: Hosting provider (e.g., "AWS", "GCP", "Azure", "Phala")
            region: Deployment region
            tee_enabled: Whether TEE is enabled
            attestation_provider: TEE attestation provider
            additional_info: Additional infrastructure details

        Returns:
            Self for method chaining
        """
        self.card["infrastructure"] = {
            "hosting": hosting,
            "teeEnabled": tee_enabled
        }

        if region:
            self.card["infrastructure"]["region"] = region
        if attestation_provider:
            self.card["infrastructure"]["attestationProvider"] = attestation_provider
        if additional_info:
            self.card["infrastructure"].update(additional_info)

        return self

    def add_metadata(
        self,
        key: str,
        value: Any
    ) -> 'AgentCardBuilder':
        """
        Add custom metadata field.

        Args:
            key: Metadata key
            value: Metadata value

        Returns:
            Self for method chaining
        """
        if "metadata" not in self.card:
            self.card["metadata"] = {}

        self.card["metadata"][key] = value
        return self

    def build(self) -> Dict[str, Any]:
        """
        Build and return the agent card.

        Returns:
            Complete agent card dictionary
        """
        # Add timestamp if not already present
        if "createdAt" not in self.card:
            self.card["createdAt"] = datetime.utcnow().isoformat() + "Z"

        return self.card


# Convenience functions for common agent types

def create_tee_agent_card(
    name: str,
    description: str,
    domain: str,
    agent_address: str,
    agent_id: Optional[int] = None,
    signature: Optional[str] = None,
    capabilities: Optional[List[tuple[str, str]]] = None,
    chain_id: int = 84532
) -> Dict[str, Any]:
    """
    Create a TEE-secured agent card.

    Args:
        name: Agent name
        description: Agent description
        domain: Agent domain
        agent_address: Agent's Ethereum address (raw format)
        agent_id: On-chain agent ID (if registered)
        signature: Registration signature (if registered)
        capabilities: List of (name, description) tuples
        chain_id: Blockchain chain ID (default: Base Sepolia)

    Returns:
        Agent card dictionary
    """
    builder = AgentCardBuilder(name, description)

    # Add capabilities
    if capabilities:
        for cap_name, cap_desc in capabilities:
            builder.add_capability(cap_name, cap_desc)

    # Set transport
    builder.set_transport(
        "http",
        f"https://{domain}/api",
        authentication={"type": "signature", "scheme": "EIP-712"}
    )

    # Add registration if available
    if agent_id is not None and signature:
        caip10_address = f"eip155:{chain_id}:{agent_address}"
        builder.add_registration(agent_id, caip10_address, signature, chain_id)

    # Set trust models for TEE agent
    builder.set_trust_models(["tee-attestation", "feedback", "inference-validation"])

    # Set infrastructure
    builder.set_infrastructure(
        hosting="Phala Cloud",
        tee_enabled=True,
        attestation_provider="dstack",
        additional_info={
            "teeType": "Intel TDX",
            "attested": True
        }
    )

    return builder.build()


def create_ai_agent_card(
    name: str,
    description: str,
    domain: str,
    agent_address: str,
    ai_provider: str,
    ai_model: str,
    ai_version: str,
    agent_id: Optional[int] = None,
    signature: Optional[str] = None,
    capabilities: Optional[List[tuple[str, str]]] = None,
    tee_enabled: bool = True,
    chain_id: int = 84532
) -> Dict[str, Any]:
    """
    Create an AI-powered agent card.

    Args:
        name: Agent name
        description: Agent description
        domain: Agent domain
        agent_address: Agent's Ethereum address
        ai_provider: AI provider (e.g., "OpenAI", "Anthropic")
        ai_model: AI model name
        ai_version: AI model version
        agent_id: On-chain agent ID (if registered)
        signature: Registration signature (if registered)
        capabilities: List of (name, description) tuples
        tee_enabled: Whether TEE is enabled
        chain_id: Blockchain chain ID

    Returns:
        Agent card dictionary
    """
    builder = AgentCardBuilder(name, description)

    # Add AI capabilities
    default_capabilities = [
        ("text-generation", "Generate human-like text responses"),
        ("analysis", "Analyze data and provide insights"),
        ("reasoning", "Apply logical reasoning to problems")
    ]

    for cap_name, cap_desc in (capabilities or default_capabilities):
        builder.add_capability(cap_name, cap_desc)

    # Set transport
    builder.set_transport(
        "http",
        f"https://{domain}/api",
        authentication={"type": "signature", "scheme": "EIP-712"}
    )

    # Add registration if available
    if agent_id is not None and signature:
        caip10_address = f"eip155:{chain_id}:{agent_address}"
        builder.add_registration(agent_id, caip10_address, signature, chain_id)

    # Set trust models
    trust_models = ["feedback", "inference-validation"]
    if tee_enabled:
        trust_models.append("tee-attestation")
    builder.set_trust_models(trust_models)

    # Set AI model info
    builder.set_ai_model(
        provider=ai_provider,
        model=ai_model,
        version=ai_version,
        capabilities=["text", "analysis"],
        context_window=128000 if "gpt-4" in ai_model.lower() else 200000,
        training_cutoff="2024-04"
    )

    # Set infrastructure
    builder.set_infrastructure(
        hosting="Phala Cloud" if tee_enabled else "Cloud",
        tee_enabled=tee_enabled,
        attestation_provider="dstack" if tee_enabled else None
    )

    return builder.build()


def build_erc8004_registration(
    domain: str,
    agent_address: str,
    agent_id: Optional[int],
    identity_registry: str,
    chain_id: int = 84532,
    config_path: str = "agent_config.json"
) -> Dict[str, Any]:
    """
    Build ERC-8004 registration JSON from config file.

    Spec: https://eips.ethereum.org/EIPS/eip-8004#registration-v1
    """
    import json
    import os

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config not found: {config_path}")

    with open(config_path) as f:
        cfg = json.load(f)

    endpoints = []

    # A2A
    if cfg["endpoints"]["a2a"]["enabled"]:
        endpoints.append({
            "name": "A2A",
            "endpoint": f"https://{domain}/.well-known/agent-card.json",
            "version": cfg["endpoints"]["a2a"]["version"]
        })

    # MCP
    if cfg["endpoints"]["mcp"]["enabled"]:
        ep = {
            "name": "MCP",
            "endpoint": cfg["endpoints"]["mcp"]["endpoint"],
            "version": cfg["endpoints"]["mcp"]["version"]
        }
        if cfg["endpoints"]["mcp"]["capabilities"]:
            ep["capabilities"] = cfg["endpoints"]["mcp"]["capabilities"]
        endpoints.append(ep)

    # OASF
    if cfg["endpoints"]["oasf"]["enabled"]:
        endpoints.append({
            "name": "OASF",
            "endpoint": cfg["endpoints"]["oasf"]["endpoint"],
            "version": cfg["endpoints"]["oasf"]["version"]
        })

    # ENS
    if cfg["endpoints"]["ens"]["enabled"]:
        endpoints.append({
            "name": "ENS",
            "endpoint": cfg["endpoints"]["ens"]["endpoint"],
            "version": cfg["endpoints"]["ens"]["version"]
        })

    # DID
    if cfg["endpoints"]["did"]["enabled"]:
        endpoints.append({
            "name": "DID",
            "endpoint": cfg["endpoints"]["did"]["endpoint"],
            "version": cfg["endpoints"]["did"]["version"]
        })

    # EVM wallets
    for chain in cfg["evmChains"]:
        endpoints.append({
            "name": f"agentWallet-{chain['name']}",
            "endpoint": f"eip155:{chain['chainId']}:{agent_address}"
        })

    card = {
        "type": "https://eips.ethereum.org/EIPS/eip-8004#registration-v1",
        "name": cfg["name"],
        "description": cfg["description"],
        "endpoints": endpoints,
        "supportedTrust": cfg["supportedTrust"]
    }

    if cfg.get("image"):
        card["image"] = cfg["image"]

    if agent_id is not None:
        card["registrations"] = [{
            "agentId": agent_id,
            "agentRegistry": f"eip155:{chain_id}:{identity_registry}"
        }]

    return card