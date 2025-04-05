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
            AgentTask instance
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
        task.created_at = data.get("created_at", task.created_at)
        task.updated_at = data.get("updated_at", task.updated_at)
        task.completion_percentage = data.get("completion_percentage", 0)
        task.comments = data.get("comments", [])
        return task
    
    def update_status(self, status: str) -> None:
        """
        Update the status of the task.
        
        Args:
            status: New status of the task
        """
        self.status = status
        self.updated_at = datetime.now().isoformat()
    
    def update_progress(self, percentage: int) -> None:
        """
        Update the progress of the task.
        
        Args:
            percentage: Percentage of completion (0-100)
        """
        self.completion_percentage = max(0, min(100, percentage))
        self.updated_at = datetime.now().isoformat()
        
        # Update status based on progress
        if self.completion_percentage == 100:
            self.status = "completed"
        elif self.completion_percentage > 0:
            self.status = "in_progress"
    
    def add_comment(self, author: str, content: str) -> Dict[str, Any]:
        """
        Add a comment to the task.
        
        Args:
            author: ID of the agent or user who wrote the comment
            content: Content of the comment
            
        Returns:
            The created comment
        """
        comment = {
            "id": str(uuid.uuid4()),
            "author": author,
            "content": content,
            "created_at": datetime.now().isoformat()
        }
        self.comments.append(comment)
        self.updated_at = comment["created_at"]
        return comment
    
    def add_artifact(self, artifact_id: str) -> None:
        """
        Associate an artifact with the task.
        
        Args:
            artifact_id: ID of the artifact to associate
        """
        if artifact_id not in self.artifacts:
            self.artifacts.append(artifact_id)
            self.updated_at = datetime.now().isoformat()


