"""
Test Suite for OpenRouter Integration with AtlasChat
Provides comprehensive tests for all components of the integration
"""

import asyncio
import json
import os
import unittest
from unittest.mock import MagicMock, patch

import pytest

from app.core.models.openrouter_models import (
    GraphitiEpisode,
    OpenRouterCompletionRequest,
    OpenRouterCompletionResponse,
    OpenRouterMessage,
)

# Import the components to test
from app.core.services.openrouter_client import OpenRouterClient
from app.core.services.openrouter_graphiti_integration import (
    OpenRouterGraphitiIntegration,
)
from app.core.services.openrouter_langgraph_agent import OpenRouterLangGraphAgent
from app.core.services.openrouter_sdk_agent import OpenRouterSDKAgent

# Test data
TEST_MESSAGES = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, can you help me with Python?"},
]

TEST_TOOLS = [
    {
        "name": "execute_code",
        "description": "Execute Python code",
        "parameters": {"code": {"type": "string", "description": "The Python code to execute"}},
    }
]

TEST_AGENT_CONFIG = {
    "model": "deepseek/deepseek-v3",
    "temperature": 0.7,
    "provider": "openrouter",
}

# Mock response data
MOCK_COMPLETION_RESPONSE = {
    "id": "test-id",
    "object": "chat.completion",
    "created": 1617979521,
    "model": "deepseek/deepseek-v3",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "I can definitely help you with Python! What would you like to know?",
            },
            "finish_reason": "stop",
        }
    ],
    "usage": {"prompt_tokens": 50, "completion_tokens": 15, "total_tokens": 65},
}


class TestOpenRouterClient(unittest.TestCase):
    """Tests for the OpenRouterClient"""

    def setUp(self):
        """Set up test environment"""
        # Mock environment variables
        os.environ["OPENROUTER_API_KEY"] = "test-api-key"
        os.environ["OPENROUTER_BASE_URL"] = "https://test-api.openrouter.ai/api/v1"

        self.client = OpenRouterClient()

    @patch("requests.post")
    def test_chat_completion(self, mock_post):
        """Test chat completion request"""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_COMPLETION_RESPONSE
        mock_post.return_value = mock_response

        # Call the method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            self.client.chat_completion(
                messages=TEST_MESSAGES, model="deepseek/deepseek-v3", temperature=0.7
            )
        )

        # Verify the response
        self.assertEqual(response["model"], "deepseek/deepseek-v3")
        self.assertEqual(
            response["choices"][0]["message"]["content"],
            "I can definitely help you with Python! What would you like to know?",
        )

        # Verify the request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-api-key")

        # Verify request payload
        payload = json.loads(kwargs["data"])
        self.assertEqual(payload["model"], "deepseek/deepseek-v3")
        self.assertEqual(payload["temperature"], 0.7)
        self.assertEqual(len(payload["messages"]), 2)

    def test_format_openrouter_response(self):
        """Test response formatting"""
        formatted = self.client.format_openrouter_response(MOCK_COMPLETION_RESPONSE)

        self.assertEqual(
            formatted["content"],
            "I can definitely help you with Python! What would you like to know?",
        )
        self.assertEqual(formatted["role"], "assistant")
        self.assertEqual(formatted["model"], "deepseek/deepseek-v3")
        self.assertEqual(formatted["finish_reason"], "stop")
        self.assertEqual(formatted["usage"]["total_tokens"], 65)


class TestOpenRouterSDKAgent(unittest.TestCase):
    """Tests for the OpenRouterSDKAgent"""

    def setUp(self):
        """Set up test environment"""
        self.agent = OpenRouterSDKAgent()
        self.agent.client = MagicMock()
        self.agent.client.chat_completion.return_value = MOCK_COMPLETION_RESPONSE
        self.agent.client.format_openrouter_response.return_value = {
            "content": "I can definitely help you with Python! What would you like to know?",
            "role": "assistant",
            "model": "deepseek/deepseek-v3",
            "finish_reason": "stop",
            "usage": {"total_tokens": 65},
        }

    def test_execute(self):
        """Test agent execution"""
        # Call the method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            self.agent.execute(
                agent_config=TEST_AGENT_CONFIG, messages=TEST_MESSAGES, tools=TEST_TOOLS
            )
        )

        # Verify the response
        self.assertEqual(
            response["content"],
            "I can definitely help you with Python! What would you like to know?",
        )
        self.assertEqual(response["role"], "assistant")

        # Verify client was called correctly
        self.agent.client.chat_completion.assert_called_once()
        args, kwargs = self.agent.client.chat_completion.call_args
        self.assertEqual(kwargs["model"], "deepseek/deepseek-v3")
        self.assertEqual(kwargs["temperature"], 0.7)

        # Verify tools were included in system message
        messages = kwargs["messages"]
        system_message = next((m for m in messages if m["role"] == "system"), None)
        self.assertIsNotNone(system_message)
        self.assertIn("execute_code", system_message["content"])


