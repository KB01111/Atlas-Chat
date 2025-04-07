"""
Agent memory module for persistent agent memory.
"""

import datetime
import logging
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MemoryEntry(BaseModel):
    """Memory entry for an agent."""

    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""

        schema_extra = {
            "example": {
                "agent_id": "agent_123456",
                "content": "User asked about quantum computing",
                "metadata": {"importance": "high", "category": "user_interest"},
            }
        }


class AgentMemory:
    """Memory for an agent."""

    def __init__(self, agent_id: str, max_entries: int = 100):
        """
        Initialize agent memory.

        Args:
            agent_id: Agent ID
            max_entries: Maximum number of memory entries
        """
        self.agent_id = agent_id
        self.max_entries = max_entries
        self.entries: List[MemoryEntry] = []

    def add_entry(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a memory entry.

        Args:
            content: Entry content
            metadata: Entry metadata

        Returns:
            Entry ID
        """
        # Create entry
        entry = MemoryEntry(
            agent_id=self.agent_id, content=content, metadata=metadata or {}
        )

        # Add entry
        self.entries.append(entry)

        # Trim if necessary
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries :]

        return entry.entry_id

    def get_entry(self, entry_id: str) -> Optional[MemoryEntry]:
        """
        Get a memory entry.

        Args:
            entry_id: Entry ID

        Returns:
            Memory entry or None if not found
        """
        for entry in self.entries:
            if entry.entry_id == entry_id:
                return entry

        return None

    def get_entries(self, limit: Optional[int] = None) -> List[MemoryEntry]:
        """
        Get memory entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of memory entries
        """
        if limit is None:
            return self.entries

        return self.entries[-limit:]

    def search_entries(self, query: str) -> List[MemoryEntry]:
        """
        Search memory entries.

        Args:
            query: Search query

        Returns:
            List of matching memory entries
        """
        # Simple substring search for now
        return [
            entry for entry in self.entries if query.lower() in entry.content.lower()
        ]

    def clear(self):
        """Clear all memory entries."""
        self.entries = []

    def to_context_string(self, limit: Optional[int] = None) -> str:
        """
        Convert memory to a context string.

        Args:
            limit: Maximum number of entries to include

        Returns:
            Context string
        """
        entries = self.get_entries(limit)

        # Format entries
        formatted = []
        for entry in entries:
            timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            formatted.append(f"[{timestamp}] {entry.content}")

        return "\n".join(formatted)


class MemoryManager:
    """Manager for agent memories."""

    def __init__(self):
        """Initialize memory manager."""
        self.memories: Dict[str, AgentMemory] = {}

    def get_memory(self, agent_id: str) -> AgentMemory:
        """
        Get memory for an agent.

        Args:
            agent_id: Agent ID

        Returns:
            Agent memory
        """
        if agent_id not in self.memories:
            self.memories[agent_id] = AgentMemory(agent_id)

        return self.memories[agent_id]

    def add_entry(
        self, agent_id: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a memory entry for an agent.

        Args:
            agent_id: Agent ID
            content: Entry content
            metadata: Entry metadata

        Returns:
            Entry ID
        """
        memory = self.get_memory(agent_id)
        return memory.add_entry(content, metadata)

    def get_entries(
        self, agent_id: str, limit: Optional[int] = None
    ) -> List[MemoryEntry]:
        """
        Get memory entries for an agent.

        Args:
            agent_id: Agent ID
            limit: Maximum number of entries to return

        Returns:
            List of memory entries
        """
        memory = self.get_memory(agent_id)
        return memory.get_entries(limit)

    def search_entries(self, agent_id: str, query: str) -> List[MemoryEntry]:
        """
        Search memory entries for an agent.

        Args:
            agent_id: Agent ID
            query: Search query

        Returns:
            List of matching memory entries
        """
        memory = self.get_memory(agent_id)
        return memory.search_entries(query)

    def clear_memory(self, agent_id: str):
        """
        Clear memory for an agent.

        Args:
            agent_id: Agent ID
        """
        if agent_id in self.memories:
            self.memories[agent_id].clear()

    def delete_memory(self, agent_id: str):
        """
        Delete memory for an agent.

        Args:
            agent_id: Agent ID
        """
        if agent_id in self.memories:
            del self.memories[agent_id]