class Agent:
    """
    Represents an agent in a team.
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
            role: Role of the agent in the team
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
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """
        Create an agent from a dictionary.
        
        Args:
            data: Dictionary representation of the agent
            
        Returns:
            Agent instance
        """
        agent = cls(
            agent_id=data["id"],
            name=data["name"],
            role=data["role"],
            capabilities=data["capabilities"],
            metadata=data.get("metadata", {})
        )
        agent.created_at = data.get("created_at", agent.created_at)
        
        # Add tasks
        for task_data in data.get("tasks", []):
            task = AgentTask.from_dict(task_data)
            agent.tasks[task.id] = task
            
        return agent
    
    def assign_task(self, task: AgentTask) -> None:
        """
        Assign a task to the agent.
        
        Args:
            task: Task to assign
        """
        self.tasks[task.id] = task
    
    def get_task(self, task_id: str) -> Optional[AgentTask]:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task to get
            
        Returns:
            Task if found, None otherwise
        """
        return self.tasks.get(task_id)
    
    def has_capability(self, capability: str) -> bool:
        """
        Check if the agent has a specific capability.
        
        Args:
            capability: Capability to check
            
        Returns:
            True if the agent has the capability, False otherwise
        """
        return capability in self.capabilities
    
    def has_all_capabilities(self, capabilities: List[str]) -> bool:
        """
        Check if the agent has all the specified capabilities.
        
        Args:
            capabilities: List of capabilities to check
            
        Returns:
            True if the agent has all the capabilities, False otherwise
        """
        return all(self.has_capability(cap) for cap in capabilities)
    
    def has_any_capability(self, capabilities: List[str]) -> bool:
        """
        Check if the agent has any of the specified capabilities.
        
        Args:
            capabilities: List of capabilities to check
            
        Returns:
            True if the agent has any of the capabilities, False otherwise
        """
        return any(self.has_capability(cap) for cap in capabilities)


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
        self.messages: List[Dict[str, Any]] = []
    
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
            "messages": self.messages
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentTeam':
        """
        Create a team from a dictionary.
        
        Args:
            data: Dictionary representation of the team
            
        Returns:
            AgentTeam instance
        """
        team = cls(
            team_id=data["id"],
            name=data["name"],
            supervisor_id=data["supervisor_id"],
            metadata=data.get("metadata", {})
        )
        team.created_at = data.get("created_at", team.created_at)
        team.messages = data.get("messages", [])
        
        # Add agents
        for agent_data in data.get("agents", []):
            agent = Agent.from_dict(agent_data)
            team.agents[agent.id] = agent
            
        return team
    
    def add_agent(self, agent: Agent) -> None:
        """
        Add an agent to the team.
        
        Args:
            agent: Agent to add
        """
        self.agents[agent.id] = agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: ID of the agent to get
            
        Returns:
            Agent if found, None otherwise
        """
        return self.agents.get(agent_id)
    
    def get_supervisor(self) -> Optional[Agent]:
        """
        Get the supervisor agent.
        
        Returns:
            Supervisor agent if found, None otherwise
        """
        return self.get_agent(self.supervisor_id)
    
    def get_agents_by_role(self, role: AgentRole) -> List[Agent]:
        """
        Get all agents with a specific role.
        
        Args:
            role: Role to filter by
            
        Returns:
            List of agents with the specified role
        """
        return [agent for agent in self.agents.values() if agent.role == role]
    
    def get_agents_by_capability(self, capability: str) -> List[Agent]:
        """
        Get all agents with a specific capability.
        
        Args:
            capability: Capability to filter by
            
        Returns:
            List of agents with the specified capability
        """
        return [agent for agent in self.agents.values() if agent.has_capability(capability)]
    
    def get_agents_by_capabilities(self, capabilities: List[str], require_all: bool = True) -> List[Agent]:
        """
        Get all agents with specific capabilities.
        
        Args:
            capabilities: List of capabilities to filter by
            require_all: If True, agents must have all capabilities; if False, any capability is sufficient
            
        Returns:
            List of agents with the specified capabilities
        """
        if require_all:
            return [agent for agent in self.agents.values() if agent.has_all_capabilities(capabilities)]
        else:
            return [agent for agent in self.agents.values() if agent.has_any_capability(capabilities)]
    
    def add_message(self, content: str, sender_id: str, message_type: str = "text") -> Dict[str, Any]:
        """
        Add a message to the team chat.
        
        Args:
            content: Content of the message
            sender_id: ID of the agent or user who sent the message
            message_type: Type of the message (text, code, image, etc.)
            
        Returns:
            The created message
        """
        message = {
            "id": str(uuid.uuid4()),
            "content": content,
            "sender_id": sender_id,
            "type": message_type,
            "created_at": datetime.now().isoformat()
        }
        self.messages.append(message)
        return message
    
    def get_messages(self, limit: Optional[int] = None, before: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get messages from the team chat.
        
        Args:
            limit: Maximum number of messages to return
            before: Return messages created before this timestamp
            
        Returns:
            List of messages
        """
        messages = self.messages
        
        if before:
            messages = [msg for msg in messages if msg["created_at"] < before]
            
        messages = sorted(messages, key=lambda msg: msg["created_at"], reverse=True)
        
        if limit:
            messages = messages[:limit]
            
        return messages