class TestOpenRouterLangGraphAgent(unittest.TestCase):
    """Tests for the OpenRouterLangGraphAgent"""

    def setUp(self):
        """Set up test environment"""
        self.agent = OpenRouterLangGraphAgent()
        self.agent.client = MagicMock()
        self.agent.client.chat_completion.return_value = MOCK_COMPLETION_RESPONSE
        self.agent.client.format_openrouter_response.return_value = {
            "content": "I can definitely help you with Python! What would you like to know?",
            "role": "assistant",
            "model": "deepseek/deepseek-v3",
            "finish_reason": "stop",
            "usage": {"total_tokens": 65},
        }

    @patch("langgraph.graph.StateGraph")
    def test_create_graph(self, mock_state_graph):
        """Test graph creation"""
        # Set up mock
        mock_graph = MagicMock()
        mock_state_graph.return_value = mock_graph
        mock_graph.compile.return_value = "compiled_graph"

        # Call the method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self.agent.create_graph(agent_config=TEST_AGENT_CONFIG, tools=TEST_TOOLS)
        )

        # Verify the result
        self.assertEqual(result, "compiled_graph")

        # Verify graph was created correctly
        mock_state_graph.assert_called_once()
        mock_graph.add_node.assert_called()
        mock_graph.add_edge.assert_called()
        mock_graph.set_entry_point.assert_called_with("thinking")
        mock_graph.compile.assert_called_once()

    @patch("langgraph.graph.StateGraph")
    def test_execute(self, mock_state_graph):
        """Test agent execution"""
        # Set up mock
        mock_graph = MagicMock()
        mock_state_graph.return_value = mock_graph
        mock_graph.compile.return_value = mock_graph
        mock_graph.ainvoke.return_value = {
            "messages": TEST_MESSAGES
            + [
                {
                    "role": "assistant",
                    "content": "I can definitely help you with Python! What would you like to know?",
                }
            ]
        }

        # Call the method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            self.agent.execute(
                agent_config=TEST_AGENT_CONFIG, messages=TEST_MESSAGES, tools=TEST_TOOLS
            )
        )

        # Verify the response
        self.assertEqual(response["role"], "assistant")
        self.assertEqual(
            response["content"],
            "I can definitely help you with Python! What would you like to know?",
        )

        # Verify graph was invoked correctly
        mock_graph.ainvoke.assert_called_once()
        args, kwargs = mock_graph.ainvoke.call_args
        self.assertEqual(args[0]["messages"], TEST_MESSAGES)
        self.assertEqual(args[0]["tools"], TEST_TOOLS)


class TestOpenRouterGraphitiIntegration(unittest.TestCase):
    """Tests for the OpenRouterGraphitiIntegration"""

    def setUp(self):
        """Set up test environment"""
        self.graphiti_client = MagicMock()
        self.integration = OpenRouterGraphitiIntegration(self.graphiti_client)

    def test_add_conversation_to_graphiti(self):
        """Test adding conversation to Graphiti"""
        # Set up mock
        self.graphiti_client.add_episode.return_value = "test-episode-id"

        # Call the method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        episode_id = loop.run_until_complete(
            self.integration.add_conversation_to_graphiti(
                conversation_id="test-conversation",
                messages=TEST_MESSAGES,
                metadata={"user_id": "test-user"},
            )
        )

        # Verify the result
        self.assertEqual(episode_id, "test-episode-id")

        # Verify client was called correctly
        self.graphiti_client.add_episode.assert_called_once()
        self.graphiti_client.add_nodes.assert_called_once()
        self.graphiti_client.add_relationships.assert_called_once()

    def test_search_graphiti_for_context(self):
        """Test searching Graphiti for context"""
        # Set up mock
        self.graphiti_client.search.return_value = [
            {
                "id": "episode:test",
                "content": "User: How do I use Python?\nAssistant: Import the libraries you need.",
                "timestamp": 1617979521,
                "relevance": 0.95,
            }
        ]

        # Call the method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(
            self.integration.search_graphiti_for_context(query="Python libraries", limit=5)
        )

        # Verify the results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["type"], "episode")
        self.assertEqual(results[0]["relevance"], 0.95)

        # Verify client was called correctly
        self.graphiti_client.search.assert_called_once_with("Python libraries", limit=5)

    def test_enhance_messages_with_graphiti_context(self):
        """Test enhancing messages with Graphiti context"""
        # Set up mock
        self.graphiti_client.search.return_value = [
            {
                "id": "episode:test",
                "content": "User: How do I use Python?\nAssistant: Import the libraries you need.",
                "timestamp": 1617979521,
                "relevance": 0.95,
            }
        ]

        # Call the method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        enhanced_messages = loop.run_until_complete(
            self.integration.enhance_messages_with_graphiti_context(
                messages=TEST_MESSAGES, query="Python libraries"
            )
        )

        # Verify the results
        self.assertEqual(len(enhanced_messages), 2)  # Original messages + system message
        system_message = next((m for m in enhanced_messages if m["role"] == "system"), None)
        self.assertIsNotNone(system_message)
        self.assertIn("Relevant context", system_message["content"])
        self.assertIn("Import the libraries you need", system_message["content"])


