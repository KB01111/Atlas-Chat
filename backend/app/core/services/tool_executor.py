from typing import Dict, Any, List, Optional
import e2b
from app.models.models import RequestContext
from app.core.logging_config import setup_logging

logger = setup_logging()

class ToolExecutor:
    """Centralized service for executing tools"""
    
    def __init__(self):
        """Initialize the Tool Executor"""
        # Initialize E2B sandbox
        try:
            self.e2b_client = e2b.Sandbox(
                timeout=60,  # 60 second timeout
                on_stderr=self._handle_stderr,
                on_stdout=self._handle_stdout
            )
            logger.info("E2B sandbox initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing E2B sandbox: {str(e)}")
            self.e2b_client = None
        
        # Graphiti client would be initialized here in a real implementation
        # self.graphiti_client = graphiti_core.Graphiti(...)
        
        logger.info("ToolExecutor initialized")
    
    def _handle_stdout(self, data: str):
        """Handle stdout streaming from E2B sandbox"""
        logger.debug(f"E2B stdout: {data}")
        
    def _handle_stderr(self, data: str):
        """Handle stderr streaming from E2B sandbox"""
        logger.debug(f"E2B stderr: {data}")
    
    async def execute_code(self, code: str, language: str, context: RequestContext) -> Dict[str, Any]:
        """
        Execute code in E2B sandbox environment
        
        Args:
            code: Code to execute
            language: Programming language (python, javascript, etc.)
            context: Request context
            
        Returns:
            Dictionary containing execution results
        """
        logger.info(f"ToolExecutor.execute_code: Executing {language} code for thread_id={context.thread_id}")
        
        # Validate inputs
        if not code or not language:
            error_msg = "Code and language must be provided"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # Validate language is supported
        supported_languages = ["python", "javascript", "typescript", "bash"]
        if language.lower() not in supported_languages:
            error_msg = f"Language {language} not supported. Supported languages: {', '.join(supported_languages)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # Check if E2B client is initialized
        if not self.e2b_client:
            error_msg = "E2B sandbox is not initialized"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        try:
            # Execute code based on language
            if language.lower() == "python":
                result = await self.e2b_client.run_python(code)
            elif language.lower() == "javascript":
                result = await self.e2b_client.run_javascript(code)
            elif language.lower() == "typescript":
                result = await self.e2b_client.run_typescript(code)
            elif language.lower() == "bash":
                result = await self.e2b_client.run_bash(code)
            
            # Process result
            output = {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.exit_code
            }
            
            # Log audit event
            audit_details = {
                "action": "execute_code",
                "language": language,
                "code_length": len(code),
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": True,
                "exit_code": result.exit_code
            }
            logger.info(f"AUDIT: {audit_details}")
            
            return output
            
        except Exception as e:
            error_msg = f"Error executing code: {str(e)}"
            logger.error(error_msg)
            
            # Log audit event for error
            audit_details = {
                "action": "execute_code",
                "language": language,
                "code_length": len(code),
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": False,
                "error": str(e)
            }
            logger.info(f"AUDIT: {audit_details}")
            
            return {"success": False, "error": error_msg}
    
    async def write_file(self, file_path: str, content: str, context: RequestContext) -> Dict[str, Any]:
        """
        Write content to a file in the sandbox
        
        Args:
            file_path: Path to the file
            content: Content to write
            context: Request context
            
        Returns:
            Dictionary indicating success or failure
        """
        logger.info(f"ToolExecutor.write_file: Writing to {file_path} for thread_id={context.thread_id}")
        
        # Check if E2B client is initialized
        if not self.e2b_client:
            error_msg = "E2B sandbox is not initialized"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        try:
            # Validate file path (security check)
            if ".." in file_path or file_path.startswith("/"):
                error_msg = "Invalid file path. Path cannot contain '..' or start with '/'"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # Write file to sandbox
            await self.e2b_client.filesystem.write(file_path, content)
            
            # Log audit event
            audit_details = {
                "action": "write_file",
                "file_path": file_path,
                "content_length": len(content),
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": True
            }
            logger.info(f"AUDIT: {audit_details}")
            
            return {"success": True}
            
        except Exception as e:
            error_msg = f"Error writing file: {str(e)}"
            logger.error(error_msg)
            
            # Log audit event for error
            audit_details = {
                "action": "write_file",
                "file_path": file_path,
                "content_length": len(content),
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": False,
                "error": str(e)
            }
            logger.info(f"AUDIT: {audit_details}")
            
            return {"success": False, "error": error_msg}
    
    async def read_file(self, file_path: str, context: RequestContext) -> Dict[str, Any]:
        """
        Read content from a file in the sandbox
        
        Args:
            file_path: Path to the file
            context: Request context
            
        Returns:
            Dictionary containing file content or error
        """
        logger.info(f"ToolExecutor.read_file: Reading from {file_path} for thread_id={context.thread_id}")
        
        # Check if E2B client is initialized
        if not self.e2b_client:
            error_msg = "E2B sandbox is not initialized"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        try:
            # Validate file path (security check)
            if ".." in file_path or file_path.startswith("/"):
                error_msg = "Invalid file path. Path cannot contain '..' or start with '/'"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # Read file from sandbox
            content = await self.e2b_client.filesystem.read(file_path)
            
            # Log audit event
            audit_details = {
                "action": "read_file",
                "file_path": file_path,
                "content_length": len(content),
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": True
            }
            logger.info(f"AUDIT: {audit_details}")
            
            return {"success": True, "content": content}
            
        except Exception as e:
            error_msg = f"Error reading file: {str(e)}"
            logger.error(error_msg)
            
            # Log audit event for error
            audit_details = {
                "action": "read_file",
                "file_path": file_path,
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": False,
                "error": str(e)
            }
            logger.info(f"AUDIT: {audit_details}")
            
            return {"success": False, "error": error_msg}
    
    async def install_packages(self, packages: List[str], language: str, context: RequestContext) -> Dict[str, Any]:
        """
        Install packages in the sandbox
        
        Args:
            packages: List of packages to install
            language: Programming language (python, javascript, etc.)
            context: Request context
            
        Returns:
            Dictionary indicating success or failure
        """
        logger.info(f"ToolExecutor.install_packages: Installing {language} packages for thread_id={context.thread_id}")
        
        # Check if E2B client is initialized
        if not self.e2b_client:
            error_msg = "E2B sandbox is not initialized"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        try:
            # Validate language
            if language.lower() == "python":
                result = await self.e2b_client.install_python_packages(packages)
            elif language.lower() in ["javascript", "typescript"]:
                result = await self.e2b_client.install_npm_packages(packages)
            else:
                error_msg = f"Package installation not supported for {language}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # Log audit event
            audit_details = {
                "action": "install_packages",
                "language": language,
                "packages": packages,
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": True
            }
            logger.info(f"AUDIT: {audit_details}")
            
            return {"success": True, "stdout": result.stdout, "stderr": result.stderr}
            
        except Exception as e:
            error_msg = f"Error installing packages: {str(e)}"
            logger.error(error_msg)
            
            # Log audit event for error
            audit_details = {
                "action": "install_packages",
                "language": language,
                "packages": packages,
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": False,
                "error": str(e)
            }
            logger.info(f"AUDIT: {audit_details}")
            
            return {"success": False, "error": error_msg}
    
    async def add_graphiti_episode(self, episode_text: str, context: RequestContext, name: str = "interaction") -> bool:
        """
        Add an episode to Graphiti
        
        Args:
            episode_text: Text of the episode
            context: Request context
            name: Name of the episode
            
        Returns:
            True if successful, False otherwise
        """
        # Check if agent uses Graphiti
        if not context.agent_definition.get("uses_graphiti", False):
            logger.info(f"ToolExecutor.add_graphiti_episode: Agent {context.agent_definition['agent_id']} does not use Graphiti, skipping")
            return False
        
        logger.info(f"ToolExecutor.add_graphiti_episode: Adding episode for thread_id={context.thread_id}")
        
        try:
            # In a real implementation, we would:
            # 1. Call graphiti.add_episode
            # 2. Log action/success/failure
            
            # For now, just log and return success
            audit_details = {
                "action": "add_graphiti_episode",
                "episode_name": name,
                "episode_length": len(episode_text),
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": True
            }
            logger.info(f"AUDIT: {audit_details}")
            
            return True
            
        except Exception as e:
            error_msg = f"Error adding Graphiti episode: {str(e)}"
            logger.error(error_msg)
            
            # Log audit event for error
            audit_details = {
                "action": "add_graphiti_episode",
                "episode_name": name,
                "episode_length": len(episode_text),
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": False,
                "error": str(e)
            }
            logger.info(f"AUDIT: {audit_details}")
            
            return False
    
    async def search_graphiti(self, query: str, context: RequestContext) -> List[Dict[str, Any]]:
        """
        Search Graphiti for relevant information
        
        Args:
            query: Search query
            context: Request context
            
        Returns:
            List of search results
        """
        # Check if agent uses Graphiti
        if not context.agent_definition.get("uses_graphiti", False):
            logger.info(f"ToolExecutor.search_graphiti: Agent {context.agent_definition['agent_id']} does not use Graphiti, skipping")
            return []
        
        logger.info(f"ToolExecutor.search_graphiti: Searching with query '{query}' for thread_id={context.thread_id}")
        
        try:
            # In a real implementation, we would:
            # 1. Call graphiti.search
            # 2. Log query/results/errors
            
            # For now, just return placeholder results
            results = [
                {"type": "episode", "id": "ep123", "text": "This is a placeholder episode result", "score": 0.95},
                {"type": "entity", "id": "ent456", "name": "Example Entity", "score": 0.85}
            ]
            
            # Log audit event
            audit_details = {
                "action": "search_graphiti",
                "query": query,
                "result_count": len(results),
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": True
            }
            logger.info(f"AUDIT: {audit_details}")
            
            return results
            
        except Exception as e:
            error_msg = f"Error searching Graphiti: {str(e)}"
            logger.error(error_msg)
            
            # Log audit event for error
            audit_details = {
                "action": "search_graphiti",
                "query": query,
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": False,
                "error": str(e)
            }
            logger.info(f"AUDIT: {audit_details}")
            
            return []
    
    async def call_specialized_model(self, model_name: str, prompt: str, context: RequestContext) -> str:
        """
        Call a specialized model
        
        Args:
            model_name: Name of the model to call
            prompt: Prompt to send to the model
            context: Request context
            
        Returns:
            Model response as string
        """
        logger.info(f"ToolExecutor.call_specialized_model: Calling model '{model_name}' for thread_id={context.thread_id}")
        
        try:
            # In a real implementation, we would:
            # 1. Check if agent uses Graphiti
            # 2. Call self.search_graphiti to get context
            # 3. Format/inject context
            # 4. Call external LLM via Google/Anthropic SDK
            # 5. Potentially call self.add_graphiti_episode
            
            # For now, just return a placeholder response
            result = f"Specialized model response placeholder (would use {model_name} in production)\nPrompt length: {len(prompt)} characters"
            
            # Log audit event
            audit_details = {
                "action": "call_specialized_model",
                "model_name": model_name,
                "prompt_length": len(prompt),
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": True
            }
            logger.info(f"AUDIT: {audit_details}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error calling specialized model: {str(e)}"
            logger.error(error_msg)
            
            # Log audit event for error
            audit_details = {
                "action": "call_specialized_model",
                "model_name": model_name,
                "prompt_length": len(prompt),
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": False,
                "error": str(e)
            }
            logger.info(f"AUDIT: {audit_details}")
            
            return error_msg
    
    async def retrieve_relevant_context(self, query: str, context: RequestContext) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from Qdrant
        
        Args:
            query: Search query
            context: Request context
            
        Returns:
            List of relevant text chunks
        """
        logger.info(f"ToolExecutor.retrieve_relevant_context: Retrieving context for query '{query}' for thread_id={context.thread_id}")
        
        try:
            # In a real implementation, we would:
            # 1. Embed query using sentence-transformers
            # 2. Search Qdrant collection (filter by context.thread_id)
            # 3. Return top N text chunks
            
            # For now, just return placeholder results
            results = [
                {"text": "This is a placeholder RAG result 1", "score": 0.92},
                {"text": "This is a placeholder RAG result 2", "score": 0.85}
            ]
            
            # Log audit event
            audit_details = {
                "action": "retrieve_relevant_context",
                "query": query,
                "result_count": len(results),
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": True
            }
            logger.info(f"AUDIT: {audit_details}")
            
            return results
            
        except Exception as e:
            error_msg = f"Error retrieving relevant context: {str(e)}"
            logger.error(error_msg)
            
            # Log audit event for error
            audit_details = {
                "action": "retrieve_relevant_context",
                "query": query,
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": False,
                "error": str(e)
            }
            logger.info(f"AUDIT: {audit_details}")
            
            return []
    
    def close(self):
        """Close the E2B sandbox and release resources"""
        if self.e2b_client:
            try:
                self.e2b_client.close()
                logger.info("E2B sandbox closed successfully")
            except Exception as e:
                logger.error(f"Error closing E2B sandbox: {str(e)}")
