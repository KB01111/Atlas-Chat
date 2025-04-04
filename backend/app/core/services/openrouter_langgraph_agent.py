"""
OpenRouter LangGraph Integration for AtlasChat
Implements LangGraph support for OpenRouter models
"""

import os
import logging
from typing import Dict, Any, List, Optional, Callable, AsyncGenerator
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from app.core.services.openrouter_client import OpenRouterClient

logger = logging.getLogger(__name__)

class OpenRouterLangGraphAgent:
    """
    Implementation of LangGraph Agent using OpenRouter API
    Compatible with AtlasChat's dual-engine architecture
    """
    
    def __init__(self):
        self.client = OpenRouterClient()
        
    async def create_graph(self, 
                          agent_config: Dict[str, Any],
                          tools: List[Dict[str, Any]] = None) -> StateGraph:
        """
        Create a LangGraph for the agent using OpenRouter
        
        Args:
            agent_config: Configuration for the agent
            tools: List of tools available to the agent
            
        Returns:
            LangGraph StateGraph
        """
        try:
            # Extract configuration
            model = agent_config.get("model", "deepseek/deepseek-v3")
            temperature = agent_config.get("temperature", 0.7)
            max_tokens = agent_config.get("max_tokens", None)
            
            # Define the state schema
            class AgentState(dict):
                """State for the agent graph"""
                messages: List[Dict[str, str]]
                tools: Optional[List[Dict[str, Any]]]
                
            # Define the nodes for the graph
            async def thinking(state: AgentState) -> AgentState:
                """Node for thinking and generating responses"""
                messages = state["messages"]
                tools = state.get("tools", [])
                
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
                    stream=False
                )
                
                # Format response and add to messages
                formatted_response = self.client.format_openrouter_response(response)
                state["messages"].append(formatted_response)
                
                return state
                
            async def tool_execution(state: AgentState) -> AgentState:
                """Node for executing tools based on agent response"""
                # Get the last message (agent's response)
                last_message = state["messages"][-1]
                content = last_message.get("content", "")
                
                # Check if the message contains a tool call
                # This is a simplified implementation - in production you'd want more robust parsing
                if "I'll use the" in content and any(tool["name"] in content for tool in state.get("tools", [])):
                    # Extract tool name and parameters
                    # This is a placeholder - you'd need proper parsing logic here
                    tool_name = next((tool["name"] for tool in state.get("tools", []) if tool["name"] in content), None)
                    
                    if tool_name:
                        # Log the tool call
                        logger.info(f"Tool call detected: {tool_name}")
                        
                        # In a real implementation, you would execute the tool here
                        # For now, we'll just add a placeholder message
                        state["messages"].append({
                            "role": "system",
                            "content": f"Tool {tool_name} was executed. This is a placeholder for actual tool execution."
                        })
                        
                        # Return to thinking node for follow-up
                        return {"messages": state["messages"], "tools": state.get("tools", []), "next": "thinking"}
                
                # If no tool call detected, end the graph
                return {"messages": state["messages"], "tools": state.get("tools", []), "next": END}
            
            # Create the graph
            workflow = StateGraph(AgentState)
            
            # Add nodes
            workflow.add_node("thinking", thinking)
            workflow.add_node("tool_execution", tool_execution)
            
            # Add edges
            workflow.add_edge("thinking", "tool_execution")
            workflow.add_edge("tool_execution", "thinking")
            
            # Set entry point
            workflow.set_entry_point("thinking")
            
            return workflow.compile()
            
        except Exception as e:
            logger.error(f"Error creating LangGraph for OpenRouter: {str(e)}")
            raise
            
    async def execute(self, 
                     agent_config: Dict[str, Any],
                     messages: List[Dict[str, str]],
                     tools: List[Dict[str, Any]] = None,
                     stream: bool = False) -> Dict[str, Any]:
        """
        Execute the LangGraph agent using OpenRouter
        
        Args:
            agent_config: Configuration for the agent
            messages: List of messages for the conversation
            tools: List of tools available to the agent
            stream: Whether to stream the response (not supported for LangGraph)
            
        Returns:
            Agent response
        """
        try:
            if stream:
                logger.warning("Streaming not supported for LangGraph agents, falling back to non-streaming")
                
            # Create the graph
            graph = await self.create_graph(agent_config, tools)
            
            # Execute the graph
            initial_state = {"messages": messages, "tools": tools}
            result = await graph.ainvoke(initial_state)
            
            # Return the last message from the result
            return result["messages"][-1]
            
        except Exception as e:
            logger.error(f"Error executing OpenRouter LangGraph agent: {str(e)}")
            return {
                "content": f"Error: {str(e)}",
                "role": "assistant"
            }
