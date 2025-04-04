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
from pydantic import BaseModel, Field, ConfigDict

logger = logging.getLogger(__name__)

# Configure logging to mask sensitive information
class SensitiveFormatter(logging.Formatter):
    """Custom formatter that masks sensitive information in logs"""
    
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)
        self.sensitive_keys = ["api_key", "Authorization", "Bearer", "token"]
    
    def format(self, record):
        formatted_message = super().format(record)
        for key in self.sensitive_keys:
            if key in formatted_message:
                # Find the pattern "key=value" or "key: value" and replace with "key=***"
                import re
                formatted_message = re.sub(
                    f"{key}[=:][^,\\s\\]\\)]+", 
                    f"{key}=***MASKED***", 
                    formatted_message
                )
        return formatted_message

# Apply the sensitive formatter to the logger
handler = logging.StreamHandler()
handler.setFormatter(SensitiveFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class OpenRouterMessage(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    role: str = Field(..., description="The role of the message sender (system, user, assistant)")
    content: str = Field(..., description="The content of the message")
    
class OpenRouterCompletionRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    
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
        logger.info("OpenRouterClient initialized with base URL: %s", self.base_url)
        
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
        
        # Log request without sensitive information
        logger.info("Sending chat completion request to OpenRouter for model: %s", model)
        
        # Validate and prepare the request using Pydantic
        request_data = OpenRouterCompletionRequest(
            model=model,
            messages=[OpenRouterMessage(role=m["role"], content=m["content"]) for m in messages],
            temperature=temperature,
            stream=stream
        )
        
        if max_tokens:
            request_data.max_tokens = max_tokens
            
        # Use model_dump instead of dict
        payload = request_data.model_dump()
        
        try:
            # Using aiohttp for async HTTP requests
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error("OpenRouter API error: %s", error_text)
                        raise Exception(f"OpenRouter API returned status code {response.status}")
                    
                    if stream:
                        # Return a generator for streaming responses
                        return await self._process_streaming_response_async(response)
                    else:
                        return await response.json()
                
        except Exception as e:
            # Log error without exposing the API key
            logger.error("Error calling OpenRouter API: %s", str(e).replace(self.api_key, "***MASKED***"))
            raise
            
    async def _process_streaming_response_async(self, response):
        """Process a streaming response from OpenRouter asynchronously"""
        result = []
        async for line in response.content:
            line = line.strip()
            if line:
                if line == b'data: [DONE]':
                    break
                    
                if line.startswith(b'data: '):
                    json_str = line[6:].decode('utf-8')
                    try:
                        result.append(json.loads(json_str))
                    except json.JSONDecodeError:
                        logger.error("Error decoding JSON from stream")
        return result
                        
    async def format_openrouter_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
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
            logger.error("Error formatting OpenRouter response: %s", str(e))
            return {"content": "Error processing response", "role": "assistant"}
