import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock, AsyncMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.core.executors.sdk_executor import OpenAIAgentSDKExecutor

class TestOpenAIAgentSDKExecutor(unittest.TestCase):
    """Test cases for the OpenAIAgentSDKExecutor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.model = "gpt-4o"
        
        # Create a mock for the OpenAI client
        self.mock_openai_client = MagicMock()
        self.mock_agent = MagicMock()
        self.mock_openai_client.beta.agents.create.return_value = self.mock_agent
        
        # Create a mock for the agent run
        self.mock_run = MagicMock()
        self.mock_agent.runs.create_and_stream.return_value = AsyncMock()
        
        # Create a mock for the tool outputs
        self.mock_tool_outputs = []
        
        # Create the executor with the mock client
        with patch('backend.app.core.executors.sdk_executor.OpenAI') as mock_openai:
            mock_openai.return_value = self.mock_openai_client
            self.executor = OpenAIAgentSDKExecutor(api_key=self.api_key, model=self.model)
    
    @patch('backend.app.core.executors.sdk_executor.OpenAI')
    def test_initialization(self, mock_openai):
        """Test that the executor initializes correctly."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        executor = OpenAIAgentSDKExecutor(api_key=self.api_key, model=self.model)
        
        # Check that the OpenAI client was created with the correct API key
        mock_openai.assert_called_once_with(api_key=self.api_key)
        
        # Check that the agent was created with the correct model
        mock_client.beta.agents.create.assert_called_once()
        args, kwargs = mock_client.beta.agents.create.call_args
        self.assertEqual(kwargs['model'], self.model)
    
    def test_register_tool(self):
        """Test that tools can be registered correctly."""
        # Define a test tool function
        def test_tool(arg1: str, arg2: int) -> str:
            """Test tool docstring."""
            return f"{arg1} {arg2}"
        
        # Register the tool
        self.executor.register_tool(test_tool)
        
        # Check that the tool was registered
        self.assertIn(test_tool.__name__, self.executor.tools)
        
        # Check that the tool definition was created correctly
        tool_def = self.executor.tool_definitions[0]
        self.assertEqual(tool_def['function']['name'], test_tool.__name__)
        self.assertEqual(tool_def['function']['description'], "Test tool docstring.")
        
        # Check that the parameters were defined correctly
        params = tool_def['function']['parameters']['properties']
        self.assertIn('arg1', params)
        self.assertEqual(params['arg1']['type'], 'string')
        self.assertIn('arg2', params)
        self.assertEqual(params['arg2']['type'], 'integer')
    
    @patch('backend.app.core.executors.sdk_executor.OpenAI')
    async def test_execute_agent(self, mock_openai):
        """Test that the agent can be executed correctly."""
        # Set up the mocks
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_agent = MagicMock()
        mock_client.beta.agents.create.return_value = mock_agent
        
        mock_run = AsyncMock()
        mock_agent.runs.create_and_stream = mock_run
        
        # Create the executor
        executor = OpenAIAgentSDKExecutor(api_key=self.api_key, model=self.model)
        
        # Define a test tool function
        def test_tool(arg1: str, arg2: int) -> str:
            """Test tool docstring."""
            return f"{arg1} {arg2}"
        
        # Register the tool
        executor.register_tool(test_tool)
        
        # Execute the agent
        message = "Test message"
        callback = MagicMock()
        
        await executor.execute_agent(message, callback)
        
        # Check that the agent was executed with the correct message
        mock_agent.runs.create_and_stream.assert_called_once()
        args, kwargs = mock_agent.runs.create_and_stream.call_args
        self.assertEqual(kwargs['messages'][0]['content'], message)
        
        # Check that the callback was called
        callback.assert_called()

if __name__ == '__main__':
    unittest.main()
