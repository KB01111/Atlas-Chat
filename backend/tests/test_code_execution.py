import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.models.models import RequestContext
from app.core.services.tool_executor import ToolExecutor

# Create test client
client = TestClient(app)

# Mock JWT token for authentication
mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXJfaWQiLCJleHAiOjk5OTk5OTk5OTl9.mock_signature"

# Mock E2B response
class MockE2BResponse:
    def __init__(self, stdout="", stderr="", exit_code=0):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code

@pytest.fixture
def mock_tool_executor():
    with patch("app.api.code.get_tool_executor") as mock_get_tool_executor:
        mock_executor = MagicMock(spec=ToolExecutor)
        mock_get_tool_executor.return_value.__enter__.return_value = mock_executor
        mock_get_tool_executor.return_value.__exit__.return_value = None
        yield mock_executor

def test_execute_code_success(mock_tool_executor):
    # Mock the execute_code method to return a successful result
    mock_tool_executor.execute_code.return_value = {
        "success": True,
        "stdout": "Hello, World!",
        "stderr": "",
        "exit_code": 0
    }
    
    # Test data
    test_data = {
        "code": "print('Hello, World!')",
        "language": "python",
        "thread_id": "test_thread",
        "agent_id": "test_agent"
    }
    
    # Make request
    response = client.post(
        "/code/execute",
        json=test_data,
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "stdout": "Hello, World!",
        "stderr": "",
        "exit_code": 0
    }
    
    # Verify execute_code was called with correct arguments
    mock_tool_executor.execute_code.assert_called_once()
    args, kwargs = mock_tool_executor.execute_code.call_args
    assert kwargs["code"] == test_data["code"]
    assert kwargs["language"] == test_data["language"]
    assert isinstance(kwargs["context"], RequestContext)
    assert kwargs["context"].thread_id == test_data["thread_id"]
    assert kwargs["context"].agent_definition["agent_id"] == test_data["agent_id"]

def test_execute_code_error(mock_tool_executor):
    # Mock the execute_code method to return an error result
    mock_tool_executor.execute_code.return_value = {
        "success": False,
        "error": "Syntax error"
    }
    
    # Test data
    test_data = {
        "code": "print('Hello, World!'",  # Missing closing parenthesis
        "language": "python",
        "thread_id": "test_thread",
        "agent_id": "test_agent"
    }
    
    # Make request
    response = client.post(
        "/code/execute",
        json=test_data,
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        "success": False,
        "error": "Syntax error"
    }

def test_write_file_success(mock_tool_executor):
    # Mock the write_file method to return a successful result
    mock_tool_executor.write_file.return_value = {
        "success": True
    }
    
    # Test data
    test_data = {
        "file_path": "test.py",
        "content": "print('Hello, World!')",
        "thread_id": "test_thread",
        "agent_id": "test_agent"
    }
    
    # Make request
    response = client.post(
        "/code/write-file",
        json=test_data,
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        "success": True
    }
    
    # Verify write_file was called with correct arguments
    mock_tool_executor.write_file.assert_called_once()
    args, kwargs = mock_tool_executor.write_file.call_args
    assert kwargs["file_path"] == test_data["file_path"]
    assert kwargs["content"] == test_data["content"]
    assert isinstance(kwargs["context"], RequestContext)
    assert kwargs["context"].thread_id == test_data["thread_id"]
    assert kwargs["context"].agent_definition["agent_id"] == test_data["agent_id"]

def test_read_file_success(mock_tool_executor):
    # Mock the read_file method to return a successful result
    mock_tool_executor.read_file.return_value = {
        "success": True,
        "content": "print('Hello, World!')"
    }
    
    # Test data
    test_data = {
        "file_path": "test.py",
        "thread_id": "test_thread",
        "agent_id": "test_agent"
    }
    
    # Make request
    response = client.post(
        "/code/read-file",
        json=test_data,
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "content": "print('Hello, World!')"
    }
    
    # Verify read_file was called with correct arguments
    mock_tool_executor.read_file.assert_called_once()
    args, kwargs = mock_tool_executor.read_file.call_args
    assert kwargs["file_path"] == test_data["file_path"]
    assert isinstance(kwargs["context"], RequestContext)
    assert kwargs["context"].thread_id == test_data["thread_id"]
    assert kwargs["context"].agent_definition["agent_id"] == test_data["agent_id"]

def test_install_packages_success(mock_tool_executor):
    # Mock the install_packages method to return a successful result
    mock_tool_executor.install_packages.return_value = {
        "success": True,
        "stdout": "Successfully installed numpy-1.24.3",
        "stderr": ""
    }
    
    # Test data
    test_data = {
        "packages": ["numpy"],
        "language": "python",
        "thread_id": "test_thread",
        "agent_id": "test_agent"
    }
    
    # Make request
    response = client.post(
        "/code/install-packages",
        json=test_data,
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "stdout": "Successfully installed numpy-1.24.3",
        "stderr": ""
    }
    
    # Verify install_packages was called with correct arguments
    mock_tool_executor.install_packages.assert_called_once()
    args, kwargs = mock_tool_executor.install_packages.call_args
    assert kwargs["packages"] == test_data["packages"]
    assert kwargs["language"] == test_data["language"]
    assert isinstance(kwargs["context"], RequestContext)
    assert kwargs["context"].thread_id == test_data["thread_id"]
    assert kwargs["context"].agent_definition["agent_id"] == test_data["agent_id"]

def test_unauthorized_access():
    # Test data
    test_data = {
        "code": "print('Hello, World!')",
        "language": "python",
        "thread_id": "test_thread",
        "agent_id": "test_agent"
    }
    
    # Make request without authorization header
    response = client.post(
        "/code/execute",
        json=test_data
    )
    
    # Check response
    assert response.status_code == 403  # Unauthorized

def test_invalid_request_data(mock_tool_executor):
    # Test data with missing required fields
    test_data = {
        "code": "print('Hello, World!')",
        # Missing language, thread_id, agent_id
    }
    
    # Make request
    response = client.post(
        "/code/execute",
        json=test_data,
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    # Check response
    assert response.status_code == 422  # Unprocessable Entity
