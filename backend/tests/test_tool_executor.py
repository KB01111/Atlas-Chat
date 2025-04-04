import pytest
from unittest.mock import patch, MagicMock
import asyncio

from app.core.services.tool_executor import ToolExecutor
from app.models.models import RequestContext

@pytest.fixture
def mock_e2b_client():
    with patch('app.core.services.tool_executor.e2b.Sandbox') as mock_sandbox:
        mock_client = MagicMock()
        mock_sandbox.return_value = mock_client
        
        # Mock process methods
        mock_process = MagicMock()
        mock_process.stdout = "Test output"
        mock_process.stderr = ""
        mock_process.exit_code = 0
        
        # Setup mock methods
        mock_client.process.start.return_value = mock_process
        mock_client.filesystem.write.return_value = None
        mock_client.filesystem.read.return_value = "Test file content"
        
        yield mock_client

@pytest.fixture
def tool_executor(mock_e2b_client):
    executor = ToolExecutor()
    executor.e2b_client = mock_e2b_client
    return executor

@pytest.fixture
def request_context():
    return RequestContext(
        thread_id="test_thread",
        user_id="test_user",
        agent_definition={"agent_id": "test_agent", "allowed_tools": ["execute_code", "write_file", "read_file", "install_packages"]}
    )

@pytest.mark.asyncio
async def test_execute_code(tool_executor, request_context, mock_e2b_client):
    # Test data
    code = "print('Hello, World!')"
    language = "python"
    
    # Execute code
    result = await tool_executor.execute_code(code, language, request_context)
    
    # Check result
    assert result["success"] is True
    assert "Test output" in result["stdout"]
    assert result["exit_code"] == 0
    
    # Verify E2B client was called correctly
    mock_e2b_client.process.start.assert_called_once()
    call_args = mock_e2b_client.process.start.call_args[0]
    assert code in call_args[0]
    assert language in call_args[1]

@pytest.mark.asyncio
async def test_write_file(tool_executor, request_context, mock_e2b_client):
    # Test data
    file_path = "test.py"
    content = "print('Hello, World!')"
    
    # Write file
    result = await tool_executor.write_file(file_path, content, request_context)
    
    # Check result
    assert result["success"] is True
    
    # Verify E2B client was called correctly
    mock_e2b_client.filesystem.write.assert_called_once_with(file_path, content)

@pytest.mark.asyncio
async def test_read_file(tool_executor, request_context, mock_e2b_client):
    # Test data
    file_path = "test.py"
    
    # Read file
    result = await tool_executor.read_file(file_path, request_context)
    
    # Check result
    assert result["success"] is True
    assert result["content"] == "Test file content"
    
    # Verify E2B client was called correctly
    mock_e2b_client.filesystem.read.assert_called_once_with(file_path)

@pytest.mark.asyncio
async def test_install_packages(tool_executor, request_context, mock_e2b_client):
    # Test data
    packages = ["numpy", "pandas"]
    language = "python"
    
    # Mock process for package installation
    mock_process = MagicMock()
    mock_process.stdout = "Successfully installed numpy pandas"
    mock_process.stderr = ""
    mock_process.exit_code = 0
    mock_e2b_client.process.start.return_value = mock_process
    
    # Install packages
    result = await tool_executor.install_packages(packages, language, request_context)
    
    # Check result
    assert result["success"] is True
    assert "Successfully installed" in result["stdout"]
    
    # Verify E2B client was called correctly
    mock_e2b_client.process.start.assert_called_once()
    call_args = mock_e2b_client.process.start.call_args[0]
    assert "pip install" in call_args[0] or "npm install" in call_args[0]
    assert "numpy" in call_args[0]
    assert "pandas" in call_args[0]

@pytest.mark.asyncio
async def test_execute_code_error(tool_executor, request_context, mock_e2b_client):
    # Mock process with error
    mock_process = MagicMock()
    mock_process.stdout = ""
    mock_process.stderr = "SyntaxError: invalid syntax"
    mock_process.exit_code = 1
    mock_e2b_client.process.start.return_value = mock_process
    
    # Test data
    code = "print('Hello, World!"  # Missing closing quote
    language = "python"
    
    # Execute code
    result = await tool_executor.execute_code(code, language, request_context)
    
    # Check result
    assert result["success"] is False
    assert "SyntaxError" in result["stderr"]
    assert result["exit_code"] == 1

@pytest.mark.asyncio
async def test_sandbox_initialization_error(request_context):
    # Mock e2b.Sandbox to raise an exception
    with patch('app.core.services.tool_executor.e2b.Sandbox', side_effect=Exception("Failed to initialize sandbox")):
        executor = ToolExecutor()
        
        # Execute code should handle the error
        result = await executor.execute_code("print('test')", "python", request_context)
        
        # Check result
        assert result["success"] is False
        assert "Failed to initialize sandbox" in result["error"]

@pytest.mark.asyncio
async def test_close_sandbox(tool_executor, mock_e2b_client):
    # Close sandbox
    await tool_executor.close()
    
    # Verify E2B client was closed
    mock_e2b_client.close.assert_called_once()
