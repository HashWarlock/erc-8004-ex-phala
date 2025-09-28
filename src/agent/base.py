"""
ERC-8004 TEE Agent Base Class

Provides core functionality for trustless agent interactions.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from .tee_auth import TEEAuthenticator
from .registry import RegistryClient
from .eip712 import EIP712Signer


class AgentRole(Enum):
    """Agent role types."""
    SERVER = "server"
    VALIDATOR = "validator"
    CLIENT = "client"
    CUSTOM = "custom"


@dataclass
class AgentConfig:
    """Agent configuration parameters."""
    domain: str
    salt: str
    role: AgentRole
    rpc_url: str
    chain_id: int
    use_tee_auth: bool = True
    private_key: Optional[str] = None
    tee_endpoint: Optional[str] = None


@dataclass
class RegistryAddresses:
    """ERC-8004 registry contract addresses."""
    identity: str
    reputation: str
    validation: str
    tee_verifier: str


class BaseAgent(ABC):
    """
    Base class for ERC-8004 TEE Agents.

    Provides:
    - TEE-secured key derivation and signing
    - ERC-8004 registry interactions
    - Agent lifecycle management
    - Extensible plugin system
    """

    def __init__(self, config: AgentConfig, registries: RegistryAddresses):
        """
        Initialize the base agent.

        Args:
            config: Agent configuration
            registries: Registry contract addresses
        """
        self.config = config
        self.registries = registries
        self.agent_id: Optional[int] = None
        self.is_registered = False
        self._plugins: Dict[str, Any] = {}

        # Initialize core components
        self._init_tee_auth()
        self._init_registry_client()
        self._init_signer()

        print(f"🤖 Agent initialized for domain: {config.domain}")

    # Core Agent Lifecycle
    async def register(self) -> int:
        """
        Register agent in ERC-8004 Identity Registry.

        Returns:
            Agent ID assigned by the registry
        """
        if self.is_registered:
            return self.agent_id

        # Get agent address
        agent_address = await self._get_agent_address()

        # Create agent card
        agent_card = await self._create_agent_card()

        print(f"📝 Registering agent with domain: {self.config.domain}")

        # Register on-chain
        registry_dict = {
            'identity': self.registries.identity,
            'reputation': self.registries.reputation,
            'validation': self.registries.validation
        }

        self.agent_id = await self._registry_client.register_agent(
            domain=self.config.domain,
            agent_address=agent_address,
            agent_card=agent_card
        )

        self.is_registered = True
        print(f"✅ Agent registered with ID: {self.agent_id}")

        return self.agent_id

    async def get_attestation(self) -> Dict[str, Any]:
        """
        Get TEE attestation for this agent.

        Returns:
            Attestation data including quote and measurements
        """
        return await self._tee_auth.get_attestation()

    async def sign_message(self, message: Dict[str, Any]) -> str:
        """
        Sign message using EIP-712 standard.

        Args:
            message: Message data to sign

        Returns:
            Signature as hex string
        """
        return await self._signer.sign_typed_data(message)

    # Registry Interactions
    async def submit_reputation_feedback(
        self,
        target_agent_id: int,
        rating: int,
        data: Dict[str, Any]
    ) -> str:
        """
        Submit feedback to reputation registry.

        Args:
            target_agent_id: ID of agent being rated
            rating: Rating value (1-5)
            data: Additional feedback data

        Returns:
            Transaction hash
        """
        return await self._registry_client.submit_feedback(
            target_agent_id, rating, data
        )

    async def request_validation(
        self,
        validator_agent_id: int,
        data_hash: str
    ) -> str:
        """
        Request validation from validator agent.

        Args:
            validator_agent_id: ID of validator
            data_hash: Hash of data to validate

        Returns:
            Transaction hash
        """
        return await self._registry_client.request_validation(
            validator_agent_id, data_hash
        )

    async def submit_validation_response(
        self,
        data_hash: str,
        response: int
    ) -> str:
        """
        Submit validation response.

        Args:
            data_hash: Hash of validated data
            response: Validation result (0=invalid, 1=valid, 2=uncertain)

        Returns:
            Transaction hash
        """
        return await self._registry_client.submit_validation_response(
            data_hash, response
        )

    # Abstract Methods - Implement in derived classes
    @abstractmethod
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming task - implement agent-specific logic.

        Args:
            task_data: Task data to process

        Returns:
            Processing result
        """
        pass

    @abstractmethod
    async def _create_agent_card(self) -> Dict[str, Any]:
        """
        Create agent card with capabilities and endpoints.

        Returns:
            Agent card dictionary
        """
        pass

    # Plugin System
    def add_plugin(self, plugin_name: str, plugin_instance: Any):
        """
        Add plugin for extended functionality.

        Args:
            plugin_name: Name of the plugin
            plugin_instance: Plugin instance
        """
        self._plugins[plugin_name] = plugin_instance
        print(f"🔌 Plugin '{plugin_name}' added")

    def get_plugin(self, plugin_name: str) -> Any:
        """
        Get plugin instance.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin instance or None
        """
        return self._plugins.get(plugin_name)

    def list_plugins(self) -> List[str]:
        """
        List all registered plugins.

        Returns:
            List of plugin names
        """
        return list(self._plugins.keys())

    # Private Implementation Methods
    def _init_tee_auth(self):
        """Initialize TEE authentication."""
        self._tee_auth = TEEAuthenticator(
            domain=self.config.domain,
            salt=self.config.salt,
            use_tee=self.config.use_tee_auth,
            tee_endpoint=self.config.tee_endpoint,
            private_key=self.config.private_key
        )

    def _init_registry_client(self):
        """Initialize registry client."""
        registry_dict = {
            'identity': self.registries.identity,
            'reputation': self.registries.reputation,
            'validation': self.registries.validation
        }

        self._registry_client = RegistryClient(
            rpc_url=self.config.rpc_url,
            chain_id=self.config.chain_id,
            registries=registry_dict,
            account=self._tee_auth.account if hasattr(self._tee_auth, 'account') else None
        )

    def _init_signer(self):
        """Initialize EIP-712 signer."""
        self._signer = EIP712Signer(
            domain_name="ERC8004-TEE-Agents",
            domain_version="1.0.0",
            chain_id=self.config.chain_id,
            account=self._tee_auth.account if hasattr(self._tee_auth, 'account') else None
        )

    async def _get_agent_address(self) -> str:
        """
        Get agent's blockchain address.

        Returns:
            Ethereum address
        """
        return await self._tee_auth.derive_address()

    # Utility Methods
    async def get_agent_info(self) -> Dict[str, Any]:
        """
        Get this agent's information from registry.

        Returns:
            Agent information
        """
        if not self.agent_id:
            return {"error": "Agent not registered"}

        return await self._registry_client.get_agent_info(self.agent_id)

    async def get_reputation(self) -> Dict[str, Any]:
        """
        Get this agent's reputation.

        Returns:
            Reputation information
        """
        if not self.agent_id:
            return {"error": "Agent not registered"}

        return await self._registry_client.get_reputation(self.agent_id)

    def get_status(self) -> Dict[str, Any]:
        """
        Get agent status summary.

        Returns:
            Status information
        """
        return {
            "domain": self.config.domain,
            "role": self.config.role.value,
            "is_registered": self.is_registered,
            "agent_id": self.agent_id,
            "use_tee": self.config.use_tee_auth,
            "plugins": self.list_plugins()
        }


# Factory function for easy agent creation
def create_agent(
    agent_type: str,
    config: AgentConfig,
    registries: RegistryAddresses
) -> BaseAgent:
    """
    Factory function to create specific agent types.

    Args:
        agent_type: Type of agent to create
        config: Agent configuration
        registries: Registry addresses

    Returns:
        Agent instance

    Raises:
        ValueError: If agent type is unknown
    """
    if agent_type == "server":
        from ..templates.server_agent import ServerAgent
        return ServerAgent(config, registries)
    elif agent_type == "validator":
        from ..templates.validator_agent import ValidatorAgent
        return ValidatorAgent(config, registries)
    elif agent_type == "client":
        from ..templates.client_agent import ClientAgent
        return ClientAgent(config, registries)
    elif agent_type == "custom":
        from ..templates.custom_agent import CustomAgent
        return CustomAgent(config, registries)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")