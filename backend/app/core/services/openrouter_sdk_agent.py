"""
OpenRouter SDK Agent Integration for AtlasChat
Extends the agent_service.py to support OpenRouter models with the OpenAI Agent SDK
"""

import os
import logging
from typing import Dict, Any, List, Optional
from app.core.services.openrouter_client import OpenRouterClient

logger = logging.getLogger(__name__)

class OpenRouterSDKAgent:
    """
    Implementation of SDK Agent using OpenRouter API
    Compatible with AtlasChat's dual-engine architecture
    """

    def __init__(self):
        self.client = OpenRouterClient()

    async def execute(self, 
                     agent_config: Dict[str, Any],
                     messages: List[Dict[str, str]],
                     tools: List[Dict[str, Any]] = None,
                     stream: bool = False) -> Dict[str, Any]:
        """
        Execute the agent using OpenRouter API

        Args:
            agent_config: Configuration for the agent
            messages: List of messages for the conversation
            tools: List of tools available to the agent
            stream: Whether to stream the response

        Returns:
            Agent response
        """
        try:
            # Extract configuration
            model = agent_config.get("model", "deepseek/deepseek-v3")
            temperature = agent_config.get("temperature", 0.7)
            max_tokens = agent_config.get("max_tokens", None)

            # Format system message to include tools if provided
            if tools and len(tools) > 0:
                # Find system message or create one
                system_msg_idx = next((i for i, m in enumerate(messages) if m["role"] == "system"), None)

                tools_description = "You have access to the following tools:\n"
                for tool in tools:
                    tools_description += f"- {tool['name']}: {tool['description']}\n"
                    if 'parameters' in tool:
                        tools_description += f"  Parameters: {tool['parameters']}\n"

                if system_msg_idx is not None:
                    # Append tools to existing system message
                    messages[system_msg_idx]["content"] += f"\n\n{tools_description}"
                else:
                    # Create new system message with tools
                    messages.insert(0, {
                        "role": "system",
                        "content": f"You are an AI assistant with the following tools:\n{tools_description}"
                    })

            # Call OpenRouter API
            response = await self.client.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )

            # Format response for AtlasChat
            if stream:
                # Return streaming generator
                return self._process_streaming_response(response)
            else:
                return self.client.format_openrouter_response(response)

        except Exception as e:
            logger.error(f"Error executing OpenRouter SDK agent: {str(e)}")
            return {
                "content": f"Error: {str(e)}",
                "role": "assistant"
            }

    def _process_streaming_response(self, response_generator):
        """Process streaming response from OpenRouter"""
        for chunk in response_generator:
            yield self.client.format_openrouter_response(chunk)
