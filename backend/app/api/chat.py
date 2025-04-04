from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
from app.core.services.agent_service import AgentService
from app.core.logging_config import setup_logging

logger = setup_logging()
router = APIRouter()

# Simple dependency to get AgentService
def get_agent_service():
    return AgentService()

# Simple dependency to get user_id from request
# In a real implementation, this would verify the JWT token
async def get_current_user(request: Request):
    # Placeholder - would normally extract from JWT token
    return "test_user_id"

@router.post("/chat")
async def chat(
    request_data: Dict[str, Any],
    agent_service: AgentService = Depends(get_agent_service),
    user_id: str = Depends(get_current_user)
):
    """
    Chat endpoint for communicating with an agent
    
    Args:
        request_data: Request data containing agent_id, message, and history
        agent_service: AgentService instance
        user_id: ID of the current user
    
    Returns:
        StreamingResponse with agent's response
    """
    agent_id = request_data.get("agent_id")
    message = request_data.get("message")
    history = request_data.get("history", [])
    
    if not agent_id or not message:
        raise HTTPException(status_code=400, detail="agent_id and message are required")
    
    async def generate():
        async for chunk in agent_service.handle_chat_request(agent_id, message, history, user_id):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
