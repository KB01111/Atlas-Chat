"""
Working Memory module for the Tiered Context Management system.

This module implements the short-term, high-fidelity memory component
that stores recent interactions in full detail.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import uuid
import logging
from pydantic import BaseModel, Field

from .context_summarizer import ConversationSegment

logger = logging.getLogger(__name__)


class WorkingMemoryEntry(BaseModel):
    """Represents an entry in working memory"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    content: str
    role: str  # user, assistant, system
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}


class WorkingMemory:
    """
    Implements the short-term, high-fidelity memory component.

    The WorkingMemory is responsible for:
    - Storing recent interactions in full detail
    - Managing memory expiration based on time or capacity
    - Providing quick access to recent context
    """

    def __init__(self, max_entries: int = 50, ttl_minutes: int = 60):
        """
        Initialize the working memory.

        Args:
            max_entries: Maximum number of entries to store
            ttl_minutes: Time-to-live in minutes for entries
        """
        self.max_entries = max_entries
        self.ttl_minutes = ttl_minutes
        self.entries: Dict[str, WorkingMemoryEntry] = {}
        self.session_entries: Dict[
            str, List[str]
        ] = {}  # session_id -> list of entry_ids

    def add_entry(
        self,
        session_id: str,
        content: str,
        role: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add an entry to working memory.

        Args:
            session_id: ID of the conversation session
            content: Content of the entry
            role: Role of the speaker (user, assistant, system)
            metadata: Additional metadata for the entry

        Returns:
            ID of the added entry
        """
        # Create entry
        entry = WorkingMemoryEntry(
            session_id=session_id,
            content=content,
            role=role,
            expires_at=datetime.now() + timedelta(minutes=self.ttl_minutes),
            metadata=metadata or {},
        )

        # Store entry
        self.entries[entry.id] = entry

        # Add to session entries
        if session_id not in self.session_entries:
            self.session_entries[session_id] = []
        self.session_entries[session_id].append(entry.id)

        # Enforce capacity limit
        self._enforce_capacity_limit(session_id)

        return entry.id

    def get_entry(self, entry_id: str) -> Optional[WorkingMemoryEntry]:
        """
        Get an entry by ID.

        Args:
            entry_id: ID of the entry to retrieve

        Returns:
            The entry or None if not found or expired
        """
        entry = self.entries.get(entry_id)

        if entry and self._is_expired(entry):
            # Remove expired entry
            self._remove_entry(entry_id)
            return None

        return entry

    def get_session_entries(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[WorkingMemoryEntry]:
        """
        Get entries for a session.

        Args:
            session_id: ID of the session
            limit: Maximum number of entries to return (most recent first)

        Returns:
            List of entries
        """
        # Clean expired entries
        self._clean_expired_entries()

        # Get entry IDs for the session
        entry_ids = self.session_entries.get(session_id, [])

        # Apply limit if specified
        if limit is not None:
            entry_ids = entry_ids[-limit:]

        # Get entries
        entries = []
        for entry_id in entry_ids:
            entry = self.get_entry(entry_id)
            if entry:
                entries.append(entry)

        return entries

    def get_conversation_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> str:
        """
        Get conversation history for a session.

        Args:
            session_id: ID of the session
            limit: Maximum number of entries to include

        Returns:
            Conversation history as string
        """
        entries = self.get_session_entries(session_id, limit)

        # Format conversation
        conversation = []
        for entry in entries:
            if entry.role == "user":
                conversation.append(f"User: {entry.content}")
            elif entry.role == "assistant":
                conversation.append(f"Assistant: {entry.content}")
            elif entry.role == "system":
                conversation.append(f"System: {entry.content}")

        return "\n\n".join(conversation)

    def clear_session(self, session_id: str) -> None:
        """
        Clear all entries for a session.

        Args:
            session_id: ID of the session to clear
        """
        # Get entry IDs for the session
        entry_ids = self.session_entries.get(session_id, [])

        # Remove entries
        for entry_id in entry_ids:
            if entry_id in self.entries:
                del self.entries[entry_id]

        # Clear session entries
        self.session_entries[session_id] = []

    def _is_expired(self, entry: WorkingMemoryEntry) -> bool:
        """
        Check if an entry is expired.

        Args:
            entry: Entry to check

        Returns:
            True if expired, False otherwise
        """
        if entry.expires_at and entry.expires_at < datetime.now():
            return True

        return False

    def _remove_entry(self, entry_id: str) -> None:
        """
        Remove an entry.

        Args:
            entry_id: ID of the entry to remove
        """
        if entry_id in self.entries:
            entry = self.entries[entry_id]

            # Remove from entries
            del self.entries[entry_id]

            # Remove from session entries
            session_id = entry.session_id
            if session_id in self.session_entries:
                if entry_id in self.session_entries[session_id]:
                    self.session_entries[session_id].remove(entry_id)

    def _clean_expired_entries(self) -> None:
        """Clean expired entries"""
        # Get expired entry IDs
        expired_ids = []
        for entry_id, entry in self.entries.items():
            if self._is_expired(entry):
                expired_ids.append(entry_id)

        # Remove expired entries
        for entry_id in expired_ids:
            self._remove_entry(entry_id)

    def _enforce_capacity_limit(self, session_id: str) -> None:
        """
        Enforce capacity limit for a session.

        Args:
            session_id: ID of the session
        """
        # Get entry IDs for the session
        entry_ids = self.session_entries.get(session_id, [])

        # Check if over capacity
        if len(entry_ids) > self.max_entries:
            # Remove oldest entries
            excess = len(entry_ids) - self.max_entries
            for i in range(excess):
                if i < len(entry_ids):
                    self._remove_entry(entry_ids[i])

    def to_conversation_segments(self, session_id: str) -> List[ConversationSegment]:
        """
        Convert session entries to conversation segments.

        Args:
            session_id: ID of the session

        Returns:
            List of conversation segments
        """
        entries = self.get_session_entries(session_id)

        segments = []
        for entry in entries:
            # Create segment
            segment = ConversationSegment(
                content=entry.content,
                segment_type="raw",
                tokens=len(entry.content.split()),
                speakers=[entry.role],
                metadata=entry.metadata,
            )
            segments.append(segment)

        return segments
