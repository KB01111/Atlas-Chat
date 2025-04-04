import pytest
from fastapi.testclient import TestClient
import os
import json
from unittest.mock import patch, MagicMock

from app.main import app
from app.core.security import create_access_token

# Create test client
client = TestClient(app)

# Mock test user
TEST_USER = {
    "id": "test-user-id",
    "name": "Test User",
    "email": "test@example.com"
}

# Create test token
def get_test_token():
    return create_access_token({"sub": TEST_USER["id"]})

# Mock database session
@pytest.fixture
def mock_db_session():
    with patch("app.core.database.get_db_session") as mock:
        session = MagicMock()
        mock.return_value.__aenter__.return_value = session
        mock.return_value.__aexit__.return_value = None
        yield session

# Mock E2B sandbox
@pytest.fixture
def mock_e2b_sandbox():
    with patch("app.core.services.tool_executor.ToolExecutor._create_sandbox") as mock:
        sandbox = MagicMock()
        sandbox.filesystem.write_file.return_value = None
        sandbox.filesystem.read_file.return_value = "file content"
        sandbox.process.start.return_value.stdout = "Hello, World!"
        sandbox.process.start.return_value.stderr = ""
        sandbox.process.start.return_value.exit_code = 0
        mock.return_value = sandbox
        yield sandbox

# Test health endpoint
def test_health_endpoint():
    response = client.get("/api/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# Test authentication
def test_login_endpoint(mock_db_session):
    # Mock user query
    mock_db_session.query.return_value.filter.return_value.first.return_value = MagicMock(
        id=TEST_USER["id"],
        email=TEST_USER["email"],
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # "password"
    )
    
    # Test successful login
    response = client.post(
        "/api/auth/login",
        data={"username": TEST_USER["email"], "password": "password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    
    # Test failed login
    response = client.post(
        "/api/auth/login",
        data={"username": TEST_USER["email"], "password": "wrong-password"}
    )
    assert response.status_code == 401

# Test user info endpoint
def test_user_info_endpoint(mock_db_session):
    # Mock user query
    mock_db_session.query.return_value.filter.return_value.first.return_value = MagicMock(
        id=TEST_USER["id"],
        name=TEST_USER["name"],
        email=TEST_USER["email"],
        created_at="2023-01-01T00:00:00"
    )
    
    # Test with valid token
    token = get_test_token()
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == TEST_USER["id"]
    assert response.json()["name"] == TEST_USER["name"]
    assert response.json()["email"] == TEST_USER["email"]
    
    # Test with invalid token
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 403

# Test agent endpoints
def test_get_agents_endpoint(mock_db_session):
    # Mock agents query
    mock_db_session.query.return_value.all.return_value = [
        MagicMock(
            id="agent-1",
            name="Test Agent 1",
            description="Description 1",
            agent_type="sdk",
            uses_graphiti=False,
            allowed_tools=["execute_code"]
        ),
        MagicMock(
            id="agent-2",
            name="Test Agent 2",
            description="Description 2",
            agent_type="langgraph",
            uses_graphiti=True,
            allowed_tools=["execute_code", "search_graphiti"]
        )
    ]
    
    # Test with valid token
    token = get_test_token()
    response = client.get(
        "/api/agents",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["id"] == "agent-1"
    assert response.json()[1]["id"] == "agent-2"

# Test code execution
def test_code_execution_endpoint(mock_db_session, mock_e2b_sandbox):
    # Mock agent query
    mock_db_session.query.return_value.filter.return_value.first.return_value = MagicMock(
        id="agent-1",
        name="Test Agent",
        agent_type="sdk",
        uses_graphiti=False,
        allowed_tools=["execute_code"]
    )
    
    # Test with valid token and code
    token = get_test_token()
    response = client.post(
        "/api/code/execute",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": "print('Hello, World!')",
            "language": "python",
            "thread_id": "test-thread",
            "agent_id": "agent-1"
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert "Hello, World!" in response.json()["stdout"]
    
    # Test with invalid code
    response = client.post(
        "/api/code/execute",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": "import os; os.system('rm -rf /')",  # Should be blocked
            "language": "python",
            "thread_id": "test-thread",
            "agent_id": "agent-1"
        }
    )
    assert response.status_code == 400
    assert response.json()["success"] == False
    assert "security" in response.json()["error"].lower()

# Test file operations
def test_file_operations(mock_db_session, mock_e2b_sandbox):
    # Mock agent query
    mock_db_session.query.return_value.filter.return_value.first.return_value = MagicMock(
        id="agent-1",
        name="Test Agent",
        agent_type="sdk",
        uses_graphiti=False,
        allowed_tools=["execute_code"]
    )
    
    token = get_test_token()
    
    # Test write file
    response = client.post(
        "/api/code/write-file",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "file_path": "workspace/test.py",
            "content": "print('Hello, World!')",
            "thread_id": "test-thread",
            "agent_id": "agent-1"
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    
    # Test read file
    response = client.post(
        "/api/code/read-file",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "file_path": "workspace/test.py",
            "thread_id": "test-thread",
            "agent_id": "agent-1"
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["content"] == "file content"
    
    # Test invalid file path
    response = client.post(
        "/api/code/write-file",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "file_path": "../etc/passwd",  # Should be blocked
            "content": "test",
            "thread_id": "test-thread",
            "agent_id": "agent-1"
        }
    )
    assert response.status_code == 400
    assert response.json()["success"] == False
    assert "path" in response.json()["error"].lower()

# Test chat endpoint
def test_chat_endpoint(mock_db_session):
    # Mock agent query
    mock_db_session.query.return_value.filter.return_value.first.return_value = MagicMock(
        id="agent-1",
        name="Test Agent",
        agent_type="sdk",
        uses_graphiti=False,
        allowed_tools=["execute_code"],
        sdk_config={"model": "gpt-4"}
    )
    
    # Mock agent service
    with patch("app.api.chat.AgentService") as MockAgentService:
        # Configure the mock
        mock_service = MagicMock()
        MockAgentService.return_value = mock_service
        
        # Configure handle_chat_request to return an async generator
        async def mock_generator():
            yield "Hello"
            yield " "
            yield "World"
        
        mock_service.handle_chat_request.return_value = mock_generator()
        
        # Test with valid token
        token = get_test_token()
        response = client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "agent_id": "agent-1",
                "message": "Hello, AI!",
                "history": []
            },
            stream=True
        )
        assert response.status_code == 200
        
        # Read streaming response
        content = b""
        for chunk in response.iter_content():
            content += chunk
        
        # Check content
        assert b"Hello World" in content

# Run all tests
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
