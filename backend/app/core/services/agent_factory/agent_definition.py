"""
Agent definition models for the agent factory.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
import uuid


class AgentDefinition(BaseModel):
    """Definition for an agent."""

    agent_id: Optional[str] = Field(
        default_factory=lambda: f"agent_{str(uuid.uuid4())}"
    )
    name: str
    description: str
    agent_type: str = Field(
        ..., description="Type of agent: 'sdk', 'langgraph', or 'hybrid'"
    )
    model_id: str
    system_prompt: str
    tools: List[str] = []
    memory_enabled: bool = True
    specialized_for: Optional[str] = None
    team_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""

        schema_extra = {
            "example": {
                "name": "Research Assistant",
                "description": "Agent specialized for research tasks",
                "agent_type": "sdk",
                "model_id": "claude-3-5-sonnet",
                "system_prompt": "You are a research expert that helps find and analyze information.",
                "tools": ["search_web", "search_graphiti"],
                "memory_enabled": True,
                "specialized_for": "research",
            }
        }


class AgentMessage(BaseModel):
    """Message in an agent conversation."""

    role: str = Field(
        ..., description="Role of the message sender: 'user', 'assistant', or 'system'"
    )
    content: Union[str, List[Dict[str, Any]]]

    class Config:
        """Pydantic configuration."""

        schema_extra = {
            "example": {
                "role": "user",
                "content": "Can you help me research quantum computing?",
            }
        }


class AgentResponse(BaseModel):
    """Response from an agent."""

    agent_id: str
    message: AgentMessage
    usage: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""

        schema_extra = {
            "example": {
                "agent_id": "agent_123456",
                "message": {
                    "role": "assistant",
                    "content": "I'd be happy to help you research quantum computing.",
                },
                "usage": {
                    "prompt_tokens": 20,
                    "completion_tokens": 10,
                    "total_tokens": 30,
                },
            }
        }


class AgentRequest(BaseModel):
    """Request to an agent."""

    agent_id: Optional[str] = None
    messages: List[AgentMessage]
    stream: bool = False
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""

        schema_extra = {
            "example": {
                "agent_id": "agent_123456",
                "messages": [
                    {
                        "role": "user",
                        "content": "Can you help me research quantum computing?",
                    }
                ],
                "stream": False,
                "max_tokens": 1000,
                "temperature": 0.7,
            }
        }
