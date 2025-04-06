"""
Agent factory for creating and managing agents.
"""

from typing import Dict, Any, List, Optional, Union, Type
from pydantic import BaseModel
import logging
import importlib
from abc import ABC, abstractmethod

from .agent_definition import AgentDefinition, AgentRequest, AgentResponse, AgentMessage
from ..model_routing.model_router import ModelRouter
from ..model_routing.model_specs import ModelSpecification

logger = logging.getLogger(__name__)


class AgentProvider(ABC):
    """Abstract base class for agent providers."""

    @abstractmethod
    def create_agent(self, definition: AgentDefinition) -> str:
        """
        Create an agent.

        Args:
            definition: Agent definition

        Returns:
            Agent ID
        """
        pass

    @abstractmethod
    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.

        Args:
            agent_id: Agent ID

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_agent(self, agent_id: str) -> Optional[AgentDefinition]:
        """
        Get agent definition.

        Args:
            agent_id: Agent ID

        Returns:
            Agent definition or None if not found
        """
        pass

    @abstractmethod
    def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> Optional[AgentDefinition]:
        """
        Update agent definition.

        Args:
            agent_id: Agent ID
            updates: Updates to apply

        Returns:
            Updated agent definition or None if not found
        """
        pass

    @abstractmethod
    def process_request(self, request: AgentRequest) -> AgentResponse:
        """
        Process a request to an agent.

        Args:
            request: Agent request

        Returns:
            Agent response
        """
        pass


class AgentFactory:
    """Factory for creating and managing agents."""

    def __init__(self, model_router: Optional[ModelRouter] = None):
        """
        Initialize agent factory.

        Args:
            model_router: Model router for selecting models
        """
        self.model_router = model_router or ModelRouter()
        self.providers: Dict[str, AgentProvider] = {}
        self.agents: Dict[str, AgentDefinition] = {}

        # Register default providers
        self._register_default_providers()

    def _register_default_providers(self):
        """Register default agent providers."""
        try:
            # Register SDK provider
            from ..services.openai_sdk_agent import OpenAISDKProvider
            self.register_provider("sdk", OpenAISDKProvider(self.model_router))

            # Register LangGraph provider
            from ..services.langgraph_agent import LangGraphProvider
            self.register_provider("langgraph", LangGraphProvider(self.model_router))

            # Register OpenRouter provider
            from ..services.openrouter_sdk_agent import OpenRouterSDKProvider
            self.register_provider("openrouter", OpenRouterSDKProvider(self.model_router))

            # Try to register Anthropic provider if available
            try:
                from ..services.anthropic_agent import AnthropicProvider
                self.register_provider("anthropic", AnthropicProvider(self.model_router))
            except ImportError:
                logger.info("Anthropic provider not available")

            # Try to register Google provider if available
            try:
                from ..services.google_agent import GoogleProvider
                self.register_provider("google", GoogleProvider(self.model_router))
            except ImportError:
                logger.info("Google provider not available")

        except ImportError as e:
            logger.warning(f"Failed to register default providers: {e}")

    def register_provider(self, provider_type: str, provider: AgentProvider):
        """
        Register an agent provider.

        Args:
            provider_type: Provider type
            provider: Agent provider
        """
        self.providers[provider_type] = provider
        logger.info(f"Registered agent provider: {provider_type}")

    def create_agent(self, definition: AgentDefinition) -> str:
        """
        Create an agent.

        Args:
            definition: Agent definition

        Returns:
            Agent ID
        """
        # Determine provider type
        provider_type = self._get_provider_type(definition)

        # Get provider
        provider = self.providers.get(provider_type)
        if not provider:
            raise ValueError(f"No provider registered for type: {provider_type}")

        # Create agent
        agent_id = provider.create_agent(definition)

        # Store agent definition
        self.agents[agent_id] = definition

        return agent_id

    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.

        Args:
            agent_id: Agent ID

        Returns:
            True if successful, False otherwise
        """
        # Get agent definition
        definition = self.agents.get(agent_id)
        if not definition:
            return False

        # Determine provider type
        provider_type = self._get_provider_type(definition)

        # Get provider
        provider = self.providers.get(provider_type)
        if not provider:
            return False

        # Delete agent
        success = provider.delete_agent(agent_id)

        # Remove agent definition if successful
        if success:
            del self.agents[agent_id]

        return success

    def get_agent(self, agent_id: str) -> Optional[AgentDefinition]:
        """
        Get agent definition.

        Args:
            agent_id: Agent ID

        Returns:
            Agent definition or None if not found
        """
        return self.agents.get(agent_id)

    def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> Optional[AgentDefinition]:
        """
        Update agent definition.

        Args:
            agent_id: Agent ID
            updates: Updates to apply

        Returns:
            Updated agent definition or None if not found
        """
        # Get agent definition
        definition = self.agents.get(agent_id)
        if not definition:
            return None

        # Determine provider type
        provider_type = self._get_provider_type(definition)

        # Get provider
        provider = self.providers.get(provider_type)
        if not provider:
            return None

        # Update agent
        updated = provider.update_agent(agent_id, updates)

        # Update agent definition if successful
        if updated:
            self.agents[agent_id] = updated

        return updated

    def process_request(self, request: AgentRequest) -> AgentResponse:
        """
        Process a request to an agent.

        Args:
            request: Agent request

        Returns:
            Agent response
        """
        # Get agent ID
        agent_id = request.agent_id
        if not agent_id:
            raise ValueError("Agent ID is required")

        # Get agent definition
        definition = self.agents.get(agent_id)
        if not definition:
            raise ValueError(f"Agent not found: {agent_id}")

        # Determine provider type
        provider_type = self._get_provider_type(definition)

        # Get provider
        provider = self.providers.get(provider_type)
        if not provider:
            raise ValueError(f"No provider registered for type: {provider_type}")

        # Process request
        return provider.process_request(request)

    def _get_provider_type(self, definition: AgentDefinition) -> str:
        """
        Get provider type for an agent definition.

        Args:
            definition: Agent definition

        Returns:
            Provider type
        """
        # Check if model is from a specific provider
        model_id = definition.model_id

        # Check for OpenRouter models
        if model_id.startswith("deepseek") or model_id.startswith("mistral") or model_id.startswith("llama"):
            return "openrouter"

        # Check for Anthropic models
        if model_id.startswith("claude"):
            return "anthropic"

        # Check for Google models
        if model_id.startswith("gemini"):
            return "google"

        # Default to agent_type
        return definition.agent_type
