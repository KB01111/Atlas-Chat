import pytest
from fastapi.testclient import TestClient

# Assuming your FastAPI app instance is defined in 'backend.main.app'
# Adjust the import path if necessary
try:
    from backend.main import app
except ImportError:
    # Fallback if the structure is different, adjust as needed
    # This might happen if tests are run from a different context
    # You might need to adjust sys.path or use relative imports carefully
    print("Warning: Could not import 'app' from 'backend.main'. TestClient setup might fail.")
    app = None  # Avoid crashing if import fails, but tests will likely fail


# Fixture for the TestClient
@pytest.fixture(scope="module")
def client():
    if app:
        with TestClient(app) as c:
            yield c
    else:
        pytest.fail("FastAPI app instance could not be imported.")


# Fixture to get auth token (replace with your actual auth logic)
@pytest.fixture(scope="module")
def auth_headers(client: TestClient):
    # Replace with actual user/password and login logic
    test_username = "testuser@example.com"
    test_password = "testpassword"
    try:
        # Attempt registration first (optional, depends on test setup)
        # client.post("/api/auth/register", json={"email": test_username, "password": test_password})

        # Login to get token
        response = client.post(
            "/api/auth/token",
            data={"username": test_username, "password": test_password},
        )
        response.raise_for_status()  # Raise exception for 4xx/5xx errors
        token_data = response.json()
        token = token_data.get("access_token")
        if not token:
            pytest.fail("Failed to retrieve access token during login.")
        return {"Authorization": f"Bearer {token}"}
    except Exception as e:
        pytest.fail(
            f"Authentication setup failed: {e}. Ensure test user exists or registration works."
        )


# --- Agent Definition Tests ---

# Store created agent ID for subsequent tests
created_agent_id: str = None


def test_create_agent(client: TestClient, auth_headers: dict):
    """Test POST /api/agents - Create a new agent definition"""
    global created_agent_id
    agent_data = {
        "agent_id": "test_agent_001",
        "name": "Test Agent",
        "description": "An agent created for testing",
        "version": "1.0",
        "tools": ["tool1", "tool2"],
        "config": {"model": "test-model"},
        # Add other required fields based on your AgentDefinition model
    }
    response = client.post("/api/agents", json=agent_data, headers=auth_headers)
    assert response.status_code == 201  # Assuming 201 Created on success
    response_data = response.json()
    assert response_data["name"] == agent_data["name"]
    assert response_data["agent_id"] == agent_data["agent_id"]
    # Store the ID for later tests
    created_agent_id = response_data.get("agent_id")
    assert created_agent_id is not None


def test_get_all_agents(client: TestClient, auth_headers: dict):
    """Test GET /api/agents - List all agent definitions"""
    assert created_agent_id is not None, "Agent must be created before listing"
    response = client.get("/api/agents", headers=auth_headers)
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)  # Expecting a list of agents
    # Check if the created agent is in the list
    assert any(agent.get("agent_id") == created_agent_id for agent in response_data)


def test_get_specific_agent(client: TestClient, auth_headers: dict):
    """Test GET /api/agents/{agent_id} - Get a specific agent definition"""
    assert created_agent_id is not None, "Agent must be created before getting"
    response = client.get(f"/api/agents/{created_agent_id}", headers=auth_headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["agent_id"] == created_agent_id
    assert response_data["name"] == "Test Agent"  # Check against created data


def test_get_specific_agent_not_found(client: TestClient, auth_headers: dict):
    """Test GET /api/agents/{agent_id} - Agent not found"""
    response = client.get("/api/agents/non_existent_agent_id", headers=auth_headers)
    assert response.status_code == 404


def test_update_agent(client: TestClient, auth_headers: dict):
    """Test PUT /api/agents/{agent_id} - Update an agent definition"""
    assert created_agent_id is not None, "Agent must be created before updating"
    update_data = {
        "name": "Updated Test Agent",
        "description": "Updated description",
        "version": "1.1",
        # Include all fields required by the PUT endpoint's model
        "tools": ["tool1", "tool_updated"],
        "config": {"model": "updated-model"},
    }
    response = client.put(f"/api/agents/{created_agent_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == update_data["name"]
    assert response_data["version"] == update_data["version"]

    # Verify update by getting again
    get_response = client.get(f"/api/agents/{created_agent_id}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["name"] == update_data["name"]


def test_update_agent_not_found(client: TestClient, auth_headers: dict):
    """Test PUT /api/agents/{agent_id} - Agent not found"""
    update_data = {"name": "NonExistent Update"}  # Provide necessary fields
    response = client.put(
        "/api/agents/non_existent_agent_id", json=update_data, headers=auth_headers
    )
    assert response.status_code == 404  # Or appropriate error code


def test_delete_agent(client: TestClient, auth_headers: dict):
    """Test DELETE /api/agents/{agent_id} - Delete an agent definition"""
    global created_agent_id
    assert created_agent_id is not None, "Agent must be created before deleting"
    response = client.delete(f"/api/agents/{created_agent_id}", headers=auth_headers)
    assert response.status_code == 204  # No Content on successful delete

    # Verify deletion
    get_response = client.get(f"/api/agents/{created_agent_id}", headers=auth_headers)
    assert get_response.status_code == 404
    created_agent_id = None  # Reset global state


def test_delete_agent_not_found(client: TestClient, auth_headers: dict):
    """Test DELETE /api/agents/{agent_id} - Agent not found"""
    response = client.delete("/api/agents/non_existent_agent_id", headers=auth_headers)
    assert response.status_code == 404  # Or appropriate error code


# Placeholder tests for other endpoints (replace pass with actual tests)


def test_chat_endpoint(client: TestClient, auth_headers: dict):
    # TODO: Implement test for POST /api/chat endpoint (consider streaming)
    pass


def test_code_execution_endpoint(client: TestClient, auth_headers: dict):
    # TODO: Implement tests for POST /api/code/* endpoints
    pass


def test_upload_endpoints(client: TestClient, auth_headers: dict):
    # TODO: Implement tests for POST /api/upload/* endpoints
    pass


def test_integration_endpoints(client: TestClient, auth_headers: dict):
    # TODO: Implement tests for POST /api/integration/* endpoints
    pass


# Add tests for authentication endpoints (/api/auth/*) if not covered elsewhere


# Add tests for health endpoint (/api/ping)
def test_health_ping(client: TestClient):
    response = client.get("/api/ping")  # Assuming /api/ping from health.py
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
