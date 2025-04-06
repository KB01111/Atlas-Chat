"""
Integration API module for Atlas-Chat.

This module provides API endpoints for accessing the integrated functionality
of the Tiered Context Management system and Agent Team Coordination framework.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from ..core.services.integration import AtlasIntegration
from ..core.security import get_current_user

router = APIRouter(prefix="/integration", tags=["integration"])

# Initialize integration
integration = AtlasIntegration()


class MessageRequest(BaseModel):
    """Request model for processing a message"""

    session_id: str
    message: str
    use_team: bool = False
    agent_type: Optional[str] = None


class MessageResponse(BaseModel):
    """Response model for a processed message"""

    response: str
    format: str = "text"
    metadata: Dict[str, Any] = {}


@router.post("/message", response_model=MessageResponse)
async def process_message(
    request: MessageRequest, current_user: Dict = Depends(get_current_user)
):
    """
    Process a user message using the integrated components.

    Args:
        request: Message request
        current_user: Current authenticated user

    Returns:
        Processed message response
    """
    try:
        # Process with specific agent if agent_type is provided
        if request.agent_type:
            result = await integration.process_message_with_agent(
                session_id=request.session_id,
                message=request.message,
                agent_type=request.agent_type,
            )
        # Otherwise, process with team or single agent based on use_team
        else:
            result = await integration.process_message(
                session_id=request.session_id,
                message=request.message,
                use_team=request.use_team,
            )

        return MessageResponse(
            response=result["response"],
            format=result.get("format", "text"),
            metadata=result.get("metadata", {}),
        )
    except Exception as e:
        # Sanitize error message to avoid exposing internal details
        raise HTTPException(
            status_code=500, detail="An error occurred while processing the message"
        )


@router.post("/session/end")
async def end_session(
    session_id: str = Body(..., embed=True),
    current_user: Dict = Depends(get_current_user),
):
    """
    End a conversation session.

    Args:
        session_id: ID of the session to end
        current_user: Current authenticated user

    Returns:
        Success status
    """
    try:
        result = integration.end_session(session_id)
        return {"success": result}
    except Exception as e:
        # Sanitize error message to avoid exposing internal details
        raise HTTPException(
            status_code=500, detail="An error occurred while ending the session"
        )


@router.get("/agents")
async def get_agents(current_user: Dict = Depends(get_current_user)):
    """
    Get all available agents.

    Args:
        current_user: Current authenticated user

    Returns:
        List of agents
    """
    try:
        agents = integration.team_manager.get_all_agents()
        return {
            "agents": [
                {
                    "id": agent.agent_id,
                    "type": agent.agent_type,
                    "capabilities": agent.capabilities,
                }
                for agent in agents
            ]
        }
    except Exception as e:
        # Sanitize error message to avoid exposing internal details
        raise HTTPException(
            status_code=500, detail="An error occurred while retrieving agents"
        )


@router.get("/agents/{agent_type}")
async def get_agents_by_type(
    agent_type: str, current_user: Dict = Depends(get_current_user)
):
    """
    Get agents by type.

    Args:
        agent_type: Type of agents to retrieve
        current_user: Current authenticated user

    Returns:
        List of agents of the specified type
    """
    try:
        agents = integration.team_manager.get_agents_by_type(agent_type)
        return {
            "agents": [
                {
                    "id": agent.agent_id,
                    "type": agent.agent_type,
                    "capabilities": agent.capabilities,
                }
                for agent in agents
            ]
        }
    except Exception as e:
        # Sanitize error message to avoid exposing internal details
        raise HTTPException(
            status_code=500, detail="An error occurred while retrieving agents by type"
        )
