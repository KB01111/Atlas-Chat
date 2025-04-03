from typing import Dict, Any, List, AsyncGenerator
import json
from app.models.models import RequestContext
from app.core.services.tool_executor import ToolExecutor
from app.core.logging_config import setup_logging

logger = setup_logging()

class AgentService:
    """Service for handling agent requests and orchestrating execution"""
    
    def __init__(self, tool_executor: ToolExecutor = None):
        """Initialize the Agent Service"""
        self.tool_executor = tool_executor or ToolExecutor()
        logger.info("AgentService initialized")
    
    async def handle_chat_request(self, agent_id: str, message: str, history: list, user_id: str) -> AsyncGenerator[str, None]:
        """
        Handle a chat request from the user
        
        Args:
            agent_id: ID of the agent to use
            message: User message
            history: Conversation history
            user_id: ID of the user
            
        Yields:
            Response chunks from the agent
        """
        # Generate/retrieve thread_id (could be based on conversation ID or session)
        thread_id = f"thread_{user_id}_{agent_id}"
        
        # Load agent_definition from Supabase using agent_id
        # In a real implementation, this would query the database
        agent_definition = await self._get_agent_definition(agent_id)
        
        # Create RequestContext
        context = RequestContext(
            thread_id=thread_id,
            user_id=user_id,
            agent_definition=agent_definition
        )
        
        # Log audit event
        logger.info(f"AUDIT: CHAT_REQUEST_RECEIVED - user_id={user_id}, agent_id={agent_id}, thread_id={thread_id}")
        
        # Check agent_definition['agent_type']
        agent_type = agent_definition.get("agent_type", "sdk")
        
        try:
            # Instantiate appropriate executor based on agent_type
            if agent_type == "sdk":
                from app.core.executors.sdk_executor import SDKExecutor
                executor = SDKExecutor(self.tool_executor)
            elif agent_type == "langgraph":
                from app.core.executors.langgraph_executor import LangGraphExecutor
                executor = LangGraphExecutor(self.tool_executor)
            else:
                error_msg = f"Unsupported agent type: {agent_type}"
                logger.error(error_msg)
                yield json.dumps({"type": "error", "content": error_msg})
                return
            
            # Call the executor's execute method
            async for chunk in executor.execute(agent_definition, context, message, history):
                yield chunk
            
            # Handle conversation history persistence
            # In a real implementation, this would save to the database
            # await self._save_conversation_history(thread_id, user_id, message, response)
            
            # Log audit event
            logger.info(f"AUDIT: CHAT_RESPONSE_SENT - user_id={user_id}, agent_id={agent_id}, thread_id={thread_id}")
            
        except Exception as e:
            error_msg = f"Error handling chat request: {str(e)}"
            logger.error(error_msg)
            yield json.dumps({"type": "error", "content": error_msg})
    
    async def _get_agent_definition(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent definition from database
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Agent definition
        """
        # In a real implementation, this would query the database
        # For now, return a mock definition
        return {
            "agent_id": agent_id,
            "name": f"Agent {agent_id}",
            "description": "Test agent with code execution capability",
            "agent_type": "sdk",
            "uses_graphiti": False,
            "allowed_tools": ["execute_code", "write_file", "read_file", "install_packages"],
            "sdk_config": {
                "model": "gpt-4",
                "temperature": 0.7
            }
        }
