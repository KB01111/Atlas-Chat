"""
Episodic Memory module for the Tiered Context Management system.

This module implements the medium-term memory component that stores
conversation history with progressive summarization.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import uuid
import logging
from pydantic import BaseModel, Field

from .context_summarizer import ConversationSegment, ContextSummarizer

logger = logging.getLogger(__name__)

class EpisodeEntry(BaseModel):
    """Represents an episode entry in episodic memory"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    raw_content: str
    detailed_summary: Optional[str] = None
    condensed_summary: Optional[str] = None
    topic_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}

class EpisodicMemory:
    """
    Implements the medium-term memory component with progressive summarization.

    The EpisodicMemory is responsible for:
    - Storing conversation episodes with progressive summarization
    - Managing memory expiration based on time
    - Providing access to conversation history at different levels of detail
    """

    def __init__(self, context_summarizer: Optional[ContextSummarizer] = None, 
                ttl_days: int = 30):
        """
        Initialize the episodic memory.

        Args:
            context_summarizer: Summarizer for creating progressive summaries
            ttl_days: Time-to-live in days for entries
        """
        self.context_summarizer = context_summarizer or ContextSummarizer()
        self.ttl_days = ttl_days
        self.episodes: Dict[str, EpisodeEntry] = {}
        self.session_episodes: Dict[str, List[str]] = {}  # session_id -> list of episode_ids

    async def add_episode(self, session_id: str, content: str, speakers: List[str],
                        metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add an episode to episodic memory with progressive summarization.

        Args:
            session_id: ID of the conversation session
            content: Content of the episode
            speakers: List of speakers in the episode
            metadata: Additional metadata for the episode

        Returns:
            ID of the added episode
        """
        # Create summaries
        summaries = await self.context_summarizer.progressive_summarize(
            content=content,
            speakers=speakers,
            metadata=metadata
        )

        # Create episode
        episode = EpisodeEntry(
            session_id=session_id,
            raw_content=content,
            detailed_summary=summaries["detailed"].content,
            condensed_summary=summaries["condensed"].content,
            topic_summary=summaries["topic"].content,
            expires_at=datetime.now() + timedelta(days=self.ttl_days),
            metadata=metadata or {}
        )

        # Store episode
        self.episodes[episode.id] = episode

        # Add to session episodes
        if session_id not in self.session_episodes:
            self.session_episodes[session_id] = []
        self.session_episodes[session_id].append(episode.id)

        return episode.id

    def get_episode(self, episode_id: str) -> Optional[EpisodeEntry]:
        """
        Get an episode by ID.

        Args:
            episode_id: ID of the episode to retrieve

        Returns:
            The episode or None if not found or expired
        """
        episode = self.episodes.get(episode_id)

        if episode and self._is_expired(episode):
            # Remove expired episode
            self._remove_episode(episode_id)
            return None

        return episode

    def get_session_episodes(self, session_id: str, 
                           summary_level: str = "detailed") -> List[Dict[str, Any]]:
        """
        Get episodes for a session at the specified summary level.

        Args:
            session_id: ID of the session
            summary_level: Level of summary to return (raw, detailed, condensed, topic)

        Returns:
            List of episodes with content at the specified summary level
        """
        # Clean expired episodes
        self._clean_expired_episodes()

        # Get episode IDs for the session
        episode_ids = self.session_episodes.get(session_id, [])

        # Get episodes
        episodes = []
        for episode_id in episode_ids:
            episode = self.get_episode(episode_id)
            if episode:
                # Get content based on summary level
                if summary_level == "raw":
                    content = episode.raw_content
                elif summary_level == "detailed":
                    content = episode.detailed_summary or episode.raw_content
                elif summary_level == "condensed":
                    content = episode.condensed_summary or episode.detailed_summary or episode.raw_content
                elif summary_level == "topic":
                    content = episode.topic_summary or episode.condensed_summary or episode.detailed_summary or episode.raw_content
                else:
                    content = episode.detailed_summary or episode.raw_content

                episodes.append({
                    "id": episode.id,
                    "content": content,
                    "created_at": episode.created_at,
                    "metadata": episode.metadata
                })

        return episodes

    async def retrieve_relevant_episodes(self, session_id: str, query: str, 
                                      limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve episodes relevant to the query.

        Args:
            session_id: ID of the session
            query: Query to match against episodes
            limit: Maximum number of episodes to return

        Returns:
            List of relevant episodes
        """
        # Get all episodes for the session
        episodes = self.get_session_episodes(session_id, "condensed")

        # Convert to conversation segments for relevance calculation
        segments = []
        for episode in episodes:
            segment = ConversationSegment(
                content=episode["content"],
                segment_type="condensed",
                tokens=len(episode["content"].split()),
                speakers=["user", "assistant"],  # Simplified
                metadata=episode["metadata"]
            )
            segments.append((segment, episode))

        # Retrieve relevant segments
        relevant_segments = await self.context_summarizer.retrieve_relevant_segments(
            segments=[s for s, _ in segments],
            query=query,
            limit=limit
        )

        # Map back to episodes
        segment_map = {s.id: e for s, e in segments}
        relevant_episodes = [segment_map[s.id] for s in relevant_segments if s.id in segment_map]

        return relevant_episodes

    def clear_session(self, session_id: str) -> None:
        """
        Clear all episodes for a session.

        Args:
            session_id: ID of the session to clear
        """
        # Get episode IDs for the session
        episode_ids = self.session_episodes.get(session_id, [])

        # Remove episodes
        for episode_id in episode_ids:
            if episode_id in self.episodes:
                del self.episodes[episode_id]

        # Clear session episodes
        self.session_episodes[session_id] = []

    def _is_expired(self, episode: EpisodeEntry) -> bool:
        """
        Check if an episode is expired.

        Args:
            episode: Episode to check

        Returns:
            True if expired, False otherwise
        """
        if episode.expires_at and episode.expires_at < datetime.now():
            return True

        return False

    def _remove_episode(self, episode_id: str) -> None:
        """
        Remove an episode.

        Args:
            episode_id: ID of the episode to remove
        """
        if episode_id in self.episodes:
            episode = self.episodes[episode_id]

            # Remove from episodes
            del self.episodes[episode_id]

            # Remove from session episodes
            session_id = episode.session_id
            if session_id in self.session_episodes:
                if episode_id in self.session_episodes[session_id]:
                    self.session_episodes[session_id].remove(episode_id)

    def _clean_expired_episodes(self) -> None:
        """Clean expired episodes"""
        # Get expired episode IDs
        expired_ids = []
        for episode_id, episode in self.episodes.items():
            if self._is_expired(episode):
                expired_ids.append(episode_id)

        # Remove expired episodes
        for episode_id in expired_ids:
            self._remove_episode(episode_id)
