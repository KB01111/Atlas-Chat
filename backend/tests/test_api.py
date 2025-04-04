import pytest
from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/api/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_agent_definitions_list():
    """Test listing agent definitions"""
    response = client.get("/api/agents")
    assert response.status_code == 200
    agents = response.json()
    assert isinstance(agents, list)
    assert len(agents) > 0
    
    # Check that each agent has the required fields
    for agent in agents:
        assert "agent_id" in agent
        assert "name" in agent
        assert "description" in agent
        assert "agent_type" in agent
        assert "uses_graphiti" in agent
        assert "allowed_tools" in agent

def test_agent_definition_detail():
    """Test getting a specific agent definition"""
    # First get the list of agents
    response = client.get("/api/agents")
    agents = response.json()
    
    # Then get the first agent's details
    first_agent_id = agents[0]["agent_id"]
    response = client.get(f"/api/agents/{first_agent_id}")
    assert response.status_code == 200
    agent = response.json()
    
    # Check that the agent has the required fields
    assert agent["agent_id"] == first_agent_id
    assert "name" in agent
    assert "description" in agent
    assert "agent_type" in agent
    assert "uses_graphiti" in agent
    assert "allowed_tools" in agent
    
    # Check additional fields based on agent_type
    if agent["agent_type"] == "sdk":
        assert "sdk_config" in agent
    elif agent["agent_type"] == "langgraph":
        assert "langgraph_definition" in agent

def test_agent_definition_not_found():
    """Test getting a non-existent agent definition"""
    response = client.get("/api/agents/non_existent_id")
    assert response.status_code == 404

def test_create_agent_definition():
    """Test creating a new agent definition"""
    new_agent = {
        "name": "Test Agent",
        "description": "A test agent created via API",
        "agent_type": "sdk",
        "uses_graphiti": False,
        "allowed_tools": ["execute_code", "web_search"]
    }
    
    response = client.post("/api/agents", json=new_agent)
    assert response.status_code == 201
    created_agent = response.json()
    
    # Check that the created agent has the required fields
    assert "agent_id" in created_agent
    assert created_agent["name"] == new_agent["name"]
    assert created_agent["description"] == new_agent["description"]
    assert created_agent["agent_type"] == new_agent["agent_type"]
    assert created_agent["uses_graphiti"] == new_agent["uses_graphiti"]
    assert created_agent["allowed_tools"] == new_agent["allowed_tools"]

def test_update_agent_definition():
    """Test updating an agent definition"""
    # First create a new agent
    new_agent = {
        "name": "Agent to Update",
        "description": "An agent that will be updated",
        "agent_type": "sdk",
        "uses_graphiti": False,
        "allowed_tools": ["execute_code"]
    }
    
    response = client.post("/api/agents", json=new_agent)
    created_agent = response.json()
    agent_id = created_agent["agent_id"]
    
    # Now update the agent
    updated_agent = {
        "name": "Updated Agent",
        "description": "This agent has been updated",
        "agent_type": "sdk",
        "uses_graphiti": True,
        "allowed_tools": ["execute_code", "web_search", "search_graphiti"]
    }
    
    response = client.put(f"/api/agents/{agent_id}", json=updated_agent)
    assert response.status_code == 200
    updated = response.json()
    
    # Check that the agent was updated correctly
    assert updated["agent_id"] == agent_id
    assert updated["name"] == updated_agent["name"]
    assert updated["description"] == updated_agent["description"]
    assert updated["uses_graphiti"] == updated_agent["uses_graphiti"]
    assert updated["allowed_tools"] == updated_agent["allowed_tools"]

def test_delete_agent_definition():
    """Test deleting an agent definition"""
    # First create a new agent
    new_agent = {
        "name": "Agent to Delete",
        "description": "An agent that will be deleted",
        "agent_type": "sdk",
        "uses_graphiti": False,
        "allowed_tools": ["execute_code"]
    }
    
    response = client.post("/api/agents", json=new_agent)
    created_agent = response.json()
    agent_id = created_agent["agent_id"]
    
    # Now delete the agent
    response = client.delete(f"/api/agents/{agent_id}")
    assert response.status_code == 204
    
    # Verify that the agent is gone
    response = client.get(f"/api/agents/{agent_id}")
    assert response.status_code == 404

def test_auth_endpoints():
    """Test authentication endpoints"""
    # Test registration
    user_data = {
        "email": "testuser@example.com",
        "username": "testuser2",
        "password": "securepassword123"
    }
    
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    result = response.json()
    assert "user_id" in result
    assert result["email"] == user_data["email"]
    assert result["username"] == user_data["username"]
    
    # Test login
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    
    response = client.post("/api/auth/token", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["email"] == user_data["email"]
    
    # Test getting current user info
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    user_info = response.json()
    assert user_info["email"] == user_data["email"]
    assert user_info["username"] == user_data["username"]

def test_chat_endpoint():
    """Test the chat endpoint"""
    # Create a chat request
    chat_request = {
        "agent_id": "sdk_test",
        "message": "Hello, how are you?",
        "history": []
    }
    
    response = client.post("/api/chat", json=chat_request)
    assert response.status_code == 200
    
    # The response should be a streaming response, so we can't easily check the content
    # In a real test, we would use a streaming client to read the response
    # For now, just check that we get a response
    assert response.content
