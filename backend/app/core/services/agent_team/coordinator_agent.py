"""
Coordinator Agent module for the Agent Team Coordination Framework.

This module implements the coordinator agent that manages specialized worker agents,
creates task plans, assigns tasks, and synthesizes results.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid
import logging
import json
from pydantic import BaseModel, Field

from .team_context_manager import TeamContextManager

logger = logging.getLogger(__name__)

class TaskPlan(BaseModel):
    """Represents a task plan created by the coordinator agent"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    thread_id: str
    user_request: str
    steps: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = "created"  # created, in_progress, completed, failed
    metadata: Dict[str, Any] = {}

class TaskResult(BaseModel):
    """Represents a result from a task execution"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plan_id: str
    step_id: str
    agent_id: str
    content: str
    format: str = "text"  # text, markdown, json, html
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = {}

class CoordinatorAgent:
    """
    Implements the coordinator agent for the agent team coordination framework.

    The CoordinatorAgent is responsible for:
    - Analyzing user requests to create task plans
    - Assigning tasks to specialized agents
    - Managing task dependencies and execution flow
    - Synthesizing results from multiple agents
    - Providing a unified response to the user
    """

    def __init__(self, context_manager=None, openai_client=None):
        """
        Initialize the coordinator agent.

        Args:
            context_manager: Optional context manager for maintaining context
            openai_client: Optional OpenAI client for API access
        """
        self.context_manager = context_manager or TeamContextManager()
        self.client = openai_client
        self.plans: Dict[str, TaskPlan] = {}
        self.results: Dict[str, TaskResult] = {}

    async def create_plan(self, thread_id: str, user_request: str, 
                        available_agents: List[str]) -> TaskPlan:
        """
        Create a task plan for a user request.

        Args:
            thread_id: ID of the conversation thread
            user_request: User's request to be processed
            available_agents: List of available agent IDs

        Returns:
            Task plan with steps
        """
        # In a real implementation, this would use the OpenAI client
        # to analyze the request and create a task plan

        # Simulate plan creation
        plan = TaskPlan(
            thread_id=thread_id,
            user_request=user_request
        )

        # Add steps based on available agents
        step_id = 1
        for agent_id in available_agents[:3]:  # Use up to 3 agents
            plan.steps.append({
                "step_id": f"step_{step_id}",
                "agent_id": agent_id,
                "task_description": f"Process the following request: {user_request}",
                "dependencies": [] if step_id == 1 else [f"step_{step_id-1}"]
            })
            step_id += 1

        # Store plan
        self.plans[plan.id] = plan

        # Store in context manager
        self.context_manager.store_plan(thread_id, plan.dict())

        return plan

    async def execute_plan(self, plan_id: str, agent_instances: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task plan using the specified agent instances.

        Args:
            plan_id: ID of the plan to execute
            agent_instances: Dictionary mapping agent IDs to agent instances

        Returns:
            Dictionary with execution results
        """
        # Get plan
        plan = self.plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan not found: {plan_id}")

        # Update plan status
        plan.status = "in_progress"

        # Execute steps
        results = {}
        for step in plan.steps:
            step_id = step.get("step_id")
            agent_id = step.get("agent_id")
            task_description = step.get("task_description")

            # Skip if missing required fields
            if not all([step_id, agent_id, task_description]):
                logger.warning(f"Skipping step with missing fields: {step}")
                continue

            # Get agent
            agent = agent_instances.get(agent_id)
            if not agent:
                logger.warning(f"Agent not found: {agent_id}")
                results[step_id] = {
                    "step_id": step_id,
                    "status": "failed",
                    "error": f"Agent not found: {agent_id}"
                }
                continue

            # Check dependencies
            dependencies = step.get("dependencies", [])
            dependency_failed = False
            for dep_id in dependencies:
                if dep_id not in results or results[dep_id].get("status") != "completed":
                    dependency_failed = True
                    break

            if dependency_failed:
                results[step_id] = {
                    "step_id": step_id,
                    "status": "failed",
                    "error": "Dependency failed or not completed"
                }
                continue

            # Execute task
            try:
                result = await agent.execute_task(
                    thread_id=plan.thread_id,
                    task_description=task_description
                )

                # Create task result
                task_result = TaskResult(
                    plan_id=plan_id,
                    step_id=step_id,
                    agent_id=agent_id,
                    content=result.get("content", ""),
                    format=result.get("format", "text"),
                    metadata={
                        "agent_id": agent_id,
                        "agent_type": getattr(agent, "agent_type", "unknown")
                    }
                )

                # Store result
                self.results[task_result.id] = task_result

                # Store in context manager
                self.context_manager.store_result(plan.thread_id, task_result.dict())

                # Add to results
                results[step_id] = {
                    "step_id": step_id,
                    "status": "completed",
                    "result_id": task_result.id,
                    "content": task_result.content
                }
            except Exception as e:
                logger.error(f"Task execution failed: {e}")
                results[step_id] = {
                    "step_id": step_id,
                    "status": "failed",
                    "error": str(e)
                }

        # Update plan status
        all_completed = all(r.get("status") == "completed" for r in results.values())
        plan.status = "completed" if all_completed else "failed"

        return results

    async def synthesize_results(self, result_ids: List[str], format: str = "markdown") -> Dict[str, Any]:
        """
        Synthesize results from multiple tasks.

        Args:
            result_ids: List of result IDs to synthesize
            format: Format of the synthesized result

        Returns:
            Dictionary with synthesized result
        """
        # Get results
        results = []
        for result_id in result_ids:
            result = self.results.get(result_id)
            if result:
                results.append(result)

        # In a real implementation, this would use the OpenAI client
        # to synthesize the results

        # Simulate synthesis
        if not results:
            return {
                "content": "No results to synthesize.",
                "format": format
            }

        # Simple concatenation for demonstration
        synthesis = "# Synthesized Results\n\n"
        for i, result in enumerate(results, 1):
            synthesis += f"## Result {i} (from {result.metadata.get('agent_type', 'unknown')})\n\n"
            synthesis += result.content
            synthesis += "\n\n"

        return {
            "content": synthesis,
            "format": format
        }

    def get_plan(self, plan_id: str) -> Optional[TaskPlan]:
        """
        Get a plan by ID.

        Args:
            plan_id: ID of the plan to retrieve

        Returns:
            The plan or None if not found
        """
        return self.plans.get(plan_id)

    def get_result(self, result_id: str) -> Optional[TaskResult]:
        """
        Get a result by ID.

        Args:
            result_id: ID of the result to retrieve

        Returns:
            The result or None if not found
        """
        return self.results.get(result_id)

    def get_plan_results(self, plan_id: str) -> List[TaskResult]:
        """
        Get results for a plan.

        Args:
            plan_id: ID of the plan

        Returns:
            List of results
        """
        return [r for r in self.results.values() if r.plan_id == plan_id]
