"""
Atlas Integration module for connecting all components.

This module implements the central integration point that connects
the Tiered Context Management system and Agent Team Coordination framework
with the existing Atlas-Chat components.
"""

import logging
from typing import Any, Dict

from ..agent_team import AgentTeamManager
from ..model_routing import ModelRouter
from ..tiered_context import TieredContextManager

logger = logging.getLogger(__name__)


class AtlasIntegration:
    """
    Implements the central integration point for all components.

    The AtlasIntegration is responsible for:
    - Connecting the Tiered Context Management system with the Agent Team Coordination framework
    - Providing a unified interface for the API layer
    - Supporting both single-agent and multi-agent processing
    - Managing context sharing between components
    """

    def __init__(self, openai_client=None):
        """
        Initialize the Atlas integration.

        Args:
            openai_client: Optional OpenAI client for API access
        """
        self.client = openai_client

        # Initialize components
        self.context_manager = TieredContextManager(openai_client=self.client)
        self.team_manager = AgentTeamManager(openai_client=self.client)
        self.model_router = ModelRouter()

        # Connect components
        self.team_manager.context_manager.tiered_context_manager = self.context_manager

    async def process_message(
        self, session_id: str, message: str, use_team: bool = False
    ) -> Dict[str, Any]:
        """
        Process a user message using the integrated components.

        Args:
            session_id: ID of the conversation session
            message: User message to process
            use_team: Whether to use the agent team for processing

        Returns:
            Dictionary with processing results
        """
        # Add message to context manager
        self.context_manager.add_message(session_id=session_id, message=message, role="user")

        # Process with agent team if requested
        if use_team:
            result = await self.team_manager.process_request(
                thread_id=session_id, user_request=message
            )

            return {
                "response": result["synthesis"]["content"],
                "format": result["synthesis"]["format"],
                "metadata": {"processing_type": "team", "plan_id": result["plan_id"]},
            }

        # Otherwise, process with single agent
        else:
            # Get context
            context_bundle = await self.context_manager.retrieve_context(
                session_id=session_id, query=message
            )

            # Format context for prompt
            formatted_context = self.context_manager.format_context_for_prompt(context_bundle)

            # Select model
            model = self.model_router.select_model(query=message, context=formatted_context)

            # In a real implementation, this would use the selected model
            # to generate a response

            # Simulate response generation
            response = f"Response to: {message}\n\nUsed context: {len(formatted_context)} characters\n\nGenerated using model: {model}"

            # Add response to context manager
            self.context_manager.add_message(
                session_id=session_id, message=response, role="assistant"
            )

            return {
                "response": response,
                "format": "text",
                "metadata": {"processing_type": "single", "model": model},
            }

    async def process_message_with_agent(
        self, session_id: str, message: str, agent_type: str
    ) -> Dict[str, Any]:
        """
        Process a user message using a specific agent type.

        Args:
            session_id: ID of the conversation session
            message: User message to process
            agent_type: Type of agent to use

        Returns:
            Dictionary with processing results
        """
        # Add message to context manager
        await self.context_manager.add_message(session_id=session_id, message=message, role="user")

        # Get agents of the specified type
        agents = self.team_manager.get_agents_by_type(agent_type)
        if not agents:
            raise ValueError(f"No agents found of type: {agent_type}")

        # Use the first agent of the specified type
        agent = agents[0]

        # Process with the agent
        result = await self.team_manager.process_request_with_agent(
            thread_id=session_id, user_request=message, agent_id=agent.agent_id
        )

        return {
            "response": result["result"]["content"],
            "format": result["result"]["format"],
            "metadata": {
                "processing_type": "agent",
                "agent_id": result["agent_id"],
                "agent_type": agent_type,
            },
        }

    def end_session(self, session_id: str) -> bool:
        """
        End a conversation session.

        Args:
            session_id: ID of the session to end

        Returns:
            True if successful, False otherwise
        """
        # End session in context manager
        context_result = self.context_manager.end_session(session_id)

        # End session in team manager
        team_result = self.team_manager.context_manager.clear_context(session_id)

        return context_result and team_result
