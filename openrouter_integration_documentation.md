# OpenRouter Integration for AtlasChat

## Overview

This document provides comprehensive documentation for integrating OpenRouter with AtlasChat, enabling support for DeepSeek v3 and other models through OpenRouter's API. The integration maintains compatibility with AtlasChat's dual-engine architecture (SDK and LangGraph) and works seamlessly with Pydantic AI and Graphiti components.

## Table of Contents

1. [Architecture](#architecture)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Agent Definitions](#agent-definitions)
5. [Usage](#usage)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Features](#advanced-features)

## Architecture

The OpenRouter integration follows AtlasChat's dual-engine architecture:

1. **OpenAI Agent SDK Engine**

   - Implemented in `openrouter_sdk_agent.py`
   - Provides structured agent workflows with built-in planning
   - Supports tool usage and streaming responses

2. **LangGraph Engine**

   - Implemented in `openrouter_langgraph_agent.py`
   - Enables custom graph-based agent workflows
   - Supports complex branching logic and state management

3. **Pydantic AI Integration**

   - Implemented in `openrouter_models.py`
   - Provides structured data validation and parsing
   - Ensures type safety and consistent data schemas

4. **Graphiti Compatibility**
   - Implemented in `openrouter_graphiti_integration.py`
   - Enables knowledge graph capabilities and episodic memory
   - Enhances conversations with relevant context from previous interactions

## Installation

### Prerequisites

- AtlasChat backend installed and configured
- OpenRouter API key (obtain from [OpenRouter](https://openrouter.ai))
- Python 3.8+ with pip

### Steps

1. Copy the OpenRouter integration files to your AtlasChat backend:

   - `app/core/services/openrouter_client.py`
   - `app/core/services/openrouter_sdk_agent.py`
   - `app/core/services/openrouter_langgraph_agent.py`
   - `app/core/services/openrouter_graphiti_integration.py`
   - `app/core/models/openrouter_models.py`
   - `app/api/openrouter_agent_definitions.json`

2. Install required dependencies:

   ```bash
   pip install openrouter-py langchain langgraph
   ```

3. Copy the environment configuration:

   ```bash
   cp .env.openrouter .env
   ```

4. Update the `.env` file with your OpenRouter API key.

5. Register the OpenRouter agents in your agent service.

## Configuration

### Environment Variables

The following environment variables can be configured in your `.env` file:

```
# OpenRouter API credentials
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# OpenRouter model configuration
OPENROUTER_DEFAULT_MODEL=deepseek/deepseek-v3
OPENROUTER_DEFAULT_TEMPERATURE=0.7
OPENROUTER_MAX_TOKENS=4096

# Integration settings
OPENROUTER_ENABLE_STREAMING=true
OPENROUTER_ENABLE_GRAPHITI=true
OPENROUTER_ENABLE_TOOL_CALLS=true

# Rate limiting and usage tracking
OPENROUTER_RATE_LIMIT_REQUESTS=100
OPENROUTER_RATE_LIMIT_WINDOW_SECONDS=60
OPENROUTER_TRACK_USAGE=true

# Fallback configuration
OPENROUTER_FALLBACK_TO_OPENAI=true
OPENROUTER_FALLBACK_MODEL=gpt-4o

# Logging and monitoring
OPENROUTER_LOG_LEVEL=info
OPENROUTER_LOG_REQUESTS=false
```

### Agent Configuration

Agent configuration is defined in `app/api/openrouter_agent_definitions.json`. You can customize the available agents by modifying this file.

## Agent Definitions

The integration provides three pre-configured agents:

1. **DeepSeek v3 (SDK)**

   - Uses the SDK engine with DeepSeek v3 model
   - Supports code execution, web search, and file management tools
   - Integrates with Graphiti for knowledge graph capabilities

2. **DeepSeek v3 (LangGraph)**

   - Uses the LangGraph engine with DeepSeek v3 model
   - Provides custom workflow capabilities
   - Supports the same tools as the SDK agent

3. **DeepSeek Coder**
   - Specialized coding assistant using DeepSeek Coder model
   - Optimized for programming tasks
   - Supports code execution and file management tools

You can add additional agents by extending the agent definitions file.

## Usage

### Integrating with Agent Service

To integrate the OpenRouter agents with your existing agent service, add the following code to `app/core/services/agent_service.py`:

```python
from app.core.services.openrouter_sdk_agent import OpenRouterSDKAgent
from app.core.services.openrouter_langgraph_agent import OpenRouterLangGraphAgent

# Initialize OpenRouter agents
openrouter_sdk_agent = OpenRouterSDKAgent()
openrouter_langgraph_agent = OpenRouterLangGraphAgent()

# In your execute_agent method
def execute_agent(self, agent_id: str, messages: list, stream: bool = False):
    # Get agent definition
    agent_def = self.get_agent_definition(agent_id)

    # Check if this is an OpenRouter agent
    if agent_def.get("sdk_config", {}).get("provider") == "openrouter":
        # Use SDK agent
        return openrouter_sdk_agent.execute(
            agent_config=agent_def.get("sdk_config", {}),
            messages=messages,
            tools=self.get_tools_for_agent(agent_id),
            stream=stream
        )
    elif agent_def.get("langgraph_config", {}).get("provider") == "openrouter":
        # Use LangGraph agent
        return openrouter_langgraph_agent.execute(
            agent_config=agent_def.get("langgraph_config", {}),
            messages=messages,
            tools=self.get_tools_for_agent(agent_id),
            stream=stream
        )

    # Existing code for other providers...
```

### Loading Agent Definitions

Add the following code to load the OpenRouter agent definitions:

```python
def load_agent_definitions(self):
    # Load existing agent definitions
    # ...

    # Load OpenRouter agent definitions
    openrouter_defs_path = os.path.join(
        os.path.dirname(__file__),
        "../../api/openrouter_agent_definitions.json"
    )

    if os.path.exists(openrouter_defs_path):
        with open(openrouter_defs_path, "r") as f:
            openrouter_defs = json.load(f)
            self.agent_definitions.extend(openrouter_defs)
```

### Using Graphiti Integration

To enhance conversations with Graphiti context:

```python
from app.core.services.openrouter_graphiti_integration import OpenRouterGraphitiIntegration

# Initialize Graphiti integration
graphiti_integration = OpenRouterGraphitiIntegration(graphiti_client)

# Before executing the agent, enhance messages with context
if agent_def.get("uses_graphiti", False):
    messages = await graphiti_integration.enhance_messages_with_graphiti_context(messages)

# After receiving a response, add the conversation to Graphiti
if agent_def.get("uses_graphiti", False):
    await graphiti_integration.add_conversation_to_graphiti(
        conversation_id=conversation_id,
        messages=messages + [response],
        metadata={"user_id": user_id, "agent_id": agent_id}
    )
```

## Testing

The integration includes a comprehensive test suite in `tests/test_openrouter_integration.py`. To run the tests:

```bash
cd backend
pytest tests/test_openrouter_integration.py -v
```

The test suite includes:

- Unit tests for all components
- Integration tests for the full workflow
- Mocked API responses for deterministic testing

## Troubleshooting

### Common Issues

1. **API Key Issues**

   - Ensure your OpenRouter API key is correctly set in the `.env` file
   - Verify the API key has access to the models you're trying to use

2. **Model Availability**

   - Check that the requested model is available through OpenRouter
   - Some models may require specific permissions or credits

3. **Rate Limiting**

   - OpenRouter has rate limits that may affect usage
   - Configure the rate limiting settings appropriately

4. **Integration Errors**
   - Check the logs for detailed error messages
   - Ensure all components are properly initialized

### Logging

The integration uses Python's logging module. To enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Advanced Features

### Custom Model Configuration

You can customize model parameters for each agent in the agent definitions:

```json
{
  "agent_id": "custom_deepseek",
  "name": "Custom DeepSeek",
  "description": "Custom configuration for DeepSeek v3",
  "agent_type": "sdk",
  "uses_graphiti": true,
  "allowed_tools": ["execute_code"],
  "sdk_config": {
    "model": "deepseek/deepseek-v3",
    "temperature": 0.5,
    "max_tokens": 2048,
    "top_p": 0.9,
    "provider": "openrouter"
  }
}
```

### Streaming Responses

The integration supports streaming responses for the SDK agent. To enable streaming:

```python
response_stream = await openrouter_sdk_agent.execute(
    agent_config=agent_def.get("sdk_config", {}),
    messages=messages,
    tools=tools,
    stream=True
)

# Process the streaming response
for chunk in response_stream:
    # Send chunk to client
    yield chunk
```

### Tool Execution

The integration supports tool execution for both SDK and LangGraph agents. Tools are defined in the agent definitions and passed to the execute method.

For the LangGraph agent, tool execution is handled by the graph workflow, which can be customized for specific use cases.

---

This documentation provides a comprehensive guide to integrating OpenRouter with AtlasChat. For additional support or questions, please refer to the OpenRouter documentation or contact the AtlasChat development team.
