from typing import Dict, List, Optional, Any, Union, Callable, Awaitable
import asyncio
import logging
import uuid
from enum import Enum
from datetime import datetime
import json

from .session import E2BSession
from .artifacts import Artifact, ArtifactManager

logger = logging.getLogger(__name__)

class AgentRole(str, Enum):
    """
    Roles that agents can have in a team.
    """
    SUPERVISOR = "supervisor"
    CODER = "coder"
    REVIEWER = "reviewer"
    TESTER = "tester"
    RESEARCHER = "researcher"
    DOCUMENTER = "documenter"


class AgentTask:
    """
    Represents a task assigned to an agent.
    """
    
    def __init__(
        self,
        task_id: str,
        title: str,
        description: str,
        assigned_to: str,
        assigned_by: str,
        status: str = "pending",
        priority: str = "medium",
        dependencies: Optional[List[str]] = None,
        artifacts: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a task.
        
        Args:
            task_id: Unique identifier for the task
            title: Title of the task
            description: Description of the task
            assigned_to: ID of the agent assigned to the task
            assigned_by: ID of the agent who assigned the task
            status: Status of the task (pending, in_progress, completed, failed)
            priority: Priority of the task (low, medium, high, critical)
            dependencies: List of task IDs that this task depends on
            artifacts: List of artifact IDs associated with this task
            metadata: Additional metadata for the task
        """
        self.id = task_id
        self.title = title
        self.description = description
        self.assigned_to = assigned_to
        self.assigned_by = assigned_by
        self.status = status
        self.priority = priority
        self.dependencies = dependencies or []
        self.artifacts = artifacts or []
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.completion_percentage = 0
        self.comments: List[Dict[str, Any]] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task to a dictionary.
        
        Returns:
            Dictionary representation of the task
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "assigned_to": self.assigned_to,
            "assigned_by": self.assigned_by,
            "status": self.status,
            "priority": self.priority,
            "dependencies": self.dependencies,
            "artifacts": self.artifacts,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completion_percentage": self.completion_percentage,
            "comments": self.comments
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentTask':
        """
        Create a task from a dictionary.
        
        Args:
            data: Dictionary representation of the task
            
        Returns:
            Task object
        """
        task = cls(
            task_id=data["id"],
            title=data["title"],
            description=data["description"],
            assigned_to=data["assigned_to"],
            assigned_by=data["assigned_by"],
            status=data.get("status", "pending"),
            priority=data.get("priority", "medium"),
            dependencies=data.get("dependencies", []),
            artifacts=data.get("artifacts", []),
            metadata=data.get("metadata", {})
        )
        task.completion_percentage = data.get("completion_percentage", 0)
        task.comments = data.get("comments", [])
        return task
    
    def update_status(self, status: str, comment: Optional[str] = None) -> None:
        """
        Update the status of the task.
        
        Args:
            status: New status
            comment: Optional comment about the status update
        """
        self.status = status
        self.updated_at = datetime.now().isoformat()
        
        # Update completion percentage based on status
        if status == "completed":
            self.completion_percentage = 100
        elif status == "in_progress":
            # Only update if it's still at 0
            if self.completion_percentage == 0:
                self.completion_percentage = 10
        
        # Add comment if provided
        if comment:
            self.add_comment(comment)
    
    def update_completion_percentage(self, percentage: int) -> None:
        """
        Update the completion percentage of the task.
        
        Args:
            percentage: New completion percentage (0-100)
        """
        self.completion_percentage = max(0, min(100, percentage))
        self.updated_at = datetime.now().isoformat()
        
        # Update status based on completion percentage
        if self.completion_percentage == 100 and self.status != "completed":
            self.status = "completed"
        elif self.completion_percentage > 0 and self.status == "pending":
            self.status = "in_progress"
    
    def add_artifact(self, artifact_id: str) -> None:
        """
        Add an artifact to the task.
        
        Args:
            artifact_id: ID of the artifact
        """
        if artifact_id not in self.artifacts:
            self.artifacts.append(artifact_id)
            self.updated_at = datetime.now().isoformat()
    
    def add_comment(self, content: str, author_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a comment to the task.
        
        Args:
            content: Comment content
            author_id: ID of the comment author
            
        Returns:
            The created comment
        """
        comment = {
            "id": str(uuid.uuid4()),
            "content": content,
            "author_id": author_id,
            "created_at": datetime.now().isoformat()
        }
        self.comments.append(comment)
        self.updated_at = datetime.now().isoformat()
        return comment


class Agent:
    """
    Represents an agent in the system.
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        role: AgentRole,
        capabilities: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Name of the agent
            role: Role of the agent
            capabilities: List of capabilities the agent has
            metadata: Additional metadata for the agent
        """
        self.id = agent_id
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.metadata = metadata or {}
        self.tasks: Dict[str, AgentTask] = {}
        self.created_at = datetime.now().isoformat()
        self.status = "idle"  # idle, busy, offline
        self.last_active = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent to a dictionary.
        
        Returns:
            Dictionary representation of the agent
        """
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
            "tasks": [task.to_dict() for task in self.tasks.values()],
            "created_at": self.created_at,
            "status": self.status,
            "last_active": self.last_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """
        Create an agent from a dictionary.
        
        Args:
            data: Dictionary representation of the agent
            
        Returns:
            Agent object
        """
        agent = cls(
            agent_id=data["id"],
            name=data["name"],
            role=AgentRole(data["role"]),
            capabilities=data["capabilities"],
            metadata=data.get("metadata", {})
        )
        
        # Add tasks
        for task_data in data.get("tasks", []):
            task = AgentTask.from_dict(task_data)
            agent.tasks[task.id] = task
        
        agent.status = data.get("status", "idle")
        agent.last_active = data.get("last_active", agent.created_at)
        
        return agent
    
    def assign_task(self, task: AgentTask) -> None:
        """
        Assign a task to the agent.
        
        Args:
            task: Task to assign
        """
        self.tasks[task.id] = task
        self.status = "busy"
        self.last_active = datetime.now().isoformat()
    
    def get_task(self, task_id: str) -> Optional[AgentTask]:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task object or None if not found
        """
        return self.tasks.get(task_id)
    
    def list_tasks(self, status: Optional[str] = None) -> List[AgentTask]:
        """
        List tasks assigned to the agent.
        
        Args:
            status: Filter tasks by status
            
        Returns:
            List of tasks
        """
        if status is None:
            return list(self.tasks.values())
        else:
            return [task for task in self.tasks.values() if task.status == status]
    
    def update_task_status(self, task_id: str, status: str, comment: Optional[str] = None) -> bool:
        """
        Update the status of a task.
        
        Args:
            task_id: ID of the task
            status: New status
            comment: Optional comment about the status update
            
        Returns:
            True if the task was updated, False otherwise
        """
        if task_id in self.tasks:
            self.tasks[task_id].update_status(status, comment)
            self.last_active = datetime.now().isoformat()
            
            # Update agent status if all tasks are completed
            if all(task.status in ["completed", "failed"] for task in self.tasks.values()):
                self.status = "idle"
            else:
                self.status = "busy"
                
            return True
        return False
    
    def has_capability(self, capability: str) -> bool:
        """
        Check if the agent has a specific capability.
        
        Args:
            capability: Capability to check
            
        Returns:
            True if the agent has the capability, False otherwise
        """
        return capability in self.capabilities
    
    def update_status(self, status: str) -> None:
        """
        Update the agent's status.
        
        Args:
            status: New status (idle, busy, offline)
        """
        self.status = status
        self.last_active = datetime.now().isoformat()


class AgentTeam:
    """
    Represents a team of agents.
    """
    
    def __init__(
        self,
        team_id: str,
        name: str,
        supervisor_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a team.
        
        Args:
            team_id: Unique identifier for the team
            name: Name of the team
            supervisor_id: ID of the supervisor agent
            metadata: Additional metadata for the team
        """
        self.id = team_id
        self.name = name
        self.supervisor_id = supervisor_id
        self.metadata = metadata or {}
        self.agents: Dict[str, Agent] = {}
        self.created_at = datetime.now().isoformat()
        self.last_active = self.created_at
        self.chat_history: List[Dict[str, Any]] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the team to a dictionary.
        
        Returns:
            Dictionary representation of the team
        """
        return {
            "id": self.id,
            "name": self.name,
            "supervisor_id": self.supervisor_id,
            "metadata": self.metadata,
            "agents": [agent.to_dict() for agent in self.agents.values()],
            "created_at": self.created_at,
            "last_active": self.last_active,
            "chat_history": self.chat_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentTeam':
        """
        Create a team from a dictionary.
        
        Args:
            data: Dictionary representation of the team
            
        Returns:
            Team object
        """
        team = cls(
            team_id=data["id"],
            name=data["name"],
            supervisor_id=data["supervisor_id"],
            metadata=data.get("metadata", {})
        )
        
        # Add agents
        for agent_data in data.get("agents", []):
            agent = Agent.from_dict(agent_data)
            team.agents[agent.id] = agent
        
        team.last_active = data.get("last_active", team.created_at)
        team.chat_history = data.get("chat_history", [])
        
        return team
    
    def add_agent(self, agent: Agent) -> None:
        """
        Add an agent to the team.
        
        Args:
            agent: Agent to add
        """
        self.agents[agent.id] = agent
        self.last_active = datetime.now().isoformat()
    
    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from the team.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            True if the agent was removed, False otherwise
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.last_active = datetime.now().isoformat()
            return True
        return False
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Agent object or None if not found
        """
        return self.agents.get(agent_id)
    
    def list_agents(self, role: Optional[AgentRole] = None) -> List[Agent]:
        """
        List agents in the team.
        
        Args:
            role: Filter agents by role
            
        Returns:
            List of agents
        """
        if role is None:
            return list(self.agents.values())
        else:
            return [agent for agent in self.agents.values() if agent.role == role]
    
    def get_supervisor(self) -> Optional[Agent]:
        """
        Get the supervisor agent.
        
        Returns:
            Supervisor agent or None if not found
        """
        return self.agents.get(self.supervisor_id)
    
    def find_agents_with_capability(self, capability: str) -> List[Agent]:
        """
        Find agents with a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of agents with the capability
        """
        return [agent for agent in self.agents.values() if agent.has_capability(capability)]
    
    def add_chat_message(self, content: str, sender_id: str, message_type: str = "text") -> Dict[str, Any]:
        """
        Add a message to the team chat history.
        
        Args:
            content: Message content
            sender_id: ID of the message sender
            message_type: Type of message (text, code, result, etc.)
            
        Returns:
            The created message
        """
        message = {
            "id": str(uuid.uuid4()),
            "content": content,
            "sender_id": sender_id,
            "type": message_type,
            "timestamp": datetime.now().isoformat()
        }
        self.chat_history.append(message)
        self.last_active = datetime.now().isoformat()
        
        # Update the sender's last active time
        sender = self.get_agent(sender_id)
        if sender:
            sender.last_active = datetime.now().isoformat()
            
        return message


class AgentDelegationService:
    """
    Service for managing agent delegation.
    """
    
    def __init__(self, e2b_session: E2BSession):
        """
        Initialize the agent delegation service.
        
        Args:
            e2b_session: E2B session for code execution
        """
        self.e2b_session = e2b_session
        self.artifact_manager = ArtifactManager(e2b_session)
        self.teams: Dict[str, AgentTeam] = {}
        self.task_callbacks: Dict[str, List[Callable[[AgentTask], Awaitable[None]]]] = {}
    
    async def initialize(self):
        """
        Initialize the agent delegation service.
        """
        await self.artifact_manager.initialize()
    
    def create_team(
        self,
        name: str,
        supervisor_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentTeam:
        """
        Create a new team with a supervisor.
        
        Args:
            name: Name of the team
            supervisor_name: Name of the supervisor agent
            metadata: Additional metadata for the team
            
        Returns:
            Team object
        """
        # Create the supervisor agent
        supervisor_id = str(uuid.uuid4())
        supervisor = Agent(
            agent_id=supervisor_id,
            name=supervisor_name,
            role=AgentRole.SUPERVISOR,
            capabilities=["task_delegation", "team_management", "progress_monitoring"],
            metadata={"is_supervisor": True}
        )
        
        # Create the team
        team_id = str(uuid.uuid4())
        team = AgentTeam(
            team_id=team_id,
            name=name,
            supervisor_id=supervisor_id,
            metadata=metadata
        )
        
        # Add the supervisor to the team
        team.add_agent(supervisor)
        
        # Store the team
        self.teams[team_id] = team
        
        return team
    
    def get_team(self, team_id: str) -> Optional[AgentTeam]:
        """
        Get a team by ID.
        
        Args:
            team_id: ID of the team
            
        Returns:
            Team object or None if not found
        """
        return self.teams.get(team_id)
    
    def list_teams(self) -> List[AgentTeam]:
        """
        List all teams.
        
        Returns:
            List of teams
        """
        return list(self.teams.values())
    
    def add_agent_to_team(
        self,
        team_id: str,
        name: str,
        role: AgentRole,
        capabilities: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Agent]:
        """
        Add an agent to a team.
        
        Args:
            team_id: ID of the team
            name: Name of the agent
            role: Role of the agent
            capabilities: List of capabilities the agent has
            metadata: Additional metadata for the agent
            
        Returns:
            Agent object or None if the team was not found
        """
        team = self.get_team(team_id)
        if team is None:
            return None
        
        # Create the agent
        agent_id = str(uuid.uuid4())
        agent = Agent(
            agent_id=agent_id,
            name=name,
            role=role,
            capabilities=capabilities,
            metadata=metadata
        )
        
        # Add the agent to the team
        team.add_agent(agent)
        
        return agent
    
    def create_coding_agent(
        self,
        team_id: str,
        name: str,
        languages: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Agent]:
        """
        Create a coding agent and add it to a team.
        
        Args:
            team_id: ID of the team
            name: Name of the agent
            languages: List of programming languages the agent can work with
            metadata: Additional metadata for the agent
            
        Returns:
            Agent object or None if the team was not found
        """
        # Prepare capabilities based on languages
        capabilities = ["code_execution", "code_generation", "code_review"]
        for language in languages:
            capabilities.append(f"language_{language.lower()}")
        
        # Prepare metadata
        agent_metadata = metadata or {}
        agent_metadata["languages"] = languages
        agent_metadata["is_coding_agent"] = True
        
        # Create and add the agent
        return self.add_agent_to_team(
            team_id=team_id,
            name=name,
            role=AgentRole.CODER,
            capabilities=capabilities,
            metadata=agent_metadata
        )
    
    async def delegate_coding_task(
        self,
        team_id: str,
        title: str,
        description: str,
        language: str,
        code: Optional[str] = None,
        priority: str = "medium",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[AgentTask]:
        """
        Delegate a coding task to an appropriate agent in the team.
        
        Args:
            team_id: ID of the team
            title: Title of the task
            description: Description of the task
            language: Programming language for the task
            code: Initial code for the task
            priority: Priority of the task
            metadata: Additional metadata for the task
            
        Returns:
            Task object or None if no suitable agent was found
        """
        team = self.get_team(team_id)
        if team is None:
            logger.error(f"Team not found: {team_id}")
            return None
        
        # Get the supervisor
        supervisor = team.get_supervisor()
        if supervisor is None:
            logger.error(f"Supervisor not found for team: {team_id}")
            return None
        
        # Find agents with the required language capability
        language_capability = f"language_{language.lower()}"
        suitable_agents = team.find_agents_with_capability(language_capability)
        
        # Filter for coding agents
        coding_agents = [
            agent for agent in suitable_agents
            if agent.role == AgentRole.CODER and agent.has_capability("code_execution")
        ]
        
        if not coding_agents:
            logger.warning(f"No suitable coding agents found for language: {language}")
            
            # Add a message to the team chat
            team.add_chat_message(
                content=f"No suitable coding agents found for language: {language}. Please add an agent with {language} capability.",
                sender_id=supervisor.id,
                message_type="system"
            )
            
            return None
        
        # Select the agent with the fewest pending tasks
        selected_agent = min(
            coding_agents,
            key=lambda agent: len(agent.list_tasks(status="pending"))
        )
        
        # Create task metadata
        task_metadata = metadata or {}
        task_metadata["language"] = language
        if code:
            task_metadata["initial_code"] = code
        
        # Create the task
        task_id = str(uuid.uuid4())
        task = AgentTask(
            task_id=task_id,
            title=title,
            description=description,
            assigned_to=selected_agent.id,
            assigned_by=supervisor.id,
            status="pending",
            priority=priority,
            metadata=task_metadata
        )
        
        # Assign the task to the agent
        selected_agent.assign_task(task)
        
        # Add a message to the team chat
        team.add_chat_message(
            content=f"Task '{title}' assigned to {selected_agent.name}",
            sender_id=supervisor.id,
            message_type="system"
        )
        
        # If code is provided, create an artifact
        if code:
            try:
                artifact = await self.artifact_manager.create_artifact(
                    content=code,
                    name=f"task_{task_id}_initial_code.{language.lower()}",
                    content_type=f"text/x-{language.lower()}",
                    metadata={"task_id": task_id, "type": "initial_code"}
                )
                task.add_artifact(artifact.id)
                
                # Add a message to the team chat
                team.add_chat_message(
                    content=f"Initial code added to task '{title}'",
                    sender_id=supervisor.id,
                    message_type="system"
                )
            except Exception as e:
                logger.error(f"Error creating artifact for task {task_id}: {str(e)}")
        
        # Trigger task callbacks
        await self._trigger_task_callbacks(task)
        
        return task
    
    async def execute_coding_task(
        self,
        team_id: str,
        task_id: str
    ) -> Dict[str, Any]:
        """
        Execute a coding task using the E2B code interpreter.
        
        Args:
            team_id: ID of the team
            task_id: ID of the task
            
        Returns:
            Result of the execution
        """
        team = self.get_team(team_id)
        if team is None:
            logger.error(f"Team not found: {team_id}")
            return {"success": False, "error": "Team not found"}
        
        # Find the agent with the task
        agent = None
        task = None
        for a in team.agents.values():
            t = a.get_task(task_id)
            if t is not None:
                agent = a
                task = t
                break
        
        if agent is None or task is None:
            logger.error(f"Task not found: {task_id}")
            return {"success": False, "error": "Task not found"}
        
        # Update task status
        task.update_status("in_progress")
        
        # Add a message to the team chat
        team.add_chat_message(
            content=f"Starting execution of task '{task.title}'",
            sender_id=agent.id,
            message_type="system"
        )
        
        try:
            # Get the code to execute
            code = task.metadata.get("initial_code", "")
            if not code:
                # Try to get code from artifacts
                for artifact_id in task.artifacts:
                    artifact = await self.artifact_manager.get_artifact(artifact_id)
                    if artifact and "initial_code" in artifact.metadata.get("type", ""):
                        code = artifact.content.decode("utf-8")
                        break
            
            if not code:
                logger.error(f"No code to execute for task {task_id}")
                task.update_status("failed", "No code to execute")
                
                # Add a message to the team chat
                team.add_chat_message(
                    content=f"Failed to execute task '{task.title}': No code to execute",
                    sender_id=agent.id,
                    message_type="error"
                )
                
                return {"success": False, "error": "No code to execute"}
            
            # Get the language
            language = task.metadata.get("language", "python").lower()
            
            # Add a message to the team chat with the code
            team.add_chat_message(
                content=code,
                sender_id=agent.id,
                message_type="code"
            )
            
            # Prepare the command based on the language
            cmd = []
            if language == "python":
                cmd = ["python", "-c", "import sys; exec(sys.stdin.read())"]
            elif language == "javascript" or language == "js":
                cmd = ["node", "-e", "eval(require('fs').readFileSync(0, 'utf-8'))"]
            elif language == "bash" or language == "shell":
                cmd = ["bash", "-c", "source /dev/stdin"]
            else:
                # Default to Python
                cmd = ["python", "-c", "import sys; exec(sys.stdin.read())"]
                language = "python"
            
            # Execute the code
            try:
                process = await self.e2b_session.process.start({
                    "cmd": cmd,
                    "env": {"PYTHONIOENCODING": "utf-8", "NODE_OPTIONS": "--no-warnings"}
                })
                
                # Write the code to stdin
                await process.stdin.write(code)
                await process.stdin.end()
                
                # Wait for the process to complete
                result = await process.wait()
                
                # Create artifacts for stdout and stderr
                if result.stdout:
                    stdout_artifact = await self.artifact_manager.create_artifact(
                        content=result.stdout,
                        name=f"task_{task_id}_stdout.txt",
                        content_type="text/plain",
                        metadata={"task_id": task_id, "type": "stdout"}
                    )
                    task.add_artifact(stdout_artifact.id)
                    
                    # Add a message to the team chat with the stdout
                    team.add_chat_message(
                        content=result.stdout,
                        sender_id=agent.id,
                        message_type="result"
                    )
                
                if result.stderr:
                    stderr_artifact = await self.artifact_manager.create_artifact(
                        content=result.stderr,
                        name=f"task_{task_id}_stderr.txt",
                        content_type="text/plain",
                        metadata={"task_id": task_id, "type": "stderr"}
                    )
                    task.add_artifact(stderr_artifact.id)
                    
                    # Add a message to the team chat with the stderr
                    team.add_chat_message(
                        content=result.stderr,
                        sender_id=agent.id,
                        message_type="error"
                    )
                
                # Scan for additional artifacts
                additional_artifacts = await self.artifact_manager.scan_for_artifacts()
                for artifact in additional_artifacts:
                    artifact.metadata["task_id"] = task_id
                    task.add_artifact(artifact.id)
                
                # Update task status based on exit code
                if result.exit_code == 0:
                    task.update_status("completed", "Code executed successfully")
                    
                    # Add a message to the team chat
                    team.add_chat_message(
                        content=f"Task '{task.title}' completed successfully",
                        sender_id=agent.id,
                        message_type="system"
                    )
                    
                    return {
                        "success": True,
                        "exit_code": result.exit_code,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "artifacts": [a.id for a in additional_artifacts]
                    }
                else:
                    task.update_status("failed", f"Code execution failed with exit code {result.exit_code}")
                    
                    # Add a message to the team chat
                    team.add_chat_message(
                        content=f"Task '{task.title}' failed with exit code {result.exit_code}",
                        sender_id=agent.id,
                        message_type="error"
                    )
                    
                    return {
                        "success": False,
                        "exit_code": result.exit_code,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "artifacts": [a.id for a in additional_artifacts]
                    }
            except Exception as e:
                logger.error(f"Error executing code for task {task_id}: {str(e)}")
                task.update_status("failed", f"Error executing code: {str(e)}")
                
                # Add a message to the team chat
                team.add_chat_message(
                    content=f"Error executing task '{task.title}': {str(e)}",
                    sender_id=agent.id,
                    message_type="error"
                )
                
                return {"success": False, "error": str(e)}
        
        except Exception as e:
            # Handle any exceptions
            logger.error(f"Error in execute_coding_task: {str(e)}")
            task.update_status("failed", f"Error: {str(e)}")
            
            # Add a message to the team chat
            team.add_chat_message(
                content=f"Error in task '{task.title}': {str(e)}",
                sender_id=agent.id,
                message_type="error"
            )
            
            return {"success": False, "error": str(e)}
    
    async def update_task_progress(
        self,
        team_id: str,
        task_id: str,
        progress: int,
        status: Optional[str] = None,
        comment: Optional[str] = None
    ) -> bool:
        """
        Update the progress of a task.
        
        Args:
            team_id: ID of the team
            task_id: ID of the task
            progress: Progress percentage (0-100)
            status: Optional new status
            comment: Optional comment
            
        Returns:
            True if the task was updated, False otherwise
        """
        team = self.get_team(team_id)
        if team is None:
            logger.error(f"Team not found: {team_id}")
            return False
        
        # Find the agent with the task
        agent = None
        task = None
        for a in team.agents.values():
            t = a.get_task(task_id)
            if t is not None:
                agent = a
                task = t
                break
        
        if agent is None or task is None:
            logger.error(f"Task not found: {task_id}")
            return False
        
        # Update task progress
        task.update_completion_percentage(progress)
        
        # Update status if provided
        if status:
            task.update_status(status, comment)
        elif comment:
            task.add_comment(comment, agent.id)
        
        # Add a message to the team chat
        if comment:
            team.add_chat_message(
                content=f"Task '{task.title}' progress: {progress}% - {comment}",
                sender_id=agent.id,
                message_type="progress"
            )
        else:
            team.add_chat_message(
                content=f"Task '{task.title}' progress: {progress}%",
                sender_id=agent.id,
                message_type="progress"
            )
        
        # Trigger task callbacks
        await self._trigger_task_callbacks(task)
        
        return True
    
    def register_task_callback(self, callback: Callable[[AgentTask], Awaitable[None]]) -> str:
        """
        Register a callback function to be called when a task is updated.
        
        Args:
            callback: Callback function
            
        Returns:
            Callback ID
        """
        callback_id = str(uuid.uuid4())
        if "global" not in self.task_callbacks:
            self.task_callbacks["global"] = []
        self.task_callbacks["global"].append(callback)
        return callback_id
    
    def register_task_callback_for_team(self, team_id: str, callback: Callable[[AgentTask], Awaitable[None]]) -> str:
        """
        Register a callback function to be called when a task in a specific team is updated.
        
        Args:
            team_id: ID of the team
            callback: Callback function
            
        Returns:
            Callback ID
        """
        callback_id = str(uuid.uuid4())
        if team_id not in self.task_callbacks:
            self.task_callbacks[team_id] = []
        self.task_callbacks[team_id].append(callback)
        return callback_id
    
    async def _trigger_task_callbacks(self, task: AgentTask) -> None:
        """
        Trigger all registered callbacks for a task.
        
        Args:
            task: The updated task
        """
        # Find the team that contains this task
        team_id = None
        for tid, team in self.teams.items():
            for agent in team.agents.values():
                if task.id in agent.tasks:
                    team_id = tid
                    break
            if team_id:
                break
        
        # Trigger global callbacks
        if "global" in self.task_callbacks:
            for callback in self.task_callbacks["global"]:
                try:
                    await callback(task)
                except Exception as e:
                    logger.error(f"Error in task callback: {str(e)}")
        
        # Trigger team-specific callbacks
        if team_id and team_id in self.task_callbacks:
            for callback in self.task_callbacks[team_id]:
                try:
                    await callback(task)
                except Exception as e:
                    logger.error(f"Error in team-specific task callback: {str(e)}")
    
    async def send_team_message(
        self,
        team_id: str,
        content: str,
        sender_id: str,
        message_type: str = "text"
    ) -> Optional[Dict[str, Any]]:
        """
        Send a message to a team chat.
        
        Args:
            team_id: ID of the team
            content: Message content
            sender_id: ID of the sender
            message_type: Type of message
            
        Returns:
            The created message or None if the team was not found
        """
        team = self.get_team(team_id)
        if team is None:
            logger.error(f"Team not found: {team_id}")
            return None
        
        # Verify sender exists in the team
        if sender_id not in team.agents:
            logger.error(f"Sender not found in team: {sender_id}")
            return None
        
        # Add the message to the team chat
        return team.add_chat_message(content, sender_id, message_type)
    
    async def get_team_chat_history(
        self,
        team_id: str,
        limit: int = 100,
        before: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get the chat history for a team.
        
        Args:
            team_id: ID of the team
            limit: Maximum number of messages to return
            before: Return messages before this message ID
            
        Returns:
            List of messages
        """
        team = self.get_team(team_id)
        if team is None:
            logger.error(f"Team not found: {team_id}")
            return []
        
        # Get the chat history
        history = team.chat_history
        
        # Filter by before if provided
        if before:
            before_index = next((i for i, m in enumerate(history) if m["id"] == before), None)
            if before_index is not None:
                history = history[:before_index]
        
        # Apply limit
        return history[-limit:] if limit < len(history) else history
    
    def export_team_data(self, team_id: str) -> Optional[Dict[str, Any]]:
        """
        Export all data for a team.
        
        Args:
            team_id: ID of the team
            
        Returns:
            Dictionary with all team data or None if the team was not found
        """
        team = self.get_team(team_id)
        if team is None:
            logger.error(f"Team not found: {team_id}")
            return None
        
        return team.to_dict()
    
    def import_team_data(self, team_data: Dict[str, Any]) -> Optional[AgentTeam]:
        """
        Import team data.
        
        Args:
            team_data: Team data dictionary
            
        Returns:
            The imported team or None if the import failed
        """
        try:
            team = AgentTeam.from_dict(team_data)
            self.teams[team.id] = team
            return team
        except Exception as e:
            logger.error(f"Error importing team data: {str(e)}")
            return None
