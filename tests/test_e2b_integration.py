import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.services.e2b.artifacts import Artifact, ArtifactManager
from backend.app.core.services.e2b.delegation import (
    AgentDelegationService,
    AgentRole,
    AgentTask,
)
from backend.app.core.services.e2b.session import E2BSession


class TestE2BSession(unittest.TestCase):
    """Test cases for the E2BSession class."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"

        # Create mocks for the E2B SDK
        self.mock_e2b_session = MagicMock()
        self.mock_e2b_session.filesystem = MagicMock()
        self.mock_e2b_session.process = MagicMock()

        # Patch the E2B SDK
        self.patcher = patch("backend.app.core.services.e2b.session.e2b")
        self.mock_e2b = self.patcher.start()
        self.mock_e2b.Session.return_value = self.mock_e2b_session

    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher.stop()

    def test_initialization(self):
        """Test that the session initializes correctly."""
        session = E2BSession(api_key=self.api_key)

        # Check that the E2B session was created with the correct API key
        self.mock_e2b.Session.assert_called_once_with(api_key=self.api_key)

        # Check that the session has the correct attributes
        self.assertEqual(session.session, self.mock_e2b_session)
        self.assertEqual(session.filesystem, self.mock_e2b_session.filesystem)
        self.assertEqual(session.process, self.mock_e2b_session.process)

    @patch("backend.app.core.services.e2b.session.e2b")
    async def test_create_file(self, mock_e2b):
        """Test that files can be created correctly."""
        # Set up the mocks
        mock_session = MagicMock()
        mock_e2b.Session.return_value = mock_session

        mock_filesystem = MagicMock()
        mock_session.filesystem = mock_filesystem

        # Create the session
        session = E2BSession(api_key=self.api_key)

        # Create a file
        path = "/test/file.txt"
        content = "Test content"

        await session.create_file(path, content)

        # Check that the file was created
        mock_filesystem.write.assert_called_once_with(path, content)

    @patch("backend.app.core.services.e2b.session.e2b")
    async def test_read_file(self, mock_e2b):
        """Test that files can be read correctly."""
        # Set up the mocks
        mock_session = MagicMock()
        mock_e2b.Session.return_value = mock_session

        mock_filesystem = MagicMock()
        mock_session.filesystem = mock_filesystem
        mock_filesystem.read.return_value = "Test content"

        # Create the session
        session = E2BSession(api_key=self.api_key)

        # Read a file
        path = "/test/file.txt"
        content = await session.read_file(path)

        # Check that the file was read
        mock_filesystem.read.assert_called_once_with(path)
        self.assertEqual(content, "Test content")

    @patch("backend.app.core.services.e2b.session.e2b")
    async def test_list_directory(self, mock_e2b):
        """Test that directories can be listed correctly."""
        # Set up the mocks
        mock_session = MagicMock()
        mock_e2b.Session.return_value = mock_session

        mock_filesystem = MagicMock()
        mock_session.filesystem = mock_filesystem
        mock_filesystem.list.return_value = [
            {"name": "file1.txt", "type": "file"},
            {"name": "dir1", "type": "directory"},
        ]

        # Create the session
        session = E2BSession(api_key=self.api_key)

        # List a directory
        path = "/test"
        entries = await session.list_directory(path)

        # Check that the directory was listed
        mock_filesystem.list.assert_called_once_with(path)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["name"], "file1.txt")
        self.assertEqual(entries[0]["type"], "file")
        self.assertEqual(entries[1]["name"], "dir1")
        self.assertEqual(entries[1]["type"], "directory")

    @patch("backend.app.core.services.e2b.session.e2b")
    async def test_execute_command(self, mock_e2b):
        """Test that commands can be executed correctly."""
        # Set up the mocks
        mock_session = MagicMock()
        mock_e2b.Session.return_value = mock_session

        mock_process = MagicMock()
        mock_session.process = mock_process

        mock_process_instance = AsyncMock()
        mock_process.start.return_value = mock_process_instance

        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.stdout = "Test stdout"
        mock_result.stderr = ""
        mock_process_instance.wait.return_value = mock_result

        # Create the session
        session = E2BSession(api_key=self.api_key)

        # Execute a command
        cmd = ["echo", "test"]
        result = await session.execute_command(cmd)

        # Check that the command was executed
        mock_process.start.assert_called_once()
        args, kwargs = mock_process.start.call_args
        self.assertEqual(kwargs["cmd"], cmd)

        # Check that the result was returned correctly
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "Test stdout")
        self.assertEqual(result.stderr, "")


class TestArtifactManager(unittest.TestCase):
    """Test cases for the ArtifactManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for the E2B session
        self.mock_session = MagicMock()
        self.mock_session.filesystem = MagicMock()
        self.mock_session.process = MagicMock()

        # Create the artifact manager
        self.artifact_manager = ArtifactManager(self.mock_session)

    async def test_create_artifact(self):
        """Test that artifacts can be created correctly."""
        # Set up the mocks
        self.mock_session.create_file = AsyncMock()

        # Create an artifact
        content = "Test content"
        name = "test_artifact.txt"
        content_type = "text/plain"
        metadata = {"key": "value"}

        artifact = await self.artifact_manager.create_artifact(
            content=content, name=name, content_type=content_type, metadata=metadata
        )

        # Check that the artifact was created correctly
        self.assertEqual(artifact.name, name)
        self.assertEqual(artifact.content_type, content_type)
        self.assertEqual(artifact.metadata, metadata)

        # Check that the file was created
        self.mock_session.create_file.assert_called_once()

    async def test_get_artifact(self):
        """Test that artifacts can be retrieved correctly."""
        # Create an artifact
        artifact_id = "test_id"
        name = "test_artifact.txt"
        content_type = "text/plain"
        metadata = {"key": "value"}

        # Add the artifact to the manager
        artifact = Artifact(
            id=artifact_id,
            name=name,
            content_type=content_type,
            content=b"Test content",
            metadata=metadata,
        )
        self.artifact_manager.artifacts[artifact_id] = artifact

        # Get the artifact
        retrieved_artifact = await self.artifact_manager.get_artifact(artifact_id)

        # Check that the artifact was retrieved correctly
        self.assertEqual(retrieved_artifact.id, artifact_id)
        self.assertEqual(retrieved_artifact.name, name)
        self.assertEqual(retrieved_artifact.content_type, content_type)
        self.assertEqual(retrieved_artifact.metadata, metadata)

    async def test_scan_for_artifacts(self):
        """Test that artifacts can be scanned for correctly."""
        # Set up the mocks
        self.mock_session.list_directory = AsyncMock()
        self.mock_session.list_directory.return_value = [
            {"name": "file1.txt", "type": "file"},
            {"name": "dir1", "type": "directory"},
        ]

        self.mock_session.read_file = AsyncMock()
        self.mock_session.read_file.return_value = "Test content"

        # Scan for artifacts
        artifacts = await self.artifact_manager.scan_for_artifacts()

        # Check that the directory was listed
        self.mock_session.list_directory.assert_called_once()

        # Check that the file was read
        self.mock_session.read_file.assert_called_once()

        # Check that the artifact was created
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].name, "file1.txt")


