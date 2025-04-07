"""
Task Executor module for the Agent Team Coordination Framework.

This module implements the task executor that runs tasks assigned by the coordinator,
manages execution flow, and handles dependencies.
"""

import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Enum for task status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskExecutor:
    """
    Implements the task executor for the agent team coordination framework.

    The TaskExecutor is responsible for:
    - Running tasks assigned by the coordinator
    - Managing execution flow
    - Handling task dependencies
    - Reporting execution results
    """

    def __init__(self):
        """Initialize the task executor."""
        self.executions: Dict[str, Dict[str, Any]] = {}

    async def execute_plan(
        self, coordinator, plan_id: str, agents: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a task plan using the specified agents.

        Args:
            coordinator: Coordinator agent
            plan_id: ID of the plan to execute
            agents: Dictionary mapping agent IDs to agent instances

        Returns:
            Dictionary with execution results
        """
        # Get plan
        plan = coordinator.get_plan(plan_id)
        if not plan:
            raise ValueError(f"Plan not found: {plan_id}")

        # Create execution record
        execution_id = str(uuid.uuid4())
        self.executions[execution_id] = {
            "execution_id": execution_id,
            "plan_id": plan_id,
            "thread_id": plan.thread_id,
            "started_at": datetime.now().isoformat(),
            "status": TaskStatus.IN_PROGRESS,
            "steps": {},
        }

        # Initialize step statuses
        for step in plan.steps:
            step_id = step.get("step_id")
            if step_id:
                self.executions[execution_id]["steps"][step_id] = {
                    "step_id": step_id,
                    "status": TaskStatus.PENDING,
                    "dependencies": step.get("dependencies", []),
                    "agent_id": step.get("agent_id"),
                    "task_description": step.get("task_description"),
                }

        # Execute steps
        results = {}
        all_completed = True

        # Process steps until all are completed or failed
        while self._has_pending_steps(execution_id):
            # Get next executable step
            step = self._get_next_executable_step(execution_id)
            if not step:
                # No executable steps, but still have pending steps
                # This means we have a dependency cycle or all remaining steps
                # have failed dependencies
                logger.warning(
                    f"No executable steps, but still have pending steps for execution {execution_id}"
                )
                all_completed = False
                break

            step_id = step["step_id"]
            agent_id = step["agent_id"]
            task_description = step["task_description"]

            # Update step status
            self.executions[execution_id]["steps"][step_id][
                "status"
            ] = TaskStatus.IN_PROGRESS

            # Get agent
            agent = agents.get(agent_id)
            if not agent:
                logger.warning(f"Agent not found: {agent_id}")
                self.executions[execution_id]["steps"][step_id][
                    "status"
                ] = TaskStatus.FAILED
                self.executions[execution_id]["steps"][step_id][
                    "error"
                ] = f"Agent not found: {agent_id}"
                results[step_id] = {
                    "step_id": step_id,
                    "status": "failed",
                    "error": f"Agent not found: {agent_id}",
                }
                all_completed = False
                continue

            # Execute task
            try:
                result = await agent.execute_task(
                    thread_id=plan.thread_id, task_description=task_description
                )

                # Update step status
                self.executions[execution_id]["steps"][step_id][
                    "status"
                ] = TaskStatus.COMPLETED
                self.executions[execution_id]["steps"][step_id]["result"] = result

                # Create task result
                task_result_id = str(uuid.uuid4())
                coordinator.results[task_result_id] = {
                    "id": task_result_id,
                    "plan_id": plan_id,
                    "step_id": step_id,
                    "agent_id": agent_id,
                    "content": result.get("content", ""),
                    "format": result.get("format", "text"),
                    "created_at": datetime.now().isoformat(),
                    "metadata": {
                        "agent_id": agent_id,
                        "agent_type": getattr(agent, "agent_type", "unknown"),
                    },
                }

                # Add to results
                results[step_id] = {
                    "step_id": step_id,
                    "status": "completed",
                    "result_id": task_result_id,
                    "content": result.get("content", ""),
                }
            except Exception as e:
                logger.error(f"Task execution failed: {e}")
                self.executions[execution_id]["steps"][step_id][
                    "status"
                ] = TaskStatus.FAILED
                self.executions[execution_id]["steps"][step_id]["error"] = str(e)
                results[step_id] = {
                    "step_id": step_id,
                    "status": "failed",
                    "error": str(e),
                }
                all_completed = False

        # Update execution status
        self.executions[execution_id]["status"] = (
            TaskStatus.COMPLETED if all_completed else TaskStatus.FAILED
        )
        self.executions[execution_id]["completed_at"] = datetime.now().isoformat()

        return results

    def _has_pending_steps(self, execution_id: str) -> bool:
        """
        Check if an execution has pending steps.

        Args:
            execution_id: ID of the execution

        Returns:
            True if there are pending steps, False otherwise
        """
        if execution_id not in self.executions:
            return False

        for step in self.executions[execution_id]["steps"].values():
            if step["status"] == TaskStatus.PENDING:
                return True

        return False

    def _get_next_executable_step(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the next executable step for an execution.

        Args:
            execution_id: ID of the execution

        Returns:
            The next executable step or None if none are available
        """
        if execution_id not in self.executions:
            return None

        for step in self.executions[execution_id]["steps"].values():
            if step["status"] != TaskStatus.PENDING:
                continue

            # Check dependencies
            dependencies_met = True
            for dep_id in step["dependencies"]:
                if dep_id not in self.executions[execution_id]["steps"]:
                    dependencies_met = False
                    break

                dep_status = self.executions[execution_id]["steps"][dep_id]["status"]
                if dep_status != TaskStatus.COMPLETED:
                    dependencies_met = False
                    break

            if dependencies_met:
                return step

        return None

    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an execution by ID.

        Args:
            execution_id: ID of the execution to retrieve

        Returns:
            The execution or None if not found
        """
        return self.executions.get(execution_id)

    def get_step_status(self, execution_id: str, step_id: str) -> Optional[TaskStatus]:
        """
        Get the status of a step.

        Args:
            execution_id: ID of the execution
            step_id: ID of the step

        Returns:
            The step status or None if not found
        """
        if execution_id not in self.executions:
            return None

        if step_id not in self.executions[execution_id]["steps"]:
            return None

        return self.executions[execution_id]["steps"][step_id]["status"]
