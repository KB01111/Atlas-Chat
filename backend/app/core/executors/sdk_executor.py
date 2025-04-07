import asyncio
import json
import os
from collections.abc import AsyncGenerator
from typing import Any, Dict, List, Optional

from openai import OpenAI
from openai.types.beta.assistant import Assistant
from openai.types.beta.threads import Run

from app.core.logging_config import setup_logging
from app.core.services.tool_executor import ToolExecutor
from app.models.models import RequestContext

logger = setup_logging()


class SDKExecutor:
    """Executor for OpenAI Agents SDK based agents"""

    def __init__(
        self, tool_executor: ToolExecutor = None, api_key: Optional[str] = None
    ):
        """
        Initialize the SDK Executor

        Args:
            tool_executor: ToolExecutor instance for executing tools
            api_key: OpenAI API key (defaults to environment variable)
        """
        self.tool_executor = tool_executor
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.assistants_cache = {}  # Cache assistants by agent_id
        logger.info("SDKExecutor initialized with OpenAI Agents SDK")

    async def execute(
        self,
        agent_definition: Dict[str, Any],
        request_context: RequestContext,
        message: str,
        history: List[Dict[str, str]],
    ) -> AsyncGenerator[str, None]:
        """
        Execute an agent using the OpenAI Agents SDK

        Args:
            agent_definition: Agent definition from database
            request_context: Request context
            message: User message
            history: Conversation history

        Returns:
            AsyncGenerator yielding response chunks
        """
        agent_id = agent_definition.get("agent_id")
        logger.info(f"SDKExecutor.execute: Starting execution for agent_id={agent_id}")

        try:
            # Get allowed_tools and uses_graphiti from agent_definition
            allowed_tools = agent_definition.get("allowed_tools", [])
            uses_graphiti = agent_definition.get("uses_graphiti", False)
            model = agent_definition.get("model", "gpt-4o")
            instructions = agent_definition.get(
                "instructions", "You are a helpful assistant."
            )

            # Check if tool_executor is available
            if not self.tool_executor:
                yield "Error: ToolExecutor not available. Cannot execute agent."
                return

            # Define tools for the OpenAI Assistant
            tools = []

            # Add code execution tool
            if "execute_code" in allowed_tools:
                tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": "execute_code",
                            "description": "Execute code in various programming languages",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "code": {
                                        "type": "string",
                                        "description": "The code to execute",
                                    },
                                    "language": {
                                        "type": "string",
                                        "description": "The programming language (python, javascript, bash, etc.)",
                                        "default": "python",
                                    },
                                },
                                "required": ["code"],
                            },
                        },
                    }
                )

            # Add computer use tools
            if "computer_use" in allowed_tools:
                # File system operations
                tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": "list_files",
                            "description": "List files in a directory",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "path": {
                                        "type": "string",
                                        "description": "Directory path to list files from",
                                    }
                                },
                                "required": ["path"],
                            },
                        },
                    }
                )

                tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": "read_file",
                            "description": "Read content from a file",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "path": {
                                        "type": "string",
                                        "description": "Path to the file to read",
                                    }
                                },
                                "required": ["path"],
                            },
                        },
                    }
                )

                tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": "write_file",
                            "description": "Write content to a file",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "path": {
                                        "type": "string",
                                        "description": "Path to the file to write",
                                    },
                                    "content": {
                                        "type": "string",
                                        "description": "Content to write to the file",
                                    },
                                },
                                "required": ["path", "content"],
                            },
                        },
                    }
                )

                # Process execution
                tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": "execute_command",
                            "description": "Execute a shell command",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "command": {
                                        "type": "string",
                                        "description": "Shell command to execute",
                                    }
                                },
                                "required": ["command"],
                            },
                        },
                    }
                )

            # Add Graphiti tools
            if uses_graphiti:
                if "add_graphiti_episode" in allowed_tools:
                    tools.append(
                        {
                            "type": "function",
                            "function": {
                                "name": "add_graphiti_episode",
                                "description": "Add an episode to Graphiti knowledge graph",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "episode_text": {
                                            "type": "string",
                                            "description": "Text content of the episode",
                                        },
                                        "name": {
                                            "type": "string",
                                            "description": "Name of the episode",
                                            "default": "interaction",
                                        },
                                    },
                                    "required": ["episode_text"],
                                },
                            },
                        }
                    )

                if "search_graphiti" in allowed_tools:
                    tools.append(
                        {
                            "type": "function",
                            "function": {
                                "name": "search_graphiti",
                                "description": "Search the Graphiti knowledge graph",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "query": {
                                            "type": "string",
                                            "description": "Search query",
                                        }
                                    },
                                    "required": ["query"],
                                },
                            },
                        }
                    )

            # Add other tools
            if "call_specialized_model" in allowed_tools:
                tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": "call_specialized_model",
                            "description": "Call a specialized model for specific tasks",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "model_name": {
                                        "type": "string",
                                        "description": "Name of the specialized model",
                                    },
                                    "prompt": {
                                        "type": "string",
                                        "description": "Prompt to send to the model",
                                    },
                                },
                                "required": ["model_name", "prompt"],
                            },
                        },
                    }
                )

            if "retrieve_relevant_context" in allowed_tools:
                tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": "retrieve_relevant_context",
                            "description": "Retrieve relevant context based on a query",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "Query to retrieve context for",
                                    }
                                },
                                "required": ["query"],
                            },
                        },
                    }
                )

            if "web_search" in allowed_tools:
                tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": "web_search",
                            "description": "Search the web for information",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "Search query",
                                    }
                                },
                                "required": ["query"],
                            },
                        },
                    }
                )

            # Get or create an assistant
            assistant = await self._get_or_create_assistant(
                agent_id=agent_id, instructions=instructions, tools=tools, model=model
            )

            # Create a thread or retrieve existing one
            thread_id = request_context.metadata.get("thread_id")
            if not thread_id:
                thread = await self._create_thread()
                thread_id = thread.id
                request_context.metadata["thread_id"] = thread_id

            # Add user message to thread
            await self._add_message_to_thread(thread_id, message, "user")

            # Run the assistant
            run = await self._create_run(thread_id, assistant.id)

            # Stream the response
            async for chunk in self._stream_run_response(thread_id, run.id):
                yield chunk

            logger.info(
                f"SDKExecutor.execute: Completed execution for agent_id={agent_id}"
            )

        except Exception as e:
            logger.error(f"Error in SDKExecutor.execute: {str(e)}")
            yield f"Error: {str(e)}"

    async def _get_or_create_assistant(
        self, agent_id: str, instructions: str, tools: List[Dict[str, Any]], model: str
    ) -> Assistant:
        """
        Get an existing assistant or create a new one

        Args:
            agent_id: ID of the agent
            instructions: Instructions for the assistant
            tools: List of tools for the assistant
            model: Model to use for the assistant

        Returns:
            Assistant object
        """
        # Check if assistant exists in cache
        if agent_id in self.assistants_cache:
            return self.assistants_cache[agent_id]

        # Create a new assistant
        assistant = self.client.beta.assistants.create(
            name=f"Atlas-Chat Agent {agent_id}",
            instructions=instructions,
            tools=tools,
            model=model,
        )

        # Cache the assistant
        self.assistants_cache[agent_id] = assistant

        return assistant

    async def _create_thread(self) -> Any:
        """
        Create a new thread

        Returns:
            Thread object
        """
        return self.client.beta.threads.create()

    async def _add_message_to_thread(
        self, thread_id: str, content: str, role: str = "user"
    ) -> Any:
        """
        Add a message to a thread

        Args:
            thread_id: ID of the thread
            content: Message content
            role: Message role (user or assistant)

        Returns:
            Message object
        """
        return self.client.beta.threads.messages.create(
            thread_id=thread_id, role=role, content=content
        )

    async def _create_run(self, thread_id: str, assistant_id: str) -> Run:
        """
        Create a run for a thread

        Args:
            thread_id: ID of the thread
            assistant_id: ID of the assistant

        Returns:
            Run object
        """
        return self.client.beta.threads.runs.create(
            thread_id=thread_id, assistant_id=assistant_id
        )

    async def _stream_run_response(
        self, thread_id: str, run_id: str
    ) -> AsyncGenerator[str, None]:
        """
        Stream the response from a run

        Args:
            thread_id: ID of the thread
            run_id: ID of the run

        Returns:
            AsyncGenerator yielding response chunks
        """
        # Poll for run completion
        while True:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run_id
            )

            if run.status == "completed":
                break
            elif run.status in ["failed", "cancelled", "expired"]:
                yield f"Run {run_id} ended with status: {run.status}"
                return
            elif run.status == "requires_action":
                # Handle tool calls
                await self._process_tool_calls(
                    thread_id,
                    run_id,
                    run.required_action.submit_tool_outputs.tool_calls,
                )

            # Wait before polling again
            await asyncio.sleep(1)

        # Get messages after run completion
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id, order="asc", after=run_id
        )

        # Yield message content
        for message in messages.data:
            if message.role == "assistant":
                for content_part in message.content:
                    if content_part.type == "text":
                        yield content_part.text.value

    async def _process_tool_calls(
        self, thread_id: str, run_id: str, tool_calls: List[Any]
    ) -> None:
        """
        Process tool calls from a run

        Args:
            thread_id: ID of the thread
            run_id: ID of the run
            tool_calls: List of tool calls
        """
        tool_outputs = []

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            try:
                # Execute the appropriate tool
                output = await self._execute_tool(function_name, function_args)

                # Add the output to the list
                tool_outputs.append(
                    {"tool_call_id": tool_call.id, "output": json.dumps(output)}
                )

            except Exception as e:
                logger.error(f"Error executing tool {function_name}: {str(e)}")
                tool_outputs.append(
                    {
                        "tool_call_id": tool_call.id,
                        "output": json.dumps({"error": str(e)}),
                    }
                )

        # Submit tool outputs
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id, run_id=run_id, tool_outputs=tool_outputs
        )

    async def _execute_tool(self, function_name: str, args: Dict[str, Any]) -> Any:
        """
        Execute a tool function

        Args:
            function_name: Name of the function to execute
            args: Arguments for the function

        Returns:
            Result of the function execution
        """
        # Map function names to tool executor methods
        if function_name == "execute_code":
            return await self.tool_executor.execute_code(
                args.get("code", ""),
                args.get("language", "python"),
                request_context,  # We'll need to pass the request_context here in a real implementation
            )

        elif function_name == "list_files":
            return await self.tool_executor.list_files(args.get("path", "./"), None)

        elif function_name == "read_file":
            return await self.tool_executor.read_file(args.get("path", ""), None)

        elif function_name == "write_file":
            return await self.tool_executor.write_file(
                args.get("path", ""), args.get("content", ""), None
            )

        elif function_name == "execute_command":
            return await self.tool_executor.execute_command(
                args.get("command", ""), None
            )

        elif function_name == "add_graphiti_episode":
            return await self.tool_executor.add_graphiti_episode(
                args.get("episode_text", ""), None, args.get("name", "interaction")
            )

        elif function_name == "search_graphiti":
            return await self.tool_executor.search_graphiti(args.get("query", ""), None)

        elif function_name == "call_specialized_model":
            return await self.tool_executor.call_specialized_model(
                args.get("model_name", ""), args.get("prompt", ""), None
            )

        elif function_name == "retrieve_relevant_context":
            return await self.tool_executor.retrieve_relevant_context(
                args.get("query", ""), None
            )

        elif function_name == "web_search":
            return await self.tool_executor.web_search(args.get("query", ""), None)

        else:
            raise ValueError(f"Unknown function: {function_name}")