class TestAgentDelegation(unittest.TestCase):
    """Test cases for the agent delegation system."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for the E2B session
        self.mock_session = MagicMock()
        self.mock_session.filesystem = MagicMock()
        self.mock_session.process = MagicMock()

        # Create a mock for the artifact manager
        self.mock_artifact_manager = MagicMock()

        # Create the delegation service
        self.delegation_service = AgentDelegationService(self.mock_session)
        self.delegation_service.artifact_manager = self.mock_artifact_manager

    def test_create_team(self):
        """Test that teams can be created correctly."""
        # Create a team
        name = "Test Team"
        supervisor_name = "Test Supervisor"
        metadata = {"key": "value"}

        team = self.delegation_service.create_team(
            name=name, supervisor_name=supervisor_name, metadata=metadata
        )

        # Check that the team was created correctly
        self.assertEqual(team.name, name)
        self.assertEqual(team.metadata, metadata)

        # Check that the supervisor was created
        supervisor = team.get_supervisor()
        self.assertIsNotNone(supervisor)
        self.assertEqual(supervisor.name, supervisor_name)
        self.assertEqual(supervisor.role, AgentRole.SUPERVISOR)

        # Check that the team was added to the service
        self.assertIn(team.id, self.delegation_service.teams)

    def test_add_agent_to_team(self):
        """Test that agents can be added to teams correctly."""
        # Create a team
        team = self.delegation_service.create_team(
            name="Test Team", supervisor_name="Test Supervisor"
        )

        # Add an agent to the team
        name = "Test Agent"
        role = AgentRole.CODER
        capabilities = ["code_execution", "language_python"]
        metadata = {"key": "value"}

        agent = self.delegation_service.add_agent_to_team(
            team_id=team.id,
            name=name,
            role=role,
            capabilities=capabilities,
            metadata=metadata,
        )

        # Check that the agent was created correctly
        self.assertEqual(agent.name, name)
        self.assertEqual(agent.role, role)
        self.assertEqual(agent.capabilities, capabilities)
        self.assertEqual(agent.metadata, metadata)

        # Check that the agent was added to the team
        self.assertIn(agent.id, team.agents)

    def test_create_coding_agent(self):
        """Test that coding agents can be created correctly."""
        # Create a team
        team = self.delegation_service.create_team(
            name="Test Team", supervisor_name="Test Supervisor"
        )

        # Create a coding agent
        name = "Test Coding Agent"
        languages = ["python", "javascript"]
        metadata = {"key": "value"}

        agent = self.delegation_service.create_coding_agent(
            team_id=team.id, name=name, languages=languages, metadata=metadata
        )

        # Check that the agent was created correctly
        self.assertEqual(agent.name, name)
        self.assertEqual(agent.role, AgentRole.CODER)
        self.assertIn("code_execution", agent.capabilities)
        self.assertIn("language_python", agent.capabilities)
        self.assertIn("language_javascript", agent.capabilities)
        self.assertEqual(agent.metadata["languages"], languages)
        self.assertTrue(agent.metadata["is_coding_agent"])

        # Check that the agent was added to the team
        self.assertIn(agent.id, team.agents)

    async def test_delegate_coding_task(self):
        """Test that coding tasks can be delegated correctly."""
        # Create a team
        team = self.delegation_service.create_team(
            name="Test Team", supervisor_name="Test Supervisor"
        )

        # Create a coding agent
        agent = self.delegation_service.create_coding_agent(
            team_id=team.id, name="Test Coding Agent", languages=["python"]
        )

        # Set up the mock for the artifact manager
        self.mock_artifact_manager.create_artifact = AsyncMock()
        mock_artifact = MagicMock()
        mock_artifact.id = "test_artifact_id"
        self.mock_artifact_manager.create_artifact.return_value = mock_artifact

        # Delegate a coding task
        title = "Test Task"
        description = "Test Description"
        language = "python"
        code = "print('Hello, World!')"
        priority = "high"
        metadata = {"key": "value"}

        task = await self.delegation_service.delegate_coding_task(
            team_id=team.id,
            title=title,
            description=description,
            language=language,
            code=code,
            priority=priority,
            metadata=metadata,
        )

        # Check that the task was created correctly
        self.assertEqual(task.title, title)
        self.assertEqual(task.description, description)
        self.assertEqual(task.priority, priority)
        self.assertEqual(task.assigned_to, agent.id)
        self.assertEqual(task.status, "pending")
        self.assertEqual(task.metadata["language"], language)
        self.assertEqual(task.metadata["initial_code"], code)

        # Check that the artifact was created
        self.mock_artifact_manager.create_artifact.assert_called_once()
        args, kwargs = self.mock_artifact_manager.create_artifact.call_args
        self.assertEqual(kwargs["content"], code)
        self.assertEqual(kwargs["metadata"]["task_id"], task.id)

        # Check that the task was assigned to the agent
        self.assertIn(task.id, agent.tasks)

    async def test_execute_coding_task(self):
        """Test that coding tasks can be executed correctly."""
        # Create a team
        team = self.delegation_service.create_team(
            name="Test Team", supervisor_name="Test Supervisor"
        )

        # Create a coding agent
        agent = self.delegation_service.create_coding_agent(
            team_id=team.id, name="Test Coding Agent", languages=["python"]
        )

        # Create a task
        task = AgentTask(
            task_id="test_task_id",
            title="Test Task",
            description="Test Description",
            assigned_to=agent.id,
            assigned_by=team.supervisor_id,
            status="pending",
            priority="high",
            metadata={"language": "python", "initial_code": "print('Hello, World!')"},
        )

        # Assign the task to the agent
        agent.assign_task(task)

        # Set up the mocks for the E2B session
        mock_process = AsyncMock()
        self.mock_session.process.start = AsyncMock(return_value=mock_process)

        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.stdout = "Hello, World!"
        mock_result.stderr = ""
        mock_process.wait.return_value = mock_result

        # Set up the mocks for the artifact manager
        self.mock_artifact_manager.create_artifact = AsyncMock()
        mock_artifact = MagicMock()
        mock_artifact.id = "test_artifact_id"
        self.mock_artifact_manager.create_artifact.return_value = mock_artifact

        self.mock_artifact_manager.scan_for_artifacts = AsyncMock(return_value=[])

        # Execute the task
        result = await self.delegation_service.execute_coding_task(team_id=team.id, task_id=task.id)

        # Check that the process was started
        self.mock_session.process.start.assert_called_once()

        # Check that the task status was updated
        self.assertEqual(task.status, "completed")

        # Check that the result was returned correctly
        self.assertTrue(result["success"])
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["stdout"], "Hello, World!")
        self.assertEqual(result["stderr"], "")


if __name__ == "__main__":
    unittest.main()