class TestPydanticModels(unittest.TestCase):
    """Tests for the Pydantic models"""

    def test_openrouter_message(self):
        """Test OpenRouterMessage model"""
        message = OpenRouterMessage(role="user", content="Hello")
        self.assertEqual(message.role, "user")
        self.assertEqual(message.content, "Hello")

        # Test to_dict method
        message_dict = message.to_dict()
        self.assertEqual(message_dict["role"], "user")
        self.assertEqual(message_dict["content"], "Hello")

    def test_openrouter_completion_request(self):
        """Test OpenRouterCompletionRequest model"""
        messages = [OpenRouterMessage(role="user", content="Hello")]
        request = OpenRouterCompletionRequest(
            model="deepseek/deepseek-v3",
            messages=messages,
            temperature=0.7,
            stream=False,
        )

        # Test to_api_format method
        api_format = request.to_api_format()
        self.assertEqual(api_format["model"], "deepseek/deepseek-v3")
        self.assertEqual(api_format["temperature"], 0.7)
        self.assertEqual(api_format["stream"], False)
        self.assertEqual(len(api_format["messages"]), 1)

    def test_openrouter_completion_response(self):
        """Test OpenRouterCompletionResponse model"""
        response = OpenRouterCompletionResponse(**MOCK_COMPLETION_RESPONSE)

        # Test get_content method
        content = response.get_content()
        self.assertEqual(
            content,
            "I can definitely help you with Python! What would you like to know?",
        )

        # Test to_atlaschat_format method
        atlaschat_format = response.to_atlaschat_format()
        self.assertEqual(
            atlaschat_format["content"],
            "I can definitely help you with Python! What would you like to know?",
        )
        self.assertEqual(atlaschat_format["role"], "assistant")
        self.assertEqual(atlaschat_format["model"], "deepseek/deepseek-v3")

    def test_graphiti_episode(self):
        """Test GraphitiEpisode model"""
        episode = GraphitiEpisode(
            id="test-episode",
            timestamp=1617979521,
            content="Test content",
            metadata={"user_id": "test-user"},
        )

        # Test to_nodes_and_relationships method
        graph_data = episode.to_nodes_and_relationships()
        self.assertEqual(len(graph_data["nodes"]), 1)
        self.assertEqual(graph_data["nodes"][0]["id"], "episode:test-episode")
        self.assertEqual(graph_data["nodes"][0]["label"], "Episode")
        self.assertEqual(graph_data["nodes"][0]["properties"]["content"], "Test content")
        self.assertEqual(graph_data["nodes"][0]["properties"]["user_id"], "test-user")


@pytest.mark.asyncio
async def test_full_integration():
    """Test full integration of all components"""
    # This would be an integration test that uses all components together
    # For now, we'll just outline the steps

    # 1. Create instances of all components
    client = OpenRouterClient()
    sdk_agent = OpenRouterSDKAgent()
    langgraph_agent = OpenRouterLangGraphAgent()
    graphiti_integration = OpenRouterGraphitiIntegration()

    # 2. Mock the API calls
    # (In a real test, you would use a more sophisticated mocking approach)
    client.chat_completion = MagicMock(return_value=MOCK_COMPLETION_RESPONSE)
    client.format_openrouter_response = MagicMock(
        return_value={
            "content": "I can definitely help you with Python! What would you like to know?",
            "role": "assistant",
        }
    )

    # 3. Set up the SDK agent to use our mocked client
    sdk_agent.client = client

    # 4. Execute the agent
    response = await sdk_agent.execute(agent_config=TEST_AGENT_CONFIG, messages=TEST_MESSAGES)

    # 5. Verify the response
    assert response["role"] == "assistant"
    assert "Python" in response["content"]

    # 6. Test with Graphiti integration
    # (In a real test, you would set up proper mocks for Graphiti)

    # 7. Test with LangGraph
    # (In a real test, you would set up proper mocks for LangGraph)


if __name__ == "__main__":
    unittest.main()
