"""
Integration API module for Atlas-Chat.

This module provides API endpoints for accessing the integrated functionality
of the Tiered Context Management system and Agent Team Coordination framework.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from ..core.services.integration import AtlasIntegration

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
async def process_message(request: MessageRequest):
    """
    Process a user message using the integrated components.
    
    Args:
        request: Message request
        
    Returns:
        Processed message response
    """
    try:
        # Process with specific agent if agent_type is provided
        if request.agent_type:
            result = await integration.process_message_with_agent(
                session_id=request.session_id,
                message=request.message,
                agent_type=request.agent_type
            )
        # Otherwise, process with team or single agent based on use_team
        else:
            result = await integration.process_message(
                session_id=request.session_id,
                message=request.message,
                use_team=request.use_team
            )
        
        return MessageResponse(
            response=result["response"],
            format=result.get("format", "text"),
            metadata=result.get("metadata", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/end")
async def end_session(session_id: str = Body(..., embed=True)):
    """
    End a conversation session.
    
    Args:
        session_id: ID of the session to end
        
    Returns:
        Success status
    """
    try:
        result = integration.end_session(session_id)
        return {"success": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents")
async def get_agents():
    """
    Get all available agents.
    
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
                    "capabilities": agent.capabilities
                }
                for agent in agents
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_type}")
async def get_agents_by_type(agent_type: str):
    """
    Get agents by type.
    
    Args:
        agent_type: Type of agents to retrieve
        
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
                    "capabilities": agent.capabilities
                }
                for agent in agents
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
