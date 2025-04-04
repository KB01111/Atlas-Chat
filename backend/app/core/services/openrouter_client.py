"""
OpenRouter API Client for AtlasChat
Provides integration with OpenRouter API for accessing models like DeepSeek v3
"""

import os
import requests
from typing import Dict, Any, Optional, List, Union
import json
import logging
import asyncio
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class OpenRouterMessage(BaseModel):
    role: str = Field(..., description="The role of the message sender (system, user, assistant)")
    content: str = Field(..., description="The content of the message")
    
class OpenRouterCompletionRequest(BaseModel):
    model: str = Field(..., description="The model identifier to use")
    messages: List[OpenRouterMessage] = Field(..., description="The messages to generate a completion for")
    temperature: float = Field(0.7, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    stream: bool = Field(False, description="Whether to stream the response")
    
class OpenRouterClient:
    """Client for interacting with the OpenRouter API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            logger.error("OPENROUTER_API_KEY environment variable not set")
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
            
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        
    async def chat_completion(self, 
                        messages: List[Dict[str, str]], 
                        model: str = "deepseek/deepseek-v3",
                        temperature: float = 0.7,
                        max_tokens: Optional[int] = None,
                        stream: bool = False) -> Dict[str, Any]:
        """
        Send a chat completion request to OpenRouter
        
        Args:
            messages: List of message objects with role and content
            model: Model identifier (e.g., "deepseek/deepseek-v3")
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Response from OpenRouter API
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://atlaschat.app",  # Replace with your app's URL
            "X-Title": "AtlasChat"  # Your app's name
        }
        
        # Validate and prepare the request using Pydantic
        request_data = OpenRouterCompletionRequest(
            model=model,
            messages=[OpenRouterMessage(role=m["role"], content=m["content"]) for m in messages],
            temperature=temperature,
            stream=stream
        )
        
        if max_tokens:
            request_data.max_tokens = max_tokens
            
        payload = request_data.dict()
        
        try:
            # Using requests for simplicity, but in production you might want to use aiohttp
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            
            if stream:
                # Return a generator for streaming responses
                return self._process_streaming_response(response)
            else:
                return response.json()
                
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {str(e)}")
            raise
            
    def _process_streaming_response(self, response):
        """Process a streaming response from OpenRouter"""
        for line in response.iter_lines():
            if line:
                if line.strip() == b'data: [DONE]':
                    break
                    
                if line.startswith(b'data: '):
                    json_str = line[6:].decode('utf-8')
                    try:
                        yield json.loads(json_str)
                    except json.JSONDecodeError:
                        logger.error(f"Error decoding JSON from stream: {json_str}")
                        
    def format_openrouter_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format OpenRouter response to match the format expected by AtlasChat
        
        Args:
            response: Response from OpenRouter API
            
        Returns:
            Formatted response compatible with AtlasChat
        """
        try:
            # Extract the content from the OpenRouter response
            if "choices" in response and len(response["choices"]) > 0:
                message = response["choices"][0].get("message", {})
                content = message.get("content", "")
                
                # Format to match AtlasChat's expected response format
                return {
                    "content": content,
                    "role": "assistant",
                    "model": response.get("model", ""),
                    "finish_reason": response["choices"][0].get("finish_reason", ""),
                    "usage": response.get("usage", {})
                }
            else:
                logger.error("Invalid response format from OpenRouter")
                return {"content": "Error: Invalid response from model provider", "role": "assistant"}
        except Exception as e:
            logger.error(f"Error formatting OpenRouter response: {str(e)}")
            return {"content": f"Error processing response: {str(e)}", "role": "assistant"}
