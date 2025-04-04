import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.core.services.agent_service import AgentService
from app.models.models import RequestContext

# Create test client
client = TestClient(app)

# Mock JWT token for authentication
mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXJfaWQiLCJleHAiOjk5OTk5OTk5OTl9.mock_signature"

@pytest.fixture
def mock_agent_service():
    with patch("app.api.chat.AgentService") as mock_service_class:
        mock_service = MagicMock(spec=AgentService)
        mock_service_class.return_value = mock_service
        yield mock_service

def test_chat_endpoint(mock_agent_service):
    # Setup mock to return a generator
    async def mock_handle_chat_request(*args, **kwargs):
        yield '{"type": "message", "content": "Hello, I am an AI assistant."}'
        yield '{"type": "message", "content": "How can I help you today?"}'
    
    mock_agent_service.handle_chat_request.return_value = mock_handle_chat_request()
    
    # Test data
    test_data = {
        "agent_id": "test_agent",
        "message": "Hello",
        "history": []
    }
    
    # Make request
    response = client.post(
        "/api/chat",
        json=test_data,
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    # Check response
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    
    # Parse the streaming response
    content = response.content.decode("utf-8")
    assert "Hello, I am an AI assistant" in content
    assert "How can I help you today" in content
    
    # Verify handle_chat_request was called with correct arguments
    mock_agent_service.handle_chat_request.assert_called_once_with(
        agent_id="test_agent",
        message="Hello",
        history=[],
        user_id="test_user_id"
    )

def test_chat_endpoint_unauthorized():
    # Test data
    test_data = {
        "agent_id": "test_agent",
        "message": "Hello",
        "history": []
    }
    
    # Make request without authorization header
    response = client.post(
        "/api/chat",
        json=test_data
    )
    
    # Check response
    assert response.status_code == 403  # Unauthorized

def test_chat_endpoint_invalid_request():
    # Test data with missing required fields
    test_data = {
        "message": "Hello"
        # Missing agent_id
    }
    
    # Make request
    response = client.post(
        "/api/chat",
        json=test_data,
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    # Check response
    assert response.status_code == 422  # Unprocessable Entity

def test_agents_endpoint():
    # TODO: Implement test for /api/agents endpoint
    pass

def test_agent_endpoint():
    # TODO: Implement test for /api/agents/{agent_id} endpoint
    pass
