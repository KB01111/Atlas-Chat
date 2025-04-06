"""
LangGraph integration module for Atlas-Chat.

This module provides integration with LangGraph for creating complex agent workflows
and graph-based agent architectures.
"""

from typing import Dict, Any, List, Optional, Union, Callable
import logging
import os
from pydantic import BaseModel, Field

# Import agent factory components
from ...services.agent_factory.agent_definition import (
    AgentDefinition,
    AgentRequest,
    AgentResponse,
    AgentMessage,
)
from ...services.agent_factory.agent_factory import AgentProvider
from ...services.model_routing.model_router import ModelRouter

logger = logging.getLogger(__name__)

# Try to import langgraph library
try:
    import langgraph.graph as lg
    from langgraph.graph import StateGraph, END

    LANGGRAPH_AVAILABLE = True
except ImportError:
    logger.warning(
        "langgraph library not available. Install with 'pip install langgraph'"
    )
    LANGGRAPH_AVAILABLE = False


class GraphState(BaseModel):
    """State for a LangGraph agent."""

    messages: List[Dict[str, Any]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    tools: Dict[str, Any] = Field(default_factory=dict)
    current_node: str = "start"
    next_node: Optional[str] = None
    error: Optional[str] = None


class LangGraphProvider(AgentProvider):
    """LangGraph provider for agent factory."""

    def __init__(self, model_router: Optional[ModelRouter] = None):
        """
        Initialize LangGraph provider.

        Args:
            model_router: Model router for selecting models
        """
        self.model_router = model_router
        self.agents: Dict[str, AgentDefinition] = {}
        self.graphs: Dict[str, Any] = {}

        # Check if LangGraph is available
        if not LANGGRAPH_AVAILABLE:
            logger.warning(
                "LangGraph is not available. Some functionality will be limited."
            )

    def create_agent(self, definition: AgentDefinition) -> str:
        """
        Create an agent.

        Args:
            definition: Agent definition

        Returns:
            Agent ID
        """
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("langgraph library not available")

        # Store agent definition
        agent_id = definition.agent_id
        self.agents[agent_id] = definition

        # Create graph
        graph = self._create_graph(definition)
        self.graphs[agent_id] = graph

        logger.info(f"Created LangGraph agent: {definition.name} ({agent_id})")

        return agent_id

    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.

        Args:
            agent_id: Agent ID

        Returns:
            True if successful, False otherwise
        """
        if agent_id in self.agents:
            del self.agents[agent_id]

            if agent_id in self.graphs:
                del self.graphs[agent_id]

            return True

        return False

    def get_agent(self, agent_id: str) -> Optional[AgentDefinition]:
        """
        Get agent definition.

        Args:
            agent_id: Agent ID

        Returns:
            Agent definition or None if not found
        """
        return self.agents.get(agent_id)

    def update_agent(
        self, agent_id: str, updates: Dict[str, Any]
    ) -> Optional[AgentDefinition]:
        """
        Update agent definition.

        Args:
            agent_id: Agent ID
            updates: Updates to apply

        Returns:
            Updated agent definition or None if not found
        """
        if agent_id not in self.agents:
            return None

        # Get current definition
        current = self.agents[agent_id]

        # Apply updates
        updated_dict = current.dict()
        updated_dict.update(updates)

        # Create new definition
        updated = AgentDefinition(**updated_dict)

        # Update agents
        self.agents[agent_id] = updated

        # Recreate graph
        graph = self._create_graph(updated)
        self.graphs[agent_id] = graph

        return updated

    def process_request(self, request: AgentRequest) -> AgentResponse:
        """
        Process a request to an agent.

        Args:
            request: Agent request

        Returns:
            Agent response
        """
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("langgraph library not available")

        # Get agent definition
        agent_id = request.agent_id
        definition = self.agents.get(agent_id)
        if not definition:
            raise ValueError(f"Agent not found: {agent_id}")

        # Get graph
        graph = self.graphs.get(agent_id)
        if not graph:
            raise ValueError(f"Graph not found for agent: {agent_id}")

        # Prepare messages
        messages = self._prepare_messages(request.messages, definition)

        # Prepare initial state
        state = GraphState(
            messages=messages,
            context={
                "agent_id": agent_id,
                "model_id": definition.model_id,
                "system_prompt": definition.system_prompt,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "stream": request.stream,
                "metadata": request.metadata,
            },
            tools={tool: {} for tool in definition.tools},
        )

        # Run graph
        try:
            final_state = graph.invoke(state)

            # Extract response from final state
            response_content = self._extract_response(final_state)

            # Create response
            response = AgentResponse(
                agent_id=agent_id,
                message=AgentMessage(role="assistant", content=response_content),
                usage={},  # Usage info not available from LangGraph
                metadata={"graph_execution": "success"},
            )

            return response

        except Exception as e:
            logger.error(f"Error running LangGraph: {e}")

            # Create error response
            response = AgentResponse(
                agent_id=agent_id,
                message=AgentMessage(
                    role="assistant",
                    content="I encountered an error while processing your request.",
                ),
                usage={},
                metadata={"graph_execution": "error", "error": str(e)},
            )

            return response

    def _prepare_messages(
        self, messages: List[AgentMessage], definition: AgentDefinition
    ) -> List[Dict[str, Any]]:
        """
        Prepare messages for LangGraph.

        Args:
            messages: Agent messages
            definition: Agent definition

        Returns:
            Prepared messages
        """
        # Add system prompt if not present
        has_system = any(msg.role == "system" for msg in messages)

        prepared = []

        if not has_system and definition.system_prompt:
            prepared.append({"role": "system", "content": definition.system_prompt})

        # Add user and assistant messages
        for msg in messages:
            prepared.append({"role": msg.role, "content": msg.content})

        return prepared

    def _create_graph(self, definition: AgentDefinition) -> Any:
        """
        Create a LangGraph for an agent.

        Args:
            definition: Agent definition

        Returns:
            LangGraph
        """
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("langgraph library not available")

        # Create nodes
        nodes = {
            "start": self._create_start_node(),
            "process": self._create_process_node(definition),
            "tool_executor": self._create_tool_executor_node(definition),
            "response_generator": self._create_response_generator_node(definition),
        }

        # Create graph
        builder = StateGraph(GraphState)

        # Add nodes
        for name, node in nodes.items():
            builder.add_node(name, node)

        # Add edges
        builder.add_edge("start", "process")
        builder.add_conditional_edges(
            "process",
            self._route_process,
            {
                "tool_executor": "tool_executor",
                "response_generator": "response_generator",
                END: END,
            },
        )
        builder.add_edge("tool_executor", "process")
        builder.add_edge("response_generator", END)

        # Set entry point
        builder.set_entry_point("start")

        # Compile graph
        graph = builder.compile()

        return graph

    def _create_start_node(self) -> Callable:
        """
        Create start node for LangGraph.

        Returns:
            Node function
        """

        def start_node(state: GraphState) -> GraphState:
            """Start node for LangGraph."""
            # Initialize state
            state.current_node = "start"
            state.next_node = "process"
            return state

        return start_node

    def _create_process_node(self, definition: AgentDefinition) -> Callable:
        """
        Create process node for LangGraph.

        Args:
            definition: Agent definition

        Returns:
            Node function
        """
        model_router = self.model_router

        def process_node(state: GraphState) -> GraphState:
            """Process node for LangGraph."""
            # Update current node
            state.current_node = "process"

            # Get context
            context = state.context
            model_id = context.get("model_id", definition.model_id)

            # Check if we need to use a tool
            last_message = state.messages[-1] if state.messages else None
            if (
                last_message
                and last_message.get("role") == "assistant"
                and "tool_calls" in last_message
            ):
                state.next_node = "tool_executor"
                return state

            # Check if we need to generate a response
            if last_message and last_message.get("role") == "user":
                state.next_node = "response_generator"
                return state

            # Default to end
            state.next_node = END
            return state

        return process_node

    def _create_tool_executor_node(self, definition: AgentDefinition) -> Callable:
        """
        Create tool executor node for LangGraph.

        Args:
            definition: Agent definition

        Returns:
            Node function
        """

        def tool_executor_node(state: GraphState) -> GraphState:
            """Tool executor node for LangGraph."""
            # Update current node
            state.current_node = "tool_executor"

            # Get last message
            last_message = state.messages[-1] if state.messages else None
            if not last_message or "tool_calls" not in last_message:
                state.next_node = "process"
                return state

            # Execute tool calls
            tool_calls = last_message.get("tool_calls", [])
            tool_results = []

            for tool_call in tool_calls:
                tool_id = tool_call.get("id")
                tool_name = tool_call.get("function", {}).get("name")
                tool_args = tool_call.get("function", {}).get("arguments", "{}")

                # Check if tool is available
                if tool_name not in state.tools:
                    tool_results.append(
                        {
                            "tool_call_id": tool_id,
                            "role": "tool",
                            "name": tool_name,
                            "content": f"Error: Tool '{tool_name}' not available",
                        }
                    )
                    continue

                # TODO: Implement actual tool execution
                # For now, just return a placeholder result
                tool_results.append(
                    {
                        "tool_call_id": tool_id,
                        "role": "tool",
                        "name": tool_name,
                        "content": f"Result from {tool_name} with args {tool_args}",
                    }
                )

            # Add tool results to messages
            state.messages.extend(tool_results)

            # Continue processing
            state.next_node = "process"
            return state

        return tool_executor_node

    def _create_response_generator_node(self, definition: AgentDefinition) -> Callable:
        """
        Create response generator node for LangGraph.

        Args:
            definition: Agent definition

        Returns:
            Node function
        """
        model_router = self.model_router

        def response_generator_node(state: GraphState) -> GraphState:
            """Response generator node for LangGraph."""
            # Update current node
            state.current_node = "response_generator"

            # Get context
            context = state.context
            model_id = context.get("model_id", definition.model_id)
            system_prompt = context.get("system_prompt", definition.system_prompt)
            max_tokens = context.get("max_tokens")
            temperature = context.get("temperature")

            # Prepare messages for model
            model_messages = []

            # Add system prompt if not present
            has_system = any(msg.get("role") == "system" for msg in state.messages)
            if not has_system and system_prompt:
                model_messages.append({"role": "system", "content": system_prompt})

            # Add other messages
            model_messages.extend(state.messages)

            try:
                # Get model
                model = model_router.get_model(model_id)

                # Generate response
                response = model.generate(
                    messages=model_messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                # Add response to messages
                state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                logger.error(f"Error generating response: {e}")
                state.error = str(e)

                # Add error response to messages
                state.messages.append(
                    {
                        "role": "assistant",
                        "content": "I encountered an error while processing your request.",
                    }
                )

            # End graph
            state.next_node = END
            return state

        return response_generator_node

    def _route_process(self, state: GraphState) -> str:
        """
        Route process node.

        Args:
            state: Graph state

        Returns:
            Next node
        """
        return state.next_node or END

    def _extract_response(self, state: GraphState) -> str:
        """
        Extract response from final state.

        Args:
            state: Final graph state

        Returns:
            Response content
        """
        # Get last assistant message
        for msg in reversed(state.messages):
            if msg.get("role") == "assistant":
                return msg.get("content", "")

        return "I don't have a response at this time."
