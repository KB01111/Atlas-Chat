"""
Team Manager module for the Agent Team Coordination Framework.

This module implements the team manager that orchestrates the agent team,
manages agent registration, and handles user interactions.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid
import logging
from pydantic import BaseModel, Field

from .coordinator_agent import CoordinatorAgent
from .specialized_agent import SpecializedAgent, ResearchAgent, CoderAgent, WritingAgent, AnalysisAgent
from .task_executor import TaskExecutor
from .team_context_manager import TeamContextManager

logger = logging.getLogger(__name__)

class AgentTeamManager:
    """
    Implements the team manager for the agent team coordination framework.
    
    The AgentTeamManager is responsible for:
    - Orchestrating the agent team
    - Managing agent registration and configuration
    - Handling user interactions
    - Coordinating task execution
    - Providing a unified interface to the agent team
    """
    
    def __init__(self, openai_client=None):
        """
        Initialize the agent team manager.
        
        Args:
            openai_client: Optional OpenAI client for API access
        """
        self.client = openai_client
        self.context_manager = TeamContextManager()
        self.coordinator = CoordinatorAgent(context_manager=self.context_manager, openai_client=self.client)
        self.task_executor = TaskExecutor()
        
        # Initialize agent registry
        self.agents: Dict[str, SpecializedAgent] = {}
        
        # Register default agents
        self._register_default_agents()
    
    def _register_default_agents(self) -> None:
        """Register default specialized agents"""
        # Research agent
        research_agent = ResearchAgent(
            agent_id="research_agent",
            context_manager=self.context_manager,
            openai_client=self.client
        )
        self.register_agent(research_agent)
        
        # Coder agent
        coder_agent = CoderAgent(
            agent_id="coder_agent",
            context_manager=self.context_manager,
            openai_client=self.client
        )
        self.register_agent(coder_agent)
        
        # Writing agent
        writing_agent = WritingAgent(
            agent_id="writing_agent",
            context_manager=self.context_manager,
            openai_client=self.client
        )
        self.register_agent(writing_agent)
        
        # Analysis agent
        analysis_agent = AnalysisAgent(
            agent_id="analysis_agent",
            context_manager=self.context_manager,
            openai_client=self.client
        )
        self.register_agent(analysis_agent)
    
    def register_agent(self, agent: SpecializedAgent) -> None:
        """
        Register a specialized agent with the team.
        
        Args:
            agent: Specialized agent to register
        """
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.agent_id} ({agent.agent_type})")
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister a specialized agent from the team.
        
        Args:
            agent_id: ID of the agent to unregister
            
        Returns:
            True if successful, False otherwise
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")
            return True
        
        return False
    
    def get_agent(self, agent_id: str) -> Optional[SpecializedAgent]:
        """
        Get a specialized agent by ID.
        
        Args:
            agent_id: ID of the agent to retrieve
            
        Returns:
            The agent or None if not found
        """
        return self.agents.get(agent_id)
    
    def get_agents_by_type(self, agent_type: str) -> List[SpecializedAgent]:
        """
        Get specialized agents by type.
        
        Args:
            agent_type: Type of agents to retrieve
            
        Returns:
            List of agents of the specified type
        """
        return [a for a in self.agents.values() if a.agent_type == agent_type]
    
    def get_all_agents(self) -> List[SpecializedAgent]:
        """
        Get all registered specialized agents.
        
        Returns:
            List of all agents
        """
        return list(self.agents.values())
    
    async def process_request(self, thread_id: str, user_request: str) -> Dict[str, Any]:
        """
        Process a user request using the agent team.
        
        Args:
            thread_id: ID of the conversation thread
            user_request: User's request to be processed
            
        Returns:
            Dictionary with processing results
        """
        # Store user request in context manager
        self.context_manager.add_user_message(
            thread_id=thread_id,
            content=user_request
        )
        
        # Create task plan
        plan = await self.coordinator.create_plan(
            thread_id=thread_id,
            user_request=user_request,
            available_agents=list(self.agents.keys())
        )
        
        # Execute plan
        execution_results = await self.task_executor.execute_plan(
            coordinator=self.coordinator,
            plan_id=plan.id,
            agents=self.agents
        )
        
        # Get result IDs
        result_ids = []
        for step_result in execution_results.values():
            if step_result.get("status") == "completed" and "result_id" in step_result:
                result_ids.append(step_result["result_id"])
        
        # Synthesize results
        synthesis = await self.coordinator.synthesize_results(result_ids)
        
        # Store assistant response in context manager
        self.context_manager.add_assistant_message(
            thread_id=thread_id,
            content=synthesis["content"]
        )
        
        return {
            "plan_id": plan.id,
            "execution_results": execution_results,
            "synthesis": synthesis
        }
    
    async def process_request_with_agent(self, thread_id: str, user_request: str, 
                                      agent_id: str) -> Dict[str, Any]:
        """
        Process a user request using a specific agent.
        
        Args:
            thread_id: ID of the conversation thread
            user_request: User's request to be processed
            agent_id: ID of the agent to use
            
        Returns:
            Dictionary with processing results
        """
        # Get agent
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        # Store user request in context manager
        self.context_manager.add_user_message(
            thread_id=thread_id,
            content=user_request
        )
        
        # Execute task
        result = await agent.execute_task(
            thread_id=thread_id,
            task_description=user_request
        )
        
        # Store assistant response in context manager
        self.context_manager.add_assistant_message(
            thread_id=thread_id,
            content=result["content"]
        )
        
        return {
            "agent_id": agent_id,
            "result": result
        }
    
    def get_conversation_history(self, thread_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history for a thread.
        
        Args:
            thread_id: ID of the conversation thread
            
        Returns:
            List of messages in the conversation
        """
        return self.context_manager.get_conversation_history(thread_id)
