"""
Agent specialization module for specialized agent capabilities.
"""

from typing import Dict, Any, List, Optional, Set
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class AgentSpecialization(BaseModel):
    """Specialization for an agent."""

    name: str
    description: str
    capabilities: List[str]
    system_prompt_template: str
    tools: List[str] = []
    recommended_models: List[str] = []
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""

        schema_extra = {
            "example": {
                "name": "research",
                "description": "Specialization for research tasks",
                "capabilities": ["web search", "information synthesis", "citation"],
                "system_prompt_template": "You are a research expert that helps find and analyze information. {additional_instructions}",
                "tools": ["search_web", "search_graphiti"],
                "recommended_models": ["claude-3-5-sonnet", "gpt-4o", "gemini-2-5-pro"]
            }
        }


class SpecializationRegistry:
    """Registry for agent specializations."""

    def __init__(self):
        """Initialize specialization registry."""
        self.specializations: Dict[str, AgentSpecialization] = {}
        self._load_default_specializations()

    def _load_default_specializations(self):
        """Load default specializations."""
        defaults = [
            AgentSpecialization(
                name="research",
                description="Specialization for research tasks",
                capabilities=["web search", "information synthesis", "citation"],
                system_prompt_template="You are a research expert that helps find and analyze information. {additional_instructions}",
                tools=["search_web", "search_graphiti"],
                recommended_models=["claude-3-5-sonnet", "gpt-4o", "gemini-2-5-pro"]
            ),
            AgentSpecialization(
                name="coding",
                description="Specialization for coding tasks",
                capabilities=["code generation", "code explanation", "debugging"],
                system_prompt_template="You are a coding expert that helps write, explain, and debug code. {additional_instructions}",
                tools=["execute_code", "search_documentation"],
                recommended_models=["claude-3-7-sonnet", "gpt-4o", "gemini-2-5-pro", "deepseek-coder"]
            ),
            AgentSpecialization(
                name="writing",
                description="Specialization for writing tasks",
                capabilities=["content creation", "editing", "summarization"],
                system_prompt_template="You are a writing expert that helps create, edit, and improve written content. {additional_instructions}",
                tools=["check_grammar", "search_web"],
                recommended_models=["claude-3-opus", "gpt-4-5-preview", "gemini-2-5-pro"]
            ),
            AgentSpecialization(
                name="data_analysis",
                description="Specialization for data analysis tasks",
                capabilities=["data processing", "visualization", "statistical analysis"],
                system_prompt_template="You are a data analysis expert that helps process, visualize, and analyze data. {additional_instructions}",
                tools=["execute_code", "plot_data"],
                recommended_models=["claude-3-5-sonnet", "gpt-4o", "gemini-2-5-pro"]
            ),
            AgentSpecialization(
                name="planning",
                description="Specialization for planning and organization tasks",
                capabilities=["task breakdown", "scheduling", "resource allocation"],
                system_prompt_template="You are a planning expert that helps organize tasks, schedules, and resources. {additional_instructions}",
                tools=["create_todo", "search_calendar"],
                recommended_models=["claude-3-5-sonnet", "gpt-4o", "gemini-2-5-pro"]
            )
        ]

        for spec in defaults:
            self.register_specialization(spec)

    def register_specialization(self, specialization: AgentSpecialization):
        """
        Register a specialization.

        Args:
            specialization: Agent specialization
        """
        self.specializations[specialization.name] = specialization
        logger.info(f"Registered agent specialization: {specialization.name}")

    def get_specialization(self, name: str) -> Optional[AgentSpecialization]:
        """
        Get a specialization by name.

        Args:
            name: Specialization name

        Returns:
            Agent specialization or None if not found
        """
        return self.specializations.get(name)

    def get_all_specializations(self) -> Dict[str, AgentSpecialization]:
        """
        Get all specializations.

        Returns:
            Dictionary of specializations
        """
        return self.specializations

    def get_specialization_names(self) -> Set[str]:
        """
        Get all specialization names.

        Returns:
            Set of specialization names
        """
        return set(self.specializations.keys())
