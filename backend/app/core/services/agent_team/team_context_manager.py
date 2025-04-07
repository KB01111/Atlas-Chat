"""
Team Context Manager module for the Agent Team Coordination Framework.

This module implements the team context manager that maintains shared context
across multiple agents and integrates with the Tiered Context Management system.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TeamMessage(BaseModel):
    """Represents a message in the team context"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    thread_id: str
    sender_type: str  # user, assistant, agent, system
    sender_id: Optional[str] = None
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = {}


class TeamContext(BaseModel):
    """Represents the shared context for a team"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    thread_id: str
    messages: List[TeamMessage] = []
    plans: List[Dict[str, Any]] = []
    results: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}


class TeamContextManager:
    """
    Implements the team context manager for the agent team coordination framework.

    The TeamContextManager is responsible for:
    - Maintaining shared context across multiple agents
    - Storing and retrieving conversation history
    - Managing task plans and results
    - Integrating with the Tiered Context Management system
    """

    def __init__(self, tiered_context_manager=None):
        """
        Initialize the team context manager.

        Args:
            tiered_context_manager: Optional tiered context manager for integration
        """
        self.tiered_context_manager = tiered_context_manager
        self.contexts: Dict[str, TeamContext] = {}

    def get_context(self, thread_id: str) -> TeamContext:
        """
        Get or create a team context for a thread.

        Args:
            thread_id: ID of the conversation thread

        Returns:
            Team context for the thread
        """
        if thread_id not in self.contexts:
            self.contexts[thread_id] = TeamContext(thread_id=thread_id)

        return self.contexts[thread_id]

    def add_user_message(
        self, thread_id: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a user message to the team context.

        Args:
            thread_id: ID of the conversation thread
            content: Content of the message
            metadata: Additional metadata for the message

        Returns:
            ID of the added message
        """
        # Get context
        context = self.get_context(thread_id)

        # Create message
        message = TeamMessage(
            thread_id=thread_id,
            sender_type="user",
            content=content,
            metadata=metadata or {},
        )

        # Add to context
        context.messages.append(message)

        # Add to tiered context manager if available
        if self.tiered_context_manager:
            self.tiered_context_manager.add_message(
                session_id=thread_id, message=content, role="user", metadata=metadata
            )

        return message.id

    def add_assistant_message(
        self, thread_id: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add an assistant message to the team context.

        Args:
            thread_id: ID of the conversation thread
            content: Content of the message
            metadata: Additional metadata for the message

        Returns:
            ID of the added message
        """
        # Get context
        context = self.get_context(thread_id)

        # Create message
        message = TeamMessage(
            thread_id=thread_id,
            sender_type="assistant",
            content=content,
            metadata=metadata or {},
        )

        # Add to context
        context.messages.append(message)

        # Add to tiered context manager if available
        if self.tiered_context_manager:
            self.tiered_context_manager.add_message(
                session_id=thread_id,
                message=content,
                role="assistant",
                metadata=metadata,
            )

        return message.id

    def add_agent_message(
        self,
        thread_id: str,
        agent_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add an agent message to the team context.

        Args:
            thread_id: ID of the conversation thread
            agent_id: ID of the agent
            content: Content of the message
            metadata: Additional metadata for the message

        Returns:
            ID of the added message
        """
        # Get context
        context = self.get_context(thread_id)

        # Create message
        message = TeamMessage(
            thread_id=thread_id,
            sender_type="agent",
            sender_id=agent_id,
            content=content,
            metadata=metadata or {},
        )

        # Add to context
        context.messages.append(message)

        return message.id

    def add_system_message(
        self, thread_id: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a system message to the team context.

        Args:
            thread_id: ID of the conversation thread
            content: Content of the message
            metadata: Additional metadata for the message

        Returns:
            ID of the added message
        """
        # Get context
        context = self.get_context(thread_id)

        # Create message
        message = TeamMessage(
            thread_id=thread_id,
            sender_type="system",
            content=content,
            metadata=metadata or {},
        )

        # Add to context
        context.messages.append(message)

        # Add to tiered context manager if available
        if self.tiered_context_manager:
            self.tiered_context_manager.add_message(
                session_id=thread_id, message=content, role="system", metadata=metadata
            )

        return message.id

    def get_conversation_history(
        self, thread_id: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a thread.

        Args:
            thread_id: ID of the conversation thread
            limit: Maximum number of messages to return (most recent first)

        Returns:
            List of messages
        """
        # Get context
        context = self.get_context(thread_id)

        # Get messages
        messages = context.messages

        # Apply limit if specified
        if limit is not None:
            messages = messages[-limit:]

        # Convert to dictionaries
        return [
            {
                "id": message.id,
                "sender_type": message.sender_type,
                "sender_id": message.sender_id,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
                "metadata": message.metadata,
            }
            for message in messages
        ]

    def store_plan(self, thread_id: str, plan: Dict[str, Any]) -> None:
        """
        Store a task plan in the team context.

        Args:
            thread_id: ID of the conversation thread
            plan: Task plan to store
        """
        # Get context
        context = self.get_context(thread_id)

        # Add to plans
        context.plans.append(plan)

    def store_result(self, thread_id: str, result: Dict[str, Any]) -> None:
        """
        Store a task result in the team context.

        Args:
            thread_id: ID of the conversation thread
            result: Task result to store
        """
        # Get context
        context = self.get_context(thread_id)

        # Add to results
        context.results.append(result)

    async def get_context_by_ids(self, context_ids: List[str]) -> str:
        """
        Get context by IDs.

        Args:
            context_ids: List of context IDs

        Returns:
            Combined context as string
        """
        # In a real implementation, this would retrieve specific
        # context elements by their IDs

        # Simulate context retrieval
        return f"Context for IDs: {', '.join(context_ids)}"

    async def get_relevant_context(
        self, thread_id: str, query: str, limit: int = 5
    ) -> str:
        """
        Get context relevant to a query.

        Args:
            thread_id: ID of the conversation thread
            query: Query to match against context
            limit: Maximum number of context elements to return

        Returns:
            Relevant context as string
        """
        # Use tiered context manager if available
        if self.tiered_context_manager:
            context_bundle = await self.tiered_context_manager.retrieve_context(
                session_id=thread_id, query=query
            )

            return self.tiered_context_manager.format_context_for_prompt(context_bundle)

        # Fallback to simple context retrieval
        context = self.get_context(thread_id)

        # Get recent messages
        messages = context.messages[-limit:]

        # Format context
        formatted_context = []
        for message in messages:
            if message.sender_type == "user":
                formatted_context.append(f"User: {message.content}")
            elif message.sender_type == "assistant":
                formatted_context.append(f"Assistant: {message.content}")
            elif message.sender_type == "agent":
                formatted_context.append(
                    f"Agent ({message.sender_id}): {message.content}"
                )
            elif message.sender_type == "system":
                formatted_context.append(f"System: {message.content}")

        return "\n\n".join(formatted_context)

    def clear_context(self, thread_id: str) -> bool:
        """
        Clear the team context for a thread.

        Args:
            thread_id: ID of the conversation thread

        Returns:
            True if successful, False otherwise
        """
        if thread_id in self.contexts:
            del self.contexts[thread_id]

            # Clear in tiered context manager if available
            if self.tiered_context_manager:
                self.tiered_context_manager.end_session(thread_id)

            return True

        return False
