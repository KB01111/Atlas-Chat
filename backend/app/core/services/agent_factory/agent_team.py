"""
Agent team module for creating and managing agent teams.
"""

from typing import Dict, Any, List, Optional, Set
from pydantic import BaseModel, Field
import logging
import uuid

from .agent_definition import AgentDefinition

logger = logging.getLogger(__name__)


class TeamMember(BaseModel):
    """Team member definition."""

    agent_id: str
    role: str
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""

        schema_extra = {
            "example": {
                "agent_id": "agent_123456",
                "role": "researcher",
                "description": "Responsible for gathering information"
            }
        }


class AgentTeam(BaseModel):
    """Definition for an agent team."""

    team_id: Optional[str] = Field(default_factory=lambda: f"team_{str(uuid.uuid4())}")
    name: str
    description: str
    members: List[TeamMember] = []
    coordinator_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""

        schema_extra = {
            "example": {
                "name": "Research Team",
                "description": "Team for comprehensive research tasks",
                "members": [
                    {
                        "agent_id": "agent_123456",
                        "role": "researcher",
                        "description": "Responsible for gathering information"
                    },
                    {
                        "agent_id": "agent_789012",
                        "role": "writer",
                        "description": "Responsible for writing reports"
                    }
                ],
                "coordinator_id": "agent_345678"
            }
        }


class TeamRegistry:
    """Registry for agent teams."""

    def __init__(self):
        """Initialize team registry."""
        self.teams: Dict[str, AgentTeam] = {}

    def register_team(self, team: AgentTeam) -> str:
        """
        Register a team.

        Args:
            team: Agent team

        Returns:
            Team ID
        """
        team_id = team.team_id or f"team_{str(uuid.uuid4())}"
        team.team_id = team_id
        self.teams[team_id] = team
        logger.info(f"Registered agent team: {team.name} ({team_id})")
        return team_id

    def get_team(self, team_id: str) -> Optional[AgentTeam]:
        """
        Get a team by ID.

        Args:
            team_id: Team ID

        Returns:
            Agent team or None if not found
        """
        return self.teams.get(team_id)

    def get_all_teams(self) -> Dict[str, AgentTeam]:
        """
        Get all teams.

        Returns:
            Dictionary of teams
        """
        return self.teams

    def get_team_ids(self) -> Set[str]:
        """
        Get all team IDs.

        Returns:
            Set of team IDs
        """
        return set(self.teams.keys())

    def update_team(self, team_id: str, updates: Dict[str, Any]) -> Optional[AgentTeam]:
        """
        Update a team.

        Args:
            team_id: Team ID
            updates: Updates to apply

        Returns:
            Updated team or None if not found
        """
        if team_id not in self.teams:
            return None

        # Get current team
        current = self.teams[team_id]

        # Apply updates
        updated_dict = current.dict()
        updated_dict.update(updates)

        # Create new team
        updated = AgentTeam(**updated_dict)

        # Update teams
        self.teams[team_id] = updated

        return updated

    def delete_team(self, team_id: str) -> bool:
        """
        Delete a team.

        Args:
            team_id: Team ID

        Returns:
            True if successful, False otherwise
        """
        if team_id not in self.teams:
            return False

        del self.teams[team_id]
        return True

    def add_member(self, team_id: str, member: TeamMember) -> bool:
        """
        Add a member to a team.

        Args:
            team_id: Team ID
            member: Team member

        Returns:
            True if successful, False otherwise
        """
        if team_id not in self.teams:
            return False

        # Get current team
        current = self.teams[team_id]

        # Add member
        members = current.members.copy()
        members.append(member)

        # Update team
        updated = self.update_team(team_id, {"members": members})

        return updated is not None

    def remove_member(self, team_id: str, agent_id: str) -> bool:
        """
        Remove a member from a team.

        Args:
            team_id: Team ID
            agent_id: Agent ID

        Returns:
            True if successful, False otherwise
        """
        if team_id not in self.teams:
            return False

        # Get current team
        current = self.teams[team_id]

        # Remove member
        members = [m for m in current.members if m.agent_id != agent_id]

        # Update team
        updated = self.update_team(team_id, {"members": members})

        return updated is not None
