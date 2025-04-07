"""
Context Summarizer module for the Tiered Context Management system.

This module implements progressive summarization techniques with three levels of granularity:
- Detailed Summaries (2:1 to 3:1 compression ratio)
- Condensed Summaries (5:1 to 10:1 compression ratio)
- Topic Summaries (20:1 or higher compression ratio)
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ConversationSegment(BaseModel):
    """Represents a segment of conversation for summarization"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    segment_type: str  # raw, detailed, condensed, topic
    tokens: int
    speakers: List[str]
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = {}


class ContextSummarizer:
    """
    Implements progressive summarization techniques for conversation context.

    The ContextSummarizer is responsible for:
    - Creating detailed summaries (2:1 to 3:1 compression ratio)
    - Creating condensed summaries (5:1 to 10:1 compression ratio)
    - Creating topic summaries (20:1 or higher compression ratio)
    - Calculating relevance between segments and queries
    """

    def __init__(self, openrouter_client=None):
        """
        Initialize the context summarizer.

        Args:
            openrouter_client: Optional OpenRouter client for API access
        """
        self.client = openrouter_client

    async def create_detailed_summary(
        self,
        content: str,
        speakers: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ConversationSegment:
        """
        Create a detailed summary of the content.

        A detailed summary has a 2:1 to 3:1 compression ratio and preserves
        most of the important details from the original content.

        Args:
            content: Content to summarize
            speakers: List of speakers in the content
            metadata: Additional metadata for the summary

        Returns:
            Conversation segment with the detailed summary
        """
        # In a real implementation, this would use the OpenRouter client
        # to generate a summary with the appropriate compression ratio

        # Simulate summarization
        tokens = len(content.split())
        summary_tokens = tokens // 2  # Aim for 2:1 compression
        summary = f"Detailed summary of {tokens} tokens content, compressed to approximately {summary_tokens} tokens."

        return ConversationSegment(
            content=summary,
            segment_type="detailed",
            tokens=summary_tokens,
            speakers=speakers,
            metadata=metadata or {},
        )

    async def create_condensed_summary(
        self,
        content: str,
        speakers: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ConversationSegment:
        """
        Create a condensed summary of the content.

        A condensed summary has a 5:1 to 10:1 compression ratio and focuses
        on the most important points from the original content.

        Args:
            content: Content to summarize
            speakers: List of speakers in the content
            metadata: Additional metadata for the summary

        Returns:
            Conversation segment with the condensed summary
        """
        # In a real implementation, this would use the OpenRouter client
        # to generate a summary with the appropriate compression ratio

        # Simulate summarization
        tokens = len(content.split())
        summary_tokens = tokens // 7  # Aim for 7:1 compression
        summary = f"Condensed summary of {tokens} tokens content, compressed to approximately {summary_tokens} tokens."

        return ConversationSegment(
            content=summary,
            segment_type="condensed",
            tokens=summary_tokens,
            speakers=speakers,
            metadata=metadata or {},
        )

    async def create_topic_summary(
        self,
        content: str,
        speakers: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ConversationSegment:
        """
        Create a topic summary of the content.

        A topic summary has a 20:1 or higher compression ratio and only captures
        the main topics or themes from the original content.

        Args:
            content: Content to summarize
            speakers: List of speakers in the content
            metadata: Additional metadata for the summary

        Returns:
            Conversation segment with the topic summary
        """
        # In a real implementation, this would use the OpenRouter client
        # to generate a summary with the appropriate compression ratio

        # Simulate summarization
        tokens = len(content.split())
        summary_tokens = tokens // 20  # Aim for 20:1 compression
        summary = f"Topic summary of {tokens} tokens content, compressed to approximately {summary_tokens} tokens."

        return ConversationSegment(
            content=summary,
            segment_type="topic",
            tokens=summary_tokens,
            speakers=speakers,
            metadata=metadata or {},
        )

    async def progressive_summarize(
        self,
        content: str,
        speakers: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, ConversationSegment]:
        """
        Create all levels of summaries for the content.

        Args:
            content: Content to summarize
            speakers: List of speakers in the content
            metadata: Additional metadata for the summaries

        Returns:
            Dictionary mapping summary types to conversation segments
        """
        # Create raw segment
        tokens = len(content.split())
        raw_segment = ConversationSegment(
            content=content,
            segment_type="raw",
            tokens=tokens,
            speakers=speakers,
            metadata=metadata or {},
        )

        # Create summaries
        detailed_segment = await self.create_detailed_summary(content, speakers, metadata)
        condensed_segment = await self.create_condensed_summary(content, speakers, metadata)
        topic_segment = await self.create_topic_summary(content, speakers, metadata)

        return {
            "raw": raw_segment,
            "detailed": detailed_segment,
            "condensed": condensed_segment,
            "topic": topic_segment,
        }

    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze a query to extract key information for relevance calculation.

        Args:
            query: Query to analyze

        Returns:
            Dictionary with query analysis
        """
        # In a real implementation, this would use more sophisticated
        # techniques to analyze the query

        # Simple analysis
        words = query.lower().split()
        return {"words": words, "length": len(words)}

    def _calculate_relevance(
        self, segment: ConversationSegment, query_analysis: Dict[str, Any]
    ) -> float:
        """
        Calculate relevance between a segment and a query.

        Args:
            segment: Conversation segment to check
            query_analysis: Analysis of the query

        Returns:
            Relevance score between 0 and 1
        """
        # In a real implementation, this would use more sophisticated
        # techniques to calculate relevance

        # Simple relevance calculation
        content_words = segment.content.lower().split()
        query_words = query_analysis["words"]

        # Count matching words
        matches = sum(1 for word in query_words if word in content_words)

        # Calculate relevance
        if len(query_words) > 0:
            return matches / len(query_words)

        return 0.0

    async def retrieve_relevant_segments(
        self, segments: List[ConversationSegment], query: str, limit: int = 5
    ) -> List[ConversationSegment]:
        """
        Retrieve segments relevant to the query.

        Args:
            segments: List of conversation segments to search
            query: Query to match against segments
            limit: Maximum number of segments to return

        Returns:
            List of relevant segments, sorted by relevance
        """
        # Analyze query
        query_analysis = self._analyze_query(query)

        # Calculate relevance for each segment
        scored_segments = []
        for segment in segments:
            relevance = self._calculate_relevance(segment, query_analysis)
            scored_segments.append((segment, relevance))

        # Sort by relevance (highest first)
        scored_segments.sort(key=lambda x: x[1], reverse=True)

        # Return top segments
        return [segment for segment, _ in scored_segments[:limit]]
