"""
Agent Team Coordination package for Atlas-Chat.

This package provides the necessary components for implementing
agent team coordination and multi-agent collaboration.
"""

from .coordinator_agent import CoordinatorAgent
from .specialized_agent import (
    AnalysisAgent,
    CoderAgent,
    ResearchAgent,
    SpecializedAgent,
    WritingAgent,
)
from .task_executor import TaskExecutor, TaskStatus
from .team_context_manager import TeamContext, TeamContextManager, TeamMessage
from .team_manager import AgentTeamManager

__all__ = [
    "CoordinatorAgent",
    "SpecializedAgent",
    "ResearchAgent",
    "CoderAgent",
    "WritingAgent",
    "AnalysisAgent",
    "AgentTeamManager",
    "TaskExecutor",
    "TaskStatus",
    "TeamContextManager",
    "TeamMessage",
    "TeamContext",
]
