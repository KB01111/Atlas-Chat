"""
Context Manager module for the Tiered Context Management system.

This module implements the main context manager that coordinates all memory tiers
and provides context retrieval based on query relevance.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from .context_summarizer import ContextSummarizer
from .episodic_memory import EpisodicMemory
from .knowledge_graph import KnowledgeGraph
from .working_memory import WorkingMemory

logger = logging.getLogger(__name__)


class ContextBundle(BaseModel):
    """Represents a bundle of context from different memory tiers"""

    working_memory: List[Dict[str, Any]] = []
    episodic_memory: List[Dict[str, Any]] = []
    knowledge_graph: List[Dict[str, Any]] = []
    total_tokens: int = 0
    metadata: Dict[str, Any] = {}


class TieredContextManager:
    """
    Main context manager that coordinates all memory tiers.

    The TieredContextManager is responsible for:
    - Coordinating working memory, episodic memory, and knowledge graph
    - Adding and retrieving messages from appropriate tiers
    - Retrieving context based on query relevance
    - Managing context window size
    """

    def __init__(self, max_context_tokens: int = 8000, openrouter_client=None):
        """
        Initialize the tiered context manager.

        Args:
            max_context_tokens: Maximum number of tokens in context window
            openrouter_client: Optional OpenRouter client for API access
        """
        self.max_context_tokens = max_context_tokens
        self.client = openrouter_client

        # Initialize components
        self.context_summarizer = ContextSummarizer(openrouter_client=self.client)
        self.working_memory = WorkingMemory()
        self.episodic_memory = EpisodicMemory(
            context_summarizer=self.context_summarizer
        )
        self.knowledge_graph = KnowledgeGraph(openrouter_client=self.client)

        # Initialize active sessions
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    async def add_message(
        self,
        session_id: str,
        message: str,
        role: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add a message to the context manager.

        Args:
            session_id: ID of the conversation session
            message: Message content
            role: Role of the speaker (user, assistant, system)
            metadata: Additional metadata for the message

        Returns:
            ID of the added message
        """
        # Update session info
        self._update_session_info(session_id, message)

        # Add to working memory
        message_id = self.working_memory.add_entry(
            session_id=session_id, content=message, role=role, metadata=metadata
        )

        # Process for episodic memory if appropriate
        # In a real implementation, this would use more sophisticated
        # logic to determine when to create episodes
        if len(message) > 100:
            # Get recent messages for context
            recent_messages = self.working_memory.get_conversation_history(
                session_id, limit=5
            )

            # Add to episodic memory
            await self.episodic_memory.add_episode(
                session_id=session_id,
                content=f"{recent_messages}\n\n{role}: {message}",
                speakers=[role],
                metadata=metadata,
            )

        # Extract knowledge if appropriate
        if role == "assistant" and len(message) > 200:
            await self.knowledge_graph.extract_knowledge(
                content=message, session_id=session_id
            )

        return message_id

    async def retrieve_context(
        self, session_id: str, query: str, depth: int = 2
    ) -> ContextBundle:
        """
        Retrieve context based on query relevance.

        Args:
            session_id: ID of the conversation session
            query: Query to match against context
            depth: Depth of context retrieval (1=shallow, 2=medium, 3=deep)

        Returns:
            Bundle of context from different memory tiers
        """
        # Initialize context bundle
        context_bundle = ContextBundle()

        # Get working memory entries
        working_memory_limit = 10 if depth == 1 else (20 if depth == 2 else 30)
        working_memory_entries = self.working_memory.get_session_entries(
            session_id=session_id, limit=working_memory_limit
        )

        # Add to context bundle
        context_bundle.working_memory = [
            {
                "id": entry.id,
                "content": entry.content,
                "role": entry.role,
                "created_at": entry.created_at.isoformat(),
                "metadata": entry.metadata,
            }
            for entry in working_memory_entries
        ]

        # Update token count
        context_bundle.total_tokens += sum(
            len(entry.content.split()) for entry in working_memory_entries
        )

        # Check if we need more context
        if context_bundle.total_tokens < self.max_context_tokens:
            # Get episodic memory entries
            episodic_memory_limit = 3 if depth == 1 else (5 if depth == 2 else 10)
            episodic_memory_entries = (
                await self.episodic_memory.retrieve_relevant_episodes(
                    session_id=session_id, query=query, limit=episodic_memory_limit
                )
            )

            # Add to context bundle
            context_bundle.episodic_memory = episodic_memory_entries

            # Update token count
            context_bundle.total_tokens += sum(
                len(entry["content"].split()) for entry in episodic_memory_entries
            )

        # Check if we need more context
        if context_bundle.total_tokens < self.max_context_tokens:
            # Get knowledge graph nodes
            knowledge_limit = 2 if depth == 1 else (3 if depth == 2 else 5)
            knowledge_nodes = await self.knowledge_graph.search_nodes(
                query=query, limit=knowledge_limit
            )

            # Add to context bundle
            context_bundle.knowledge_graph = [
                {
                    "id": node.id,
                    "label": node.label,
                    "content": node.content,
                    "node_type": node.node_type,
                    "created_at": node.created_at.isoformat(),
                    "metadata": node.metadata,
                }
                for node in knowledge_nodes
            ]

            # Update token count
            context_bundle.total_tokens += sum(
                len(node.content.split()) for node in knowledge_nodes
            )

        return context_bundle

    async def format_context_for_prompt(self, context_bundle: ContextBundle) -> str:
        """
        Format context bundle for use in a prompt.

        Args:
            context_bundle: Bundle of context from different memory tiers

        Returns:
            Formatted context string
        """
        context_parts = []

        # Add working memory
        if context_bundle.working_memory:
            working_memory_str = "## Recent Conversation\n\n"
            for entry in context_bundle.working_memory:
                role_display = (
                    "User"
                    if entry["role"] == "user"
                    else "Assistant" if entry["role"] == "assistant" else "System"
                )
                working_memory_str += f"{role_display}: {entry['content']}\n\n"
            context_parts.append(working_memory_str)

        # Add episodic memory
        if context_bundle.episodic_memory:
            episodic_memory_str = "## Related Conversation History\n\n"
            for entry in context_bundle.episodic_memory:
                episodic_memory_str += f"{entry['content']}\n\n"
            context_parts.append(episodic_memory_str)

        # Add knowledge graph
        if context_bundle.knowledge_graph:
            knowledge_graph_str = "## Relevant Knowledge\n\n"
            for node in context_bundle.knowledge_graph:
                knowledge_graph_str += f"- {node['label']}: {node['content']}\n\n"
            context_parts.append(knowledge_graph_str)

        return "\n\n".join(context_parts)

    async def end_session(self, session_id: str) -> bool:
        """
        End a conversation session.

        Args:
            session_id: ID of the session to end

        Returns:
            True if successful, False otherwise
        """
        try:
            # Clear working memory
            self.working_memory.clear_session(session_id)

            # Clear episodic memory
            await self.episodic_memory.clear_session(session_id)

            # Clear knowledge graph
            await self.knowledge_graph.clear_session(session_id)

            # Remove from active sessions
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

            return True
        except Exception as e:
            logger.error(f"Error ending session {session_id}: {e}")
            return False

    def _update_session_info(self, session_id: str, message: str) -> None:
        """
        Update session information.

        Args:
            session_id: ID of the session
            message: Latest message
        """
        # Create session if not exists
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "message_count": 0,
                "title": f"Conversation {session_id[:8]}",
            }

        # Update session
        self.active_sessions[session_id]["last_updated"] = datetime.now().isoformat()
        self.active_sessions[session_id]["message_count"] += 1

        # Update title if first user message
        if self.active_sessions[session_id]["message_count"] <= 2 and len(message) > 10:
            self.active_sessions[session_id]["title"] = message[:50] + (
                "..." if len(message) > 50 else ""
            )
