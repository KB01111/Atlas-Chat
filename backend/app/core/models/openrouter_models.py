"""
Pydantic AI Integration for OpenRouter in AtlasChat
Provides Pydantic models for structured data handling with OpenRouter
"""

from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
import json

class OpenRouterMessageContent(BaseModel):
    """Content of a message that can be text or structured with tool calls"""
    model_config = ConfigDict(extra="allow")
    
    type: Literal["text", "tool_call"] = Field(default="text", description="Type of message content")
    text: Optional[str] = Field(None, description="Text content if type is text")
    tool_call: Optional[Dict[str, Any]] = Field(None, description="Tool call details if type is tool_call")
    
    @field_validator("tool_call", mode="after")
    def validate_tool_call(cls, v, info):
        values = info.data
        if values.get("type") == "tool_call" and not v:
            raise ValueError("tool_call must be provided when type is tool_call")
        return v
    
    @field_validator("text", mode="after")
    def validate_text(cls, v, info):
        values = info.data
        if values.get("type") == "text" and not v:
            raise ValueError("text must be provided when type is text")
        return v

class OpenRouterMessage(BaseModel):
    """Message for OpenRouter API with role and content"""
    model_config = ConfigDict(extra="allow")
    
    role: Literal["system", "user", "assistant", "tool"] = Field(..., description="Role of the message sender")
    content: Union[str, OpenRouterMessageContent, List[OpenRouterMessageContent]] = Field(
        ..., description="Content of the message"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format expected by OpenRouter API"""
        if isinstance(self.content, str):
            return {"role": self.role, "content": self.content}
        else:
            # Handle structured content
            return {"role": self.role, "content": json.dumps(self.content.model_dump())}

class ToolDefinition(BaseModel):
    """Definition of a tool that can be used by the agent"""
    model_config = ConfigDict(extra="allow")
    
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of what the tool does")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters for the tool")
    required: Optional[List[str]] = Field(None, description="Required parameters")

class OpenRouterAgentConfig(BaseModel):
    """Configuration for an OpenRouter agent"""
    model_config = ConfigDict(extra="allow")
    
    model: str = Field(..., description="Model identifier (e.g., 'deepseek/deepseek-v3')")
    temperature: float = Field(0.7, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    top_p: Optional[float] = Field(None, description="Top-p sampling parameter")
    presence_penalty: Optional[float] = Field(None, description="Presence penalty parameter")
    frequency_penalty: Optional[float] = Field(None, description="Frequency penalty parameter")

class OpenRouterCompletionRequest(BaseModel):
    """Request for OpenRouter chat completion"""
    model_config = ConfigDict(extra="allow")
    
    model: str = Field(..., description="Model identifier")
    messages: List[OpenRouterMessage] = Field(..., description="Messages for the conversation")
    temperature: float = Field(0.7, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    stream: bool = Field(False, description="Whether to stream the response")
    tools: Optional[List[ToolDefinition]] = Field(None, description="Tools available to the model")
    
    def to_api_format(self) -> Dict[str, Any]:
        """Convert to format expected by OpenRouter API"""
        result = {
            "model": self.model,
            "messages": [m.to_dict() for m in self.messages],
            "temperature": self.temperature,
            "stream": self.stream
        }
        
        if self.max_tokens:
            result["max_tokens"] = self.max_tokens
            
        if self.tools:
            result["tools"] = [t.model_dump() for t in self.tools]
            
        return result

class OpenRouterToolCall(BaseModel):
    """Tool call in an OpenRouter response"""
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(..., description="ID of the tool call")
    type: Literal["function"] = Field(..., description="Type of tool call")
    function: Dict[str, Any] = Field(..., description="Function details")

class OpenRouterResponseChoice(BaseModel):
    """Choice in an OpenRouter response"""
    model_config = ConfigDict(extra="allow")
    
    index: int = Field(..., description="Index of the choice")
    message: Dict[str, Any] = Field(..., description="Message content")
    finish_reason: str = Field(..., description="Reason for finishing")

class OpenRouterUsage(BaseModel):
    """Token usage information"""
    model_config = ConfigDict(extra="allow")
    
    prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
    completion_tokens: int = Field(..., description="Number of tokens in the completion")
    total_tokens: int = Field(..., description="Total number of tokens used")

class OpenRouterCompletionResponse(BaseModel):
    """Response from OpenRouter chat completion"""
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(..., description="ID of the completion")
    object: str = Field(..., description="Object type")
    created: int = Field(..., description="Creation timestamp")
    model: str = Field(..., description="Model used")
    choices: List[OpenRouterResponseChoice] = Field(..., description="Completion choices")
    usage: OpenRouterUsage = Field(..., description="Token usage information")
    
    def get_content(self) -> str:
        """Get the content from the first choice"""
        if not self.choices:
            return ""
        return self.choices[0].message.get("content", "")
    
    def get_tool_calls(self) -> List[Dict[str, Any]]:
        """Get tool calls from the first choice"""
        if not self.choices:
            return []
        return self.choices[0].message.get("tool_calls", [])
    
    def to_atlaschat_format(self) -> Dict[str, Any]:
        """Convert to format expected by AtlasChat"""
        if not self.choices:
            return {"content": "", "role": "assistant"}
            
        message = self.choices[0].message
        
        return {
            "content": message.get("content", ""),
            "role": "assistant",
            "model": self.model,
            "finish_reason": self.choices[0].finish_reason,
            "usage": self.usage.model_dump(),
            "tool_calls": message.get("tool_calls", [])
        }

# Graphiti integration models
class GraphitiNode(BaseModel):
    """Node in a Graphiti knowledge graph"""
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(..., description="ID of the node")
    label: str = Field(..., description="Label of the node")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Properties of the node")

class GraphitiRelationship(BaseModel):
    """Relationship in a Graphiti knowledge graph"""
    model_config = ConfigDict(extra="allow")
    
    source: str = Field(..., description="ID of the source node")
    target: str = Field(..., description="ID of the target node")
    type: str = Field(..., description="Type of the relationship")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Properties of the relationship")

class GraphitiEpisode(BaseModel):
    """Episode in Graphiti episodic memory"""
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(..., description="ID of the episode")
    timestamp: int = Field(..., description="Timestamp of the episode")
    content: str = Field(..., description="Content of the episode")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata for the episode")
    
    def to_nodes_and_relationships(self) -> Dict[str, Any]:
        """Convert episode to nodes and relationships for the knowledge graph"""
        # This is a simplified implementation
        # In a real implementation, you would parse the content and extract entities and relationships
        
        # Create a node for the episode
        episode_node = GraphitiNode(
            id=f"episode:{self.id}",
            label="Episode",
            properties={
                "content": self.content,
                "timestamp": self.timestamp,
                **self.metadata
            }
        )
        
        # Return the node
        return {
            "nodes": [episode_node.model_dump()],
            "relationships": []
        }
