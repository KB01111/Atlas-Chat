"""
OpenRouter API Client for AtlasChat
Provides integration with OpenRouter API for accessing models like DeepSeek v3
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


# Configure logging to mask sensitive information
class SensitiveFormatter(logging.Formatter):
    """Custom formatter that masks sensitive information in logs"""

    def __init__(self, fmt=None, datefmt=None, style="%"):
        super().__init__(fmt, datefmt, style)
        self.sensitive_keys = ["api_key", "Authorization", "Bearer", "token"]

    def format(self, record):
        formatted_message = super().format(record)
        for key in self.sensitive_keys:
            if key in formatted_message:
                # Find the pattern "key=value" or "key: value" and replace with "key=***"
                import re

                formatted_message = re.sub(
                    f"{key}[=:][^,\\s\\]\\)]+", f"{key}=***MASKED***", formatted_message
                )
        return formatted_message


# Apply the sensitive formatter to the logger
handler = logging.StreamHandler()
handler.setFormatter(SensitiveFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


class OpenRouterMessage(BaseModel):
    model_config = ConfigDict(extra="allow")

    role: str = Field(..., description="The role of the message sender (system, user, assistant)")
    content: str = Field(..., description="The content of the message")


class OpenRouterCompletionRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str = Field(..., description="The model identifier to use")
    messages: List[OpenRouterMessage] = Field(
        ..., description="The messages to generate a completion for"
    )
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

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek/deepseek-v3",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
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
            "X-Title": "AtlasChat",  # Your app's name
        }

        # Log request without sensitive information
        logger.info("Sending chat completion request to OpenRouter for model: %s", model)

        # Validate and prepare the request using Pydantic
        request_data = OpenRouterCompletionRequest(
            model=model,
            messages=[OpenRouterMessage(role=m["role"], content=m["content"]) for m in messages],
            temperature=temperature,
            stream=stream,
        )

        if max_tokens:
            request_data.max_tokens = max_tokens

        # Use model_dump instead of dict
        payload = request_data.model_dump(exclude_none=True)

        try:
            # Dynamically import aiohttp only when needed
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions", headers=headers, json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error("OpenRouter API error (%s): %s", response.status, error_text)
                        # Consider raising a more specific custom exception
                        raise Exception(
                            f"OpenRouter API returned status code {response.status}: {error_text}"
                        )

                    if stream:
                        # Return the response object directly for the caller to handle streaming
                        # Or process it here if consistent handling is preferred
                        # For now, returning the processed list for simplicity in this example fix
                        # In a real scenario, yielding chunks might be better:
                        # async for chunk in self._process_streaming_response_async(response): yield chunk
                        processed_stream = await self._process_streaming_response_async(response)
                        # Assuming the caller expects a final aggregated dictionary for stream=True too for now
                        # This might need adjustment based on how streaming is handled upstream
                        # Let's aggregate the content for simplicity here
                        full_content = ""
                        usage = {}
                        finish_reason = "stop"
                        final_model = model
                        for chunk_resp in processed_stream:
                            if chunk_resp.get("choices") and len(chunk_resp["choices"]) > 0:
                                delta = chunk_resp["choices"][0].get("delta", {})
                                full_content += delta.get("content", "")
                                if chunk_resp["choices"][0].get("finish_reason"):
                                    finish_reason = chunk_resp["choices"][0]["finish_reason"]
                            if chunk_resp.get("usage"):
                                usage = chunk_resp["usage"]
                            if chunk_resp.get("model"):
                                final_model = chunk_resp["model"]

                        # Return a structure similar to the non-streaming one
                        return {
                            "choices": [
                                {
                                    "message": {"role": "assistant", "content": full_content},
                                    "finish_reason": finish_reason,
                                }
                            ],
                            "model": final_model,
                            "usage": usage,
                        }

                    else:
                        # Process non-streaming response
                        response_json = await response.json()
                        return response_json  # Return the full JSON response

        except aiohttp.ClientError as ce:
            logger.error("Network error calling OpenRouter API: %s", str(ce))
            raise Exception(f"Network error calling OpenRouter API: {str(ce)}") from ce
        except Exception as e:
            # Log error without exposing the API key
            logger.error(
                "Error calling OpenRouter API: %s",
                str(e).replace(self.api_key, "***MASKED***") if self.api_key else str(e),
                exc_info=True,  # Include traceback for better debugging
            )
            # Re-raise the original exception to preserve traceback
            raise

    # Ensure this helper function is correctly indented outside the chat_completion method
    async def _process_streaming_response_async(self, response) -> List[Dict[str, Any]]:
        """Process a streaming response from OpenRouter asynchronously, yielding JSON chunks."""
        # This implementation collects all chunks; consider yielding for true streaming
        results = []
        try:
            async for line in response.content:
                line = line.strip()
                if not line:
                    continue
                if line == b"data: [DONE]":
                    logger.debug("Received [DONE] marker from OpenRouter stream.")
                    break
                if line.startswith(b"data: "):
                    json_str = line[len(b"data: ") :].decode("utf-8")
                    try:
                        chunk_data = json.loads(json_str)
                        results.append(chunk_data)  # Collect results
                        # yield chunk_data # Use yield for true async generator behavior
                    except json.JSONDecodeError:
                        logger.error(
                            "Error decoding JSON chunk from OpenRouter stream: %s", json_str
                        )
                else:
                    logger.warning("Received unexpected line from OpenRouter stream: %s", line)
        except Exception as e:
            logger.error("Error processing OpenRouter stream: %s", str(e), exc_info=True)
            # Depending on desired behavior, you might re-raise or yield an error indicator
        return results  # Return collected results

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
                    "usage": response.get("usage", {}),
                }
            else:
                logger.error("Invalid response format from OpenRouter")
                return {
                    "content": "Error: Invalid response from model provider",
                    "role": "assistant",
                }
        except Exception as e:
            logger.error("Error formatting OpenRouter response: %s", str(e))
            return {"content": "Error processing response", "role": "assistant"}


# Ensure no trailing code or incorrect indentation at the end of the file