class AgentDelegationService:
    """
    Service for delegating tasks to agents.
    """
    
    def __init__(self, e2b_session: E2BSession):
        """
        Initialize the agent delegation service.
        
        Args:
            e2b_session: E2B session for executing code and managing files
        """
        self.e2b_session = e2b_session
        self.artifact_manager = ArtifactManager(e2b_session)
        self.teams: Dict[str, AgentTeam] = {}
        self.task_callbacks: Dict[str, List[Callable[[AgentTask], Awaitable[None]]]] = {}
    
    async def initialize(self) -> None:
        """
        Initialize the agent delegation service.
        """
        await self.artifact_manager.initialize()
    
    def create_team(self, name: str, supervisor_name: str, metadata: Optional[Dict[str, Any]] = None) -> AgentTeam:
        """
        Create a new team with a supervisor.
        
        Args:
            name: Name of the team
            supervisor_name: Name of the supervisor agent
            metadata: Additional metadata for the team
            
        Returns:
            The created team
        """
        team_id = str(uuid.uuid4())
        supervisor_id = str(uuid.uuid4())
        
        team = AgentTeam(
            team_id=team_id,
            name=name,
            supervisor_id=supervisor_id,
            metadata=metadata
        )
        
        supervisor = Agent(
            agent_id=supervisor_id,
            name=supervisor_name,
            role=AgentRole.SUPERVISOR,
            capabilities=["task_delegation", "team_management"],
            metadata={"is_supervisor": True}
        )
        
        team.add_agent(supervisor)
        self.teams[team_id] = team
        
        return team
    
    def get_team(self, team_id: str) -> Optional[AgentTeam]:
        """
        Get a team by ID.
        
        Args:
            team_id: ID of the team to get
            
        Returns:
            Team if found, None otherwise
        """
        return self.teams.get(team_id)
    
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
            team_id: ID of the team to add the agent to
            name: Name of the agent
            role: Role of the agent in the team
            capabilities: List of capabilities the agent has
            metadata: Additional metadata for the agent
            
        Returns:
            The created agent if successful, None otherwise
        """
        team = self.get_team(team_id)
        if not team:
            logger.error(f"Team with ID {team_id} not found")
            return None
        
        agent_id = str(uuid.uuid4())
        agent = Agent(
            agent_id=agent_id,
            name=name,
            role=role,
            capabilities=capabilities,
            metadata=metadata
        )
        
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
            team_id: ID of the team to add the agent to
            name: Name of the agent
            languages: List of programming languages the agent can work with
            metadata: Additional metadata for the agent
            
        Returns:
            The created agent if successful, None otherwise
        """
        if metadata is None:
            metadata = {}
            
        metadata["languages"] = languages
        metadata["is_coding_agent"] = True
        
        capabilities = ["code_execution"]
        for lang in languages:
            capabilities.append(f"language_{lang.lower()}")
        
        return self.add_agent_to_team(
            team_id=team_id,
            name=name,
            role=AgentRole.CODER,
            capabilities=capabilities,
            metadata=metadata
        )
    
    async def delegate_task(
        self,
        team_id: str,
        title: str,
        description: str,
        required_capabilities: List[str],
        priority: str = "medium",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[AgentTask]:
        """
        Delegate a task to an appropriate agent in the team.
        
        Args:
            team_id: ID of the team to delegate the task to
            title: Title of the task
            description: Description of the task
            required_capabilities: List of capabilities required to complete the task
            priority: Priority of the task (low, medium, high, critical)
            metadata: Additional metadata for the task
            
        Returns:
            The created task if successful, None otherwise
        """
        team = self.get_team(team_id)
        if not team:
            logger.error(f"Team with ID {team_id} not found")
            return None
        
        supervisor = team.get_supervisor()
        if not supervisor:
            logger.error(f"Supervisor not found for team {team_id}")
            return None
        
        # Find agents with the required capabilities
        agents = team.get_agents_by_capabilities(required_capabilities)
        if not agents:
            logger.error(f"No agents found with capabilities {required_capabilities}")
            return None
        
        # Choose the agent with the fewest tasks
        agent = min(agents, key=lambda a: len(a.tasks))
        
        # Create the task
        task_id = str(uuid.uuid4())
        task = AgentTask(
            task_id=task_id,
            title=title,
            description=description,
            assigned_to=agent.id,
            assigned_by=supervisor.id,
            status="pending",
            priority=priority,
            metadata=metadata
        )
        
        # Assign the task to the agent
        agent.assign_task(task)
        
        return task
    
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
            team_id: ID of the team to delegate the task to
            title: Title of the task
            description: Description of the task
            language: Programming language for the task
            code: Initial code for the task
            priority: Priority of the task (low, medium, high, critical)
            metadata: Additional metadata for the task
            
        Returns:
            The created task if successful, None otherwise
        """
        if metadata is None:
            metadata = {}
            
        metadata["language"] = language
        if code:
            metadata["initial_code"] = code
        
        required_capabilities = [f"language_{language.lower()}", "code_execution"]
        
        task = await self.delegate_task(
            team_id=team_id,
            title=title,
            description=description,
            required_capabilities=required_capabilities,
            priority=priority,
            metadata=metadata
        )
        
        if task and code:
            # Create an artifact for the initial code
            artifact = await self.artifact_manager.create_artifact(
                content=code,
                name=f"initial_code_{task.id}.{language.lower()}",
                content_type=f"text/{language.lower()}",
                metadata={"task_id": task.id, "type": "initial_code"}
            )
            
            # Associate the artifact with the task
            task.add_artifact(artifact.id)
        
        return task
    
    async def execute_coding_task(self, team_id: str, task_id: str) -> Dict[str, Any]:
        """
        Execute a coding task using the E2B code interpreter.
        
        Args:
            team_id: ID of the team containing the task
            task_id: ID of the task to execute
            
        Returns:
            Result of the execution
        """
        team = self.get_team(team_id)
        if not team:
            return {"success": False, "error": f"Team with ID {team_id} not found"}
        
        # Find the agent assigned to the task
        agent = None
        task = None
        for a in team.agents.values():
            t = a.get_task(task_id)
            if t:
                agent = a
                task = t
                break
        
        if not task:
            return {"success": False, "error": f"Task with ID {task_id} not found"}
        
        if not agent:
            return {"success": False, "error": f"Agent assigned to task {task_id} not found"}
        
        # Update task status
        task.update_status("in_progress")
        await self._notify_task_update(task)
        
        # Get the code to execute
        code = task.metadata.get("initial_code", "")
        language = task.metadata.get("language", "python").lower()
        
        # Create a file for the code
        file_name = f"task_{task_id}.{language}"
        file_path = f"/tmp/{file_name}"
        await self.e2b_session.create_file(file_path, code)
        
        # Execute the code
        result = {"success": False, "error": "Execution failed"}
        
        try:
            if language == "python":
                process = await self.e2b_session.process.start(cmd=["python3", file_path])
            elif language == "javascript" or language == "js":
                process = await self.e2b_session.process.start(cmd=["node", file_path])
            elif language == "typescript" or language == "ts":
                # Compile TypeScript to JavaScript first
                await self.e2b_session.process.start(cmd=["tsc", file_path])
                js_file_path = file_path.replace(".ts", ".js")
                process = await self.e2b_session.process.start(cmd=["node", js_file_path])
            elif language == "bash" or language == "sh":
                process = await self.e2b_session.process.start(cmd=["bash", file_path])
            else:
                return {"success": False, "error": f"Unsupported language: {language}"}
            
            execution_result = await process.wait()
            
            result = {
                "success": execution_result.exit_code == 0,
                "exit_code": execution_result.exit_code,
                "stdout": execution_result.stdout,
                "stderr": execution_result.stderr
            }
            
            # Update task status based on execution result
            if result["success"]:
                task.update_status("completed")
                task.update_progress(100)
            else:
                task.update_status("failed")
                
            # Add a comment with the execution result
            if result["success"]:
                task.add_comment(
                    author=agent.id,
                    content=f"Task executed successfully. Output:\n```\n{result['stdout']}\n```"
                )
            else:
                task.add_comment(
                    author=agent.id,
                    content=f"Task execution failed. Error:\n```\n{result['stderr']}\n```"
                )
            
            # Scan for artifacts created during execution
            artifacts = await self.artifact_manager.scan_for_artifacts()
            for artifact in artifacts:
                task.add_artifact(artifact.id)
            
            await self._notify_task_update(task)
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            task.update_status("failed")
            task.add_comment(
                author=agent.id,
                content=f"Task execution failed with exception: {str(e)}"
            )
            await self._notify_task_update(task)
            result = {"success": False, "error": str(e)}
        
        return result
    
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
            team_id: ID of the team containing the task
            task_id: ID of the task to update
            progress: Percentage of completion (0-100)
            status: New status of the task (optional)
            comment: Comment to add to the task (optional)
            
        Returns:
            True if successful, False otherwise
        """
        team = self.get_team(team_id)
        if not team:
            logger.error(f"Team with ID {team_id} not found")
            return False
        
        # Find the agent assigned to the task
        agent = None
        task = None
        for a in team.agents.values():
            t = a.get_task(task_id)
            if t:
                agent = a
                task = t
                break
        
        if not task:
            logger.error(f"Task with ID {task_id} not found")
            return False
        
        if not agent:
            logger.error(f"Agent assigned to task {task_id} not found")
            return False
        
        # Update task progress
        task.update_progress(progress)
        
        # Update task status if provided
        if status:
            task.update_status(status)
        
        # Add comment if provided
        if comment:
            task.add_comment(author=agent.id, content=comment)
        
        # Notify task update
        await self._notify_task_update(task)
        
        return True
    
    def register_task_callback(self, callback: Callable[[AgentTask], Awaitable[None]]) -> str:
        """
        Register a callback function to be called when a task is updated.
        
        Args:
            callback: Callback function that takes a task as argument
            
        Returns:
            ID of the registered callback
        """
        callback_id = str(uuid.uuid4())
        if "all" not in self.task_callbacks:
            self.task_callbacks["all"] = []
        self.task_callbacks["all"].append(callback)
        return callback_id
    
    def register_task_callback_for_team(self, team_id: str, callback: Callable[[AgentTask], Awaitable[None]]) -> str:
        """
        Register a callback function to be called when a task in a specific team is updated.
        
        Args:
            team_id: ID of the team to register the callback for
            callback: Callback function that takes a task as argument
            
        Returns:
            ID of the registered callback
        """
        callback_id = str(uuid.uuid4())
        if team_id not in self.task_callbacks:
            self.task_callbacks[team_id] = []
        self.task_callbacks[team_id].append(callback)
        return callback_id
    
    async def _notify_task_update(self, task: AgentTask) -> None:
        """
        Notify all registered callbacks about a task update.
        
        Args:
            task: Updated task
        """
        # Get the team ID for the task
        team_id = None
        for tid, team in self.teams.items():
            for agent in team.agents.values():
                if task.id in agent.tasks:
                    team_id = tid
                    break
            if team_id:
                break
        
        if not team_id:
            logger.error(f"Team not found for task {task.id}")
            return
        
        # Call team-specific callbacks
        if team_id in self.task_callbacks:
            for callback in self.task_callbacks[team_id]:
                try:
                    await callback(task)
                except Exception as e:
                    logger.error(f"Error in task callback: {str(e)}")
        
        # Call global callbacks
        if "all" in self.task_callbacks:
            for callback in self.task_callbacks["all"]:
                try:
                    await callback(task)
                except Exception as e:
                    logger.error(f"Error in task callback: {str(e)}")
    
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
            team_id: ID of the team to send the message to
            content: Content of the message
            sender_id: ID of the agent or user who sent the message
            message_type: Type of the message (text, code, image, etc.)
            
        Returns:
            The created message if successful, None otherwise
        """
        team = self.get_team(team_id)
        if not team:
            logger.error(f"Team with ID {team_id} not found")
            return None
        
        # Check if sender is a member of the team or a user
        if sender_id not in team.agents and not sender_id.startswith("user_"):
            logger.error(f"Sender {sender_id} is not a member of team {team_id}")
            return None
        
        return team.add_message(content=content, sender_id=sender_id, message_type=message_type)
    
    def get_team_messages(
        self,
        team_id: str,
        limit: Optional[int] = None,
        before: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get messages from a team chat.
        
        Args:
            team_id: ID of the team to get messages from
            limit: Maximum number of messages to return
            before: Return messages created before this timestamp
            
        Returns:
            List of messages
        """
        team = self.get_team(team_id)
        if not team:
            logger.error(f"Team with ID {team_id} not found")
            return []
        
        return team.get_messages(limit=limit, before=before)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent delegation service to a dictionary.
        
        Returns:
            Dictionary representation of the agent delegation service
        """
        return {
            "teams": [team.to_dict() for team in self.teams.values()]
        }
    
    @classmethod
    async def from_dict(cls, data: Dict[str, Any], e2b_session: E2BSession) -> 'AgentDelegationService':
        """
        Create an agent delegation service from a dictionary.
        
        Args:
            data: Dictionary representation of the agent delegation service
            e2b_session: E2B session for executing code and managing files
            
        Returns:
            AgentDelegationService instance
        """
        service = cls(e2b_session=e2b_session)
        await service.initialize()
        
        # Add teams
        for team_data in data.get("teams", []):
            team = AgentTeam.from_dict(team_data)
            service.teams[team.id] = team
            
        return service
    
    async def save_state(self, file_path: str) -> None:
        """
        Save the state of the agent delegation service to a file.
        
        Args:
            file_path: Path to save the state to
        """
        state = self.to_dict()
        await self.e2b_session.create_file(file_path, json.dumps(state, indent=2))
    
    @classmethod
    async def load_state(cls, file_path: str, e2b_session: E2BSession) -> 'AgentDelegationService':
        """
        Load the state of the agent delegation service from a file.
        
        Args:
            file_path: Path to load the state from
            e2b_session: E2B session for executing code and managing files
            
        Returns:
            AgentDelegationService instance
        """
        try:
            state_json = await e2b_session.read_file(file_path)
            state = json.loads(state_json)
            return await cls.from_dict(state, e2b_session)
        except Exception as e:
            logger.error(f"Error loading state: {str(e)}")
            service = cls(e2b_session=e2b_session)
            await service.initialize()
            return service
