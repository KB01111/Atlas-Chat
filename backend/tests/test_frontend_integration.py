"""
Frontend-Backend Integration Test for Atlas-Chat.

This script tests the integration between the frontend components and our
newly implemented backend features.
"""

import json
import logging

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Base URL for API requests
BASE_URL = "http://localhost:8000"


def test_agent_api_endpoints():
    """Test the agent API endpoints."""
    logger.info("Testing Agent API Endpoints...")

    # Test endpoints
    endpoints = [
        {
            "name": "Get Agents",
            "method": "GET",
            "url": f"{BASE_URL}/api/agents",
            "expected_status": 200,
            "expected_content_type": "application/json",
        },
        {
            "name": "Get Agent Types",
            "method": "GET",
            "url": f"{BASE_URL}/api/agent-types",
            "expected_status": 200,
            "expected_content_type": "application/json",
        },
        {
            "name": "Get Agent Models",
            "method": "GET",
            "url": f"{BASE_URL}/api/agent-models",
            "expected_status": 200,
            "expected_content_type": "application/json",
        },
    ]

    success_count = 0

    for endpoint in endpoints:
        logger.info(f"Testing endpoint: {endpoint['name']}")

        try:
            if endpoint["method"] == "GET":
                response = requests.get(endpoint["url"])
            elif endpoint["method"] == "POST":
                response = requests.post(endpoint["url"], json=endpoint.get("data", {}))
            else:
                logger.warning(f"Unsupported method: {endpoint['method']}")
                continue

            # Check status code
            if response.status_code == endpoint["expected_status"]:
                logger.info(f"✅ Status code: {response.status_code}")
            else:
                logger.warning(
                    f"❌ Status code: {response.status_code}, expected: "
                    f"{endpoint['expected_status']}"
                )
                continue

            # Check content type
            content_type = response.headers.get("Content-Type", "")
            if endpoint["expected_content_type"] in content_type:
                logger.info(f"✅ Content type: {content_type}")
            else:
                logger.warning(
                    f"❌ Content type: {content_type}, expected: "
                    f"{endpoint['expected_content_type']}"
                )
                continue

            # Check response data
            try:
                data = response.json()
                logger.info(f"✅ Response data: {json.dumps(data, indent=2)[:200]}...")
                success_count += 1
            except ValueError:
                logger.warning("❌ Response is not valid JSON")

        except requests.RequestException as e:
            logger.error(f"❌ Request failed: {e}")

    logger.info(f"Agent API Endpoints Tests: {success_count}/{len(endpoints)} passed")
    return success_count == len(endpoints)


def test_model_router_integration():
    """Test the integration with the model router."""
    logger.info("Testing Model Router Integration...")

    # Test model selection endpoint
    test_cases = [
        {
            "name": "General query",
            "data": {"query": "What is the capital of France?", "task_type": "general"},
            "expected_status": 200,
        },
        {
            "name": "Code generation",
            "data": {
                "query": "Write a Python function to calculate Fibonacci numbers",
                "task_type": "coding",
            },
            "expected_status": 200,
        },
        {
            "name": "With user preference",
            "data": {
                "query": "Tell me a joke",
                "task_type": "general",
                "user_preference": "google",
            },
            "expected_status": 200,
        },
    ]

    success_count = 0

    for case in test_cases:
        logger.info(f"Testing model selection: {case['name']}")

        try:
            response = requests.post(f"{BASE_URL}/api/select-model", json=case["data"])

            # Check status code
            if response.status_code == case["expected_status"]:
                logger.info(f"✅ Status code: {response.status_code}")
            else:
                logger.warning(
                    f"❌ Status code: {response.status_code}, expected: {case['expected_status']}"
                )
                continue

            # Check response data
            try:
                data = response.json()
                if "model_id" in data:
                    logger.info(f"✅ Selected model: {data['model_id']}")
                    success_count += 1
                else:
                    logger.warning("❌ Response does not contain model_id")
            except ValueError:
                logger.warning("❌ Response is not valid JSON")

        except requests.RequestException as e:
            logger.error(f"❌ Request failed: {e}")

    logger.info(f"Model Router Integration Tests: {success_count}/{len(test_cases)} passed")
    return success_count == len(test_cases)


