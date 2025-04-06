"""
Roo-Code adapter module for Atlas-Chat.

This module provides integration with Roo-Code for autonomous agent capabilities
within the Atlas desktop e2b code interpreter environment.
"""

from typing import Dict, Any, List, Optional, Union, Callable
import logging
import os
import json
from pydantic import BaseModel, Field

# Import agent factory components
from ...services.agent_factory.agent_definition import (
    AgentDefinition,
    AgentRequest,
    AgentResponse,
    AgentMessage,
)
from ...services.agent_factory.agent_factory import AgentProvider
from ...services.model_routing.model_router import ModelRouter

logger = logging.getLogger(__name__)

# Try to import roo_code library
try:
    # This is a placeholder - actual import would depend on how Roo-Code is packaged
    import roo_code

    ROO_CODE_AVAILABLE = True
except ImportError:
    logger.warning(
        "roo_code library not available. Install from https://github.com/RooVetGit/Roo-Code"
    )
    ROO_CODE_AVAILABLE = False


class RooCodeConfig(BaseModel):
    """Configuration for Roo-Code adapter."""

    workspace_dir: str = Field(default="./roo_workspace")
    max_iterations: int = 10
    auto_improve: bool = True
    verbose: bool = False
    memory_enabled: bool = True
    tools: List[str] = []
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RooCodeAdapter(AgentProvider):
    """Roo-Code adapter for agent factory."""

    def __init__(
        self,
        model_router: Optional[ModelRouter] = None,
        config: Optional[RooCodeConfig] = None,
    ):
        """
        Initialize Roo-Code adapter.

        Args:
            model_router: Model router for selecting models
            config: Roo-Code configuration
        """
        self.model_router = model_router
        self.config = config or RooCodeConfig()
        self.agents: Dict[str, AgentDefinition] = {}
        self.roo_agents: Dict[str, Any] = {}

        # Check if Roo-Code is available
        if not ROO_CODE_AVAILABLE:
            logger.warning(
                "Roo-Code is not available. Some functionality will be limited."
            )

        # Create workspace directory if it doesn't exist
        os.makedirs(self.config.workspace_dir, exist_ok=True)

    def create_agent(self, definition: AgentDefinition) -> str:
        """
        Create an agent.

        Args:
            definition: Agent definition

        Returns:
            Agent ID
        """
        if not ROO_CODE_AVAILABLE:
            # Fallback implementation when Roo-Code is not available
            agent_id = definition.agent_id
            self.agents[agent_id] = definition
            logger.info(
                f"Created Roo-Code agent (fallback mode): {definition.name} ({agent_id})"
            )
            return agent_id

        # Store agent definition
        agent_id = definition.agent_id
        self.agents[agent_id] = definition

        # Create Roo-Code agent
        try:
            # This is a placeholder - actual implementation would depend on Roo-Code API
            roo_agent = self._create_roo_agent(definition)
            self.roo_agents[agent_id] = roo_agent

            logger.info(f"Created Roo-Code agent: {definition.name} ({agent_id})")

        except Exception as e:
            logger.error(f"Error creating Roo-Code agent: {e}")
            # Continue with fallback implementation

        return agent_id

    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.

        Args:
            agent_id: Agent ID

        Returns:
            True if successful, False otherwise
        """
        if agent_id in self.agents:
            del self.agents[agent_id]

            if agent_id in self.roo_agents:
                # Clean up Roo-Code agent
                try:
                    # This is a placeholder - actual implementation would depend on Roo-Code API
                    self._cleanup_roo_agent(agent_id)
                except Exception as e:
                    logger.error(f"Error cleaning up Roo-Code agent: {e}")

                del self.roo_agents[agent_id]

            return True

        return False

    def get_agent(self, agent_id: str) -> Optional[AgentDefinition]:
        """
        Get agent definition.

        Args:
            agent_id: Agent ID

        Returns:
            Agent definition or None if not found
        """
        return self.agents.get(agent_id)

    def update_agent(
        self, agent_id: str, updates: Dict[str, Any]
    ) -> Optional[AgentDefinition]:
        """
        Update agent definition.

        Args:
            agent_id: Agent ID
            updates: Updates to apply

        Returns:
            Updated agent definition or None if not found
        """
        if agent_id not in self.agents:
            return None

        # Get current definition
        current = self.agents[agent_id]

        # Apply updates
        updated_dict = current.dict()
        updated_dict.update(updates)

        # Create new definition
        updated = AgentDefinition(**updated_dict)

        # Update agents
        self.agents[agent_id] = updated

        # Update Roo-Code agent if available
        if ROO_CODE_AVAILABLE and agent_id in self.roo_agents:
            try:
                # This is a placeholder - actual implementation would depend on Roo-Code API
                self._update_roo_agent(agent_id, updated)
            except Exception as e:
                logger.error(f"Error updating Roo-Code agent: {e}")

        return updated

    def process_request(self, request: AgentRequest) -> AgentResponse:
        """
        Process a request to an agent.

        Args:
            request: Agent request

        Returns:
            Agent response
        """
        # Get agent definition
        agent_id = request.agent_id
        definition = self.agents.get(agent_id)
        if not definition:
            raise ValueError(f"Agent not found: {agent_id}")

        # Check if Roo-Code is available and agent exists
        if ROO_CODE_AVAILABLE and agent_id in self.roo_agents:
            try:
                # Process with Roo-Code
                return self._process_with_roo(request, definition)
            except Exception as e:
                logger.error(f"Error processing with Roo-Code: {e}")
                # Fall back to model-based processing

        # Fall back to model-based processing
        return self._process_with_model(request, definition)

    def _create_roo_agent(self, definition: AgentDefinition) -> Any:
        """
        Create a Roo-Code agent.

        Args:
            definition: Agent definition

        Returns:
            Roo-Code agent
        """
        if not ROO_CODE_AVAILABLE:
            raise ImportError("roo_code library not available")

        # This is a placeholder - actual implementation would depend on Roo-Code API
        agent_config = {
            "agent_id": definition.agent_id,
            "name": definition.name,
            "description": definition.description,
            "system_prompt": definition.system_prompt,
            "model": definition.model_id,
            "workspace_dir": os.path.join(
                self.config.workspace_dir, definition.agent_id
            ),
            "max_iterations": self.config.max_iterations,
            "auto_improve": self.config.auto_improve,
            "verbose": self.config.verbose,
            "memory_enabled": definition.memory_enabled,
            "tools": definition.tools,
        }

        # Create agent workspace directory
        os.makedirs(agent_config["workspace_dir"], exist_ok=True)

        # Save agent configuration
        config_path = os.path.join(agent_config["workspace_dir"], "config.json")
        with open(config_path, "w") as f:
            json.dump(agent_config, f, indent=2)

        # Create and initialize Roo-Code agent
        # This is a placeholder - actual implementation would depend on Roo-Code API
        # roo_agent = roo_code.Agent(**agent_config)
        # roo_agent.initialize()

        # For now, just return the config as a placeholder
        return agent_config

    def _update_roo_agent(self, agent_id: str, definition: AgentDefinition) -> None:
        """
        Update a Roo-Code agent.

        Args:
            agent_id: Agent ID
            definition: Updated agent definition
        """
        if not ROO_CODE_AVAILABLE:
            raise ImportError("roo_code library not available")

        # Get current Roo-Code agent
        roo_agent = self.roo_agents.get(agent_id)
        if not roo_agent:
            raise ValueError(f"Roo-Code agent not found: {agent_id}")

        # Update agent configuration
        roo_agent.update(
            {
                "name": definition.name,
                "description": definition.description,
                "system_prompt": definition.system_prompt,
                "model": definition.model_id,
                "memory_enabled": definition.memory_enabled,
                "tools": definition.tools,
            }
        )

        # Save updated configuration
        workspace_dir = roo_agent.get("workspace_dir")
        config_path = os.path.join(workspace_dir, "config.json")
        with open(config_path, "w") as f:
            json.dump(roo_agent, f, indent=2)

        # Update Roo-Code agent
        # This is a placeholder - actual implementation would depend on Roo-Code API
        # roo_agent.reload_config()

    def _cleanup_roo_agent(self, agent_id: str) -> None:
        """
        Clean up a Roo-Code agent.

        Args:
            agent_id: Agent ID
        """
        if not ROO_CODE_AVAILABLE:
            raise ImportError("roo_code library not available")

        # Get Roo-Code agent
        roo_agent = self.roo_agents.get(agent_id)
        if not roo_agent:
            return

        # Clean up agent resources
        # This is a placeholder - actual implementation would depend on Roo-Code API
        # roo_agent.cleanup()

        # Optionally, clean up workspace
        workspace_dir = roo_agent.get("workspace_dir")
        if workspace_dir and os.path.exists(workspace_dir):
            # Uncomment to actually delete the workspace
            # import shutil
            # shutil.rmtree(workspace_dir)
            pass

    def _process_with_roo(
        self, request: AgentRequest, definition: AgentDefinition
    ) -> AgentResponse:
        """
        Process a request with Roo-Code.

        Args:
            request: Agent request
            definition: Agent definition

        Returns:
            Agent response
        """
        if not ROO_CODE_AVAILABLE:
            raise ImportError("roo_code library not available")

        # Get agent ID
        agent_id = request.agent_id

        # Get Roo-Code agent
        roo_agent = self.roo_agents.get(agent_id)
        if not roo_agent:
            raise ValueError(f"Roo-Code agent not found: {agent_id}")

        # Extract user message
        user_message = None
        for msg in request.messages:
            if msg.role == "user":
                user_message = msg.content
                if isinstance(user_message, list):
                    # Handle multimodal content
                    user_message = " ".join(
                        [
                            part.get("text", "")
                            if isinstance(part, dict) and "text" in part
                            else str(part)
                            for part in user_message
                        ]
                    )
                break

        if not user_message:
            raise ValueError("No user message found in request")

        # Process with Roo-Code
        # This is a placeholder - actual implementation would depend on Roo-Code API
        # response = roo_agent.process(user_message)

        # For now, create a simulated response
        response_content = f"[Roo-Code] I would process your request: '{user_message}' using autonomous agent capabilities."

        # Create response
        response = AgentResponse(
            agent_id=agent_id,
            message=AgentMessage(role="assistant", content=response_content),
            usage={},
            metadata={"processor": "roo_code"},
        )

        return response

    def _process_with_model(
        self, request: AgentRequest, definition: AgentDefinition
    ) -> AgentResponse:
        """
        Process a request with a model (fallback).

        Args:
            request: Agent request
            definition: Agent definition

        Returns:
            Agent response
        """
        # Get agent ID
        agent_id = request.agent_id

        # Get model
        model_id = definition.model_id

        if not self.model_router:
            # Create a simple response if model router is not available
            response = AgentResponse(
                agent_id=agent_id,
                message=AgentMessage(
                    role="assistant",
                    content="I'm sorry, I cannot process your request at this time due to configuration issues.",
                ),
                usage={},
                metadata={"processor": "fallback"},
            )

            return response

        # Prepare messages
        messages = []

        # Add system prompt if not present
        has_system = any(msg.role == "system" for msg in request.messages)
        if not has_system and definition.system_prompt:
            messages.append({"role": "system", "content": definition.system_prompt})

        # Add user and assistant messages
        for msg in request.messages:
            messages.append({"role": msg.role, "content": msg.content})

        try:
            # Get model
            model = self.model_router.get_model(model_id)

            # Generate response
            response_content, usage = model.generate(
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=request.stream,
            )

            # Create response
            response = AgentResponse(
                agent_id=agent_id,
                message=AgentMessage(role="assistant", content=response_content),
                usage=usage,
                metadata={"processor": "model_fallback"},
            )

            return response

        except Exception as e:
            logger.error(f"Error generating response: {e}")

            # Create error response
            response = AgentResponse(
                agent_id=agent_id,
                message=AgentMessage(
                    role="assistant",
                    content="I encountered an error while processing your request.",
                ),
                usage={},
                metadata={"processor": "error", "error": str(e)},
            )

            return response
