"""
Google GenAI integration module for Atlas-Chat.

This module provides integration with Google's Generative AI models using the official
python-genai library for direct access to Gemini models.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

# Import agent factory components
from ...services.agent_factory.agent_definition import (
    AgentDefinition,
    AgentMessage,
    AgentRequest,
    AgentResponse,
)
from ...services.agent_factory.agent_factory import AgentProvider
from ...services.model_routing.model_router import ModelRouter

logger = logging.getLogger(__name__)

# Try to import google-genai library
try:
    import google.generativeai as genai

    GENAI_AVAILABLE = True
except ImportError:
    logger.warning("google-genai library not available. Install with 'pip install google-genai'")
    GENAI_AVAILABLE = False


class GoogleProvider(AgentProvider):
    """Google GenAI provider for agent factory."""

    def __init__(self, model_router: Optional[ModelRouter] = None):
        """
        Initialize Google provider.

        Args:
            model_router: Model router for selecting models
        """
        self.model_router = model_router
        self.agents: Dict[str, AgentDefinition] = {}

        # Initialize Google GenAI client if available
        if GENAI_AVAILABLE:
            api_key = os.environ.get("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                logger.info("Google GenAI client initialized")
            else:
                logger.warning("GOOGLE_API_KEY environment variable not set")

    def create_agent(self, definition: AgentDefinition) -> str:
        """
        Create an agent.

        Args:
            definition: Agent definition

        Returns:
            Agent ID
        """
        if not GENAI_AVAILABLE:
            raise ImportError("google-genai library not available")

        # Store agent definition
        agent_id = definition.agent_id
        self.agents[agent_id] = definition

        logger.info(f"Created Google agent: {definition.name} ({agent_id})")

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

    def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> Optional[AgentDefinition]:
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

        return updated

    def process_request(self, request: AgentRequest) -> AgentResponse:
        """
        Process a request to an agent.

        Args:
            request: Agent request

        Returns:
            Agent response
        """
        if not GENAI_AVAILABLE:
            raise ImportError("google-genai library not available")

        # Get agent definition
        agent_id = request.agent_id
        definition = self.agents.get(agent_id)
        if not definition:
            raise ValueError(f"Agent not found: {agent_id}")

        # Get model
        model_id = definition.model_id

        # Prepare messages
        messages = self._prepare_messages(request.messages, definition)

        # Process request
        response_content, usage = self._call_gemini_model(
            model_id=model_id,
            messages=messages,
            stream=request.stream,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )

        # Create response
        response = AgentResponse(
            agent_id=agent_id,
            message=AgentMessage(role="assistant", content=response_content),
            usage=usage,
            metadata={},
        )

        return response

    def _prepare_messages(
        self, messages: List[AgentMessage], definition: AgentDefinition
    ) -> List[Dict[str, Any]]:
        """
        Prepare messages for Google GenAI.

        Args:
            messages: Agent messages
            definition: Agent definition

        Returns:
            Prepared messages
        """
        # Add system prompt if not present
        has_system = any(msg.role == "system" for msg in messages)

        prepared = []

        if not has_system and definition.system_prompt:
            prepared.append({"role": "system", "content": definition.system_prompt})

        # Add user and assistant messages
        for msg in messages:
            prepared.append({"role": msg.role, "content": msg.content})

        return prepared

    def _call_gemini_model(
        self,
        model_id: str,
        messages: List[Dict[str, Any]],
        stream: bool = False,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> tuple[str, Dict[str, Any]]:
        """
        Call Google GenAI model.

        Args:
            model_id: Model ID
            messages: Prepared messages
            stream: Whether to stream the response
            max_tokens: Maximum tokens to generate
            temperature: Temperature for sampling

        Returns:
            Tuple of (response content, usage info)
        """
        if not GENAI_AVAILABLE:
            raise ImportError("google-genai library not available")

        # Configure generation config
        generation_config = {}
        if max_tokens is not None:
            generation_config["max_output_tokens"] = max_tokens
        if temperature is not None:
            generation_config["temperature"] = temperature

        # Get model
        model = genai.GenerativeModel(model_id)

        # Convert messages to Google GenAI format
        google_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                # System messages are handled differently in Google GenAI
                # They are added as system instructions
                model.system_instruction = content
            else:
                google_messages.append({"role": role, "parts": [{"text": content}]})

        # Generate response
        if stream:
            response = model.generate_content(
                google_messages, generation_config=generation_config, stream=True
            )

            # Collect streamed response
            chunks = []
            for chunk in response:
                if chunk.text:
                    chunks.append(chunk.text)

            response_text = "".join(chunks)

            # Usage info not available for streaming
            usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        else:
            response = model.generate_content(google_messages, generation_config=generation_config)

            response_text = response.text

            # Extract usage info if available
            usage = {
                "prompt_tokens": getattr(response, "usage_metadata", {}).get(
                    "prompt_token_count", 0
                ),
                "completion_tokens": getattr(response, "usage_metadata", {}).get(
                    "candidates_token_count", 0
                ),
                "total_tokens": getattr(response, "usage_metadata", {}).get("total_token_count", 0),
            }

        return response_text, usage