def test_agent_factory_integration():
    """Test the integration with the agent factory."""
    logger.info("Testing Agent Factory Integration...")

    # Test agent creation
    test_agent = {
        "name": "Test Agent",
        "description": "Agent for testing",
        "agent_type": "sdk",
        "model_id": "gpt-4o",
        "system_prompt": "You are a test agent.",
        "tools": ["search_web"],
        "memory_enabled": True,
    }

    try:
        # Create agent
        logger.info("Creating test agent")
        response = requests.post(f"{BASE_URL}/api/agents", json=test_agent)

        if response.status_code != 201:
            logger.warning(f"❌ Failed to create agent: {response.status_code}")
            return False

        data = response.json()
        agent_id = data.get("agent_id")

        if not agent_id:
            logger.warning("❌ Response does not contain agent_id")
            return False

        logger.info(f"✅ Created agent with ID: {agent_id}")

        # Get agent
        logger.info(f"Getting agent: {agent_id}")
        response = requests.get(f"{BASE_URL}/api/agents/{agent_id}")

        if response.status_code != 200:
            logger.warning(f"❌ Failed to get agent: {response.status_code}")
            return False

        data = response.json()
        if data.get("name") != test_agent["name"]:
            logger.warning(f"❌ Agent name mismatch: {data.get('name')} != {test_agent['name']}")
            return False

        logger.info("✅ Retrieved agent successfully")

        # Send message to agent
        logger.info("Sending message to agent")
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"agent_id": agent_id, "message": "Hello, agent!", "stream": False},
        )

        if response.status_code != 200:
            logger.warning(f"❌ Failed to send message: {response.status_code}")
            return False

        data = response.json()
        if "response" not in data:
            logger.warning("❌ Response does not contain agent response")
            return False

        logger.info(f"✅ Agent response: {data['response'][:100]}...")

        # Delete agent
        logger.info(f"Deleting agent: {agent_id}")
        response = requests.delete(f"{BASE_URL}/api/agents/{agent_id}")

        if response.status_code != 204:
            logger.warning(f"❌ Failed to delete agent: {response.status_code}")
            return False

        logger.info("✅ Deleted agent successfully")

        return True

    except requests.RequestException as e:
        logger.error(f"❌ Request failed: {e}")
        return False


def test_frontend_api_compatibility():
    """Test compatibility with frontend API expectations."""
    logger.info("Testing Frontend API Compatibility...")

    # Test endpoints used by frontend components
    endpoints = [
        {
            "name": "Get Agents (AgentSelector)",
            "method": "GET",
            "url": f"{BASE_URL}/api/agents",
            "expected_status": 200,
            "expected_fields": ["agent_id", "name", "agent_type"],
        },
        {
            "name": "Get Conversations (ChatContainer)",
            "method": "GET",
            "url": f"{BASE_URL}/api/conversations",
            "expected_status": 200,
            "expected_fields": ["id", "title", "created_at"],
        },
        {
            "name": "Execute Code (CodeExecutionComponent)",
            "method": "POST",
            "url": f"{BASE_URL}/api/code/execute",
            "data": {"code": "print('Hello, world!')", "language": "python"},
            "expected_status": 200,
            "expected_fields": ["output", "execution_time"],
        },
    ]

    success_count = 0

    for endpoint in endpoints:
        logger.info(f"Testing endpoint: {endpoint['name']}")

        try:
            if endpoint["method"] == "GET":
                response = requests.get(endpoint["url"])
            elif endpoint["method"] == "POST":
                response = requests.post(endpoint["url"], json=endpoint.get("data", {}))
            else:
                logger.warning(f"Unsupported method: {endpoint['method']}")
                continue

            # Check status code
            if response.status_code == endpoint["expected_status"]:
                logger.info(f"✅ Status code: {response.status_code}")
            else:
                logger.warning(
                    f"❌ Status code: {response.status_code}, "
                    f"expected: {endpoint['expected_status']}"
                )
                continue

            # Check expected fields
            try:
                data = response.json()

                if isinstance(data, list) and data:
                    # Check first item in list
                    item = data[0]
                    missing_fields = [
                        field for field in endpoint["expected_fields"] if field not in item
                    ]

                    if missing_fields:
                        logger.warning(f"❌ Missing fields in response: {missing_fields}")
                        continue
                elif isinstance(data, dict):
                    # Check dictionary
                    missing_fields = [
                        field for field in endpoint["expected_fields"] if field not in data
                    ]

                    if missing_fields:
                        logger.warning(f"❌ Missing fields in response: {missing_fields}")
                        continue
                else:
                    logger.warning("❌ Unexpected response format")
                    continue

                logger.info("✅ Response contains all expected fields")
                success_count += 1

            except ValueError:
                logger.warning("❌ Response is not valid JSON")

        except requests.RequestException as e:
            logger.error(f"❌ Request failed: {e}")

    logger.info(f"Frontend API Compatibility Tests: {success_count}/{len(endpoints)} passed")
    return success_count == len(endpoints)


def run_all_tests():
    """Run all integration tests."""
    logger.info("Running all frontend-backend integration tests...")

    tests = [
        ("Agent API Endpoints", test_agent_api_endpoints),
        ("Model Router Integration", test_model_router_integration),
        ("Agent Factory Integration", test_agent_factory_integration),
        ("Frontend API Compatibility", test_frontend_api_compatibility),
    ]

    results = {}
    all_passed = True

    for name, test_func in tests:
        logger.info(f"\n{'='*50}\nRunning {name} tests\n{'='*50}")
        try:
            passed = test_func()
            results[name] = "PASSED" if passed else "FAILED"
            all_passed = all_passed and passed
        except Exception as e:
            logger.error(f"Error running {name} tests: {e}")
            results[name] = "ERROR"
            all_passed = False

    logger.info("\n\n")
    logger.info("=" * 50)
    logger.info("INTEGRATION TEST RESULTS SUMMARY")
    logger.info("=" * 50)

    for name, result in results.items():
        status = "✅" if result == "PASSED" else "❌"
        logger.info(f"{status} {name}: {result}")

    logger.info("=" * 50)
    logger.info(f"Overall result: {'PASSED' if all_passed else 'FAILED'}")
    logger.info("=" * 50)

    return all_passed


if __name__ == "__main__":
    run_all_tests()
