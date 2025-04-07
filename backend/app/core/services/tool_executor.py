import asyncio
from typing import Any, Dict, List

import e2b

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.models.models import RequestContext

logger = setup_logging()

# Common large packages that should be pre-installed
COMMON_PYTHON_PACKAGES = {
    "tensorflow": "2.15.0",
    "torch": "2.1.0",
    "pandas": "2.1.1",
    "numpy": "1.24.3",
    "scikit-learn": "1.3.0",
    "transformers": "4.35.0",
    "matplotlib": "3.8.0",
    "opencv-python": "4.8.0.76",
    "scipy": "1.11.3",
    "nltk": "3.8.1",
    "unstructured": "0.17.2",
}

COMMON_NPM_PACKAGES = {
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "next": "14.0.3",
    "vue": "3.3.8",
    "angular": "17.0.2",
    "express": "4.18.2",
    "axios": "1.6.2",
    "lodash": "4.17.21",
    "typescript": "5.2.2",
}


class ToolExecutor:
    """Centralized service for executing tools"""

    def __init__(self):
        """Initialize the Tool Executor"""
        # Initialize E2B sandbox
        try:
            self.e2b_client = e2b.Sandbox(
                timeout=60,  # 60 second timeout
                on_stderr=self._handle_stderr,
                on_stdout=self._handle_stdout,
            )
            logger.info("E2B sandbox initialized successfully")

            # Pre-install common packages in background
            asyncio.create_task(self._preinstall_common_packages())

        except Exception as e:
            logger.error(f"Error initializing E2B sandbox: {str(e)}")
            self.e2b_client = None

        # Track installed packages to avoid reinstalling
        self.installed_packages = {"python": set(), "npm": set()}

        # Track ongoing package installations
        self.ongoing_installations = {}

        # Graphiti client would be initialized here in a real implementation
        # self.graphiti_client = graphiti_core.Graphiti(...)

        logger.info("ToolExecutor initialized")

    async def _preinstall_common_packages(self):
        """Pre-install common packages in background to improve user experience"""
        try:
            logger.info("Starting pre-installation of common packages")

            # Only pre-install if enabled in settings
            if not settings.PREINSTALL_COMMON_PACKAGES:
                logger.info(
                    "Pre-installation of common packages is disabled in settings"
                )
                return

            # Pre-install Python packages
            python_packages_to_install = [
                f"{pkg}=={version}" for pkg, version in COMMON_PYTHON_PACKAGES.items()
            ]

            # Install in batches to avoid overwhelming the sandbox
            batch_size = 3
            for i in range(0, len(python_packages_to_install), batch_size):
                batch = python_packages_to_install[i : i + batch_size]
                try:
                    logger.info(f"Pre-installing Python packages batch: {batch}")
                    await self.e2b_client.install_python_packages(
                        batch,
                        timeout=300,  # 5 minutes timeout for pre-installation
                    )
                    # Add to installed packages
                    for pkg in batch:
                        pkg_name = pkg.split("==")[0]
                        self.installed_packages["python"].add(pkg_name)
                    logger.info(
                        f"Successfully pre-installed Python packages batch: {batch}"
                    )
                except Exception as e:
                    logger.warning(
                        f"Error pre-installing Python packages batch {batch}: {str(e)}"
                    )

            # Pre-install NPM packages
            npm_packages_to_install = [
                f"{pkg}@{version}" for pkg, version in COMMON_NPM_PACKAGES.items()
            ]

            for i in range(0, len(npm_packages_to_install), batch_size):
                batch = npm_packages_to_install[i : i + batch_size]
                try:
                    logger.info(f"Pre-installing NPM packages batch: {batch}")
                    await self.e2b_client.install_npm_packages(
                        batch,
                        timeout=300,  # 5 minutes timeout for pre-installation
                    )
                    # Add to installed packages
                    for pkg in batch:
                        pkg_name = pkg.split("@")[0]
                        self.installed_packages["npm"].add(pkg_name)
                    logger.info(
                        f"Successfully pre-installed NPM packages batch: {batch}"
                    )
                except Exception as e:
                    logger.warning(
                        f"Error pre-installing NPM packages batch {batch}: {str(e)}"
                    )

            logger.info("Completed pre-installation of common packages")

        except Exception as e:
            logger.error(f"Error during pre-installation of common packages: {str(e)}")

    def _handle_stdout(self, data: str):
        """Handle stdout streaming from E2B sandbox"""
        logger.debug(f"E2B stdout: {data}")

    def _handle_stderr(self, data: str):
        """Handle stderr streaming from E2B sandbox"""
        logger.debug(f"E2B stderr: {data}")

    async def execute_code(
        self, code: str, language: str, context: RequestContext
    ) -> Dict[str, Any]:
        """
        Execute code in E2B sandbox environment

        Args:
            code: Code to execute
            language: Programming language (python, javascript, etc.)
            context: Request context

        Returns:
            Dictionary containing execution results
        """
        logger.info(
            f"ToolExecutor.execute_code: Executing {language} code for thread_id={context.thread_id}"
        )

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
                "exit_code": result.exit_code,
            }

            # Log audit event
            audit_details = {
                "action": "execute_code",
                "language": language,
                "code_length": len(code),
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": True,
                "exit_code": result.exit_code,
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
                "error": str(e),
            }
            logger.info(f"AUDIT: {audit_details}")

            return {"success": False, "error": error_msg}

    async def write_file(
        self, file_path: str, content: str, context: RequestContext
    ) -> Dict[str, Any]:
        """
        Write content to a file in the sandbox

        Args:
            file_path: Path to the file
            content: Content to write
            context: Request context

        Returns:
            Dictionary indicating success or failure
        """
        logger.info(
            f"ToolExecutor.write_file: Writing to {file_path} for thread_id={context.thread_id}"
        )

        # Check if E2B client is initialized
        if not self.e2b_client:
            error_msg = "E2B sandbox is not initialized"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

        try:
            # Validate file path (security check)
            if ".." in file_path or file_path.startswith("/"):
                error_msg = (
                    "Invalid file path. Path cannot contain '..' or start with '/'"
                )
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
                "success": True,
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
                "error": str(e),
            }
            logger.info(f"AUDIT: {audit_details}")

            return {"success": False, "error": error_msg}

    async def read_file(
        self, file_path: str, context: RequestContext
    ) -> Dict[str, Any]:
        """
        Read content from a file in the sandbox

        Args:
            file_path: Path to the file
            context: Request context

        Returns:
            Dictionary containing file content or error
        """
        logger.info(
            f"ToolExecutor.read_file: Reading from {file_path} for thread_id={context.thread_id}"
        )

        # Check if E2B client is initialized
        if not self.e2b_client:
            error_msg = "E2B sandbox is not initialized"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

        try:
            # Validate file path (security check)
            if ".." in file_path or file_path.startswith("/"):
                error_msg = (
                    "Invalid file path. Path cannot contain '..' or start with '/'"
                )
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
                "success": True,
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
                "error": str(e),
            }
            logger.info(f"AUDIT: {audit_details}")

            return {"success": False, "error": error_msg}

    async def install_packages(
        self, packages: List[str], language: str, context: RequestContext
    ) -> Dict[str, Any]:
        """
        Install packages in the sandbox with improved handling for large packages

        Args:
            packages: List of packages to install
            language: Programming language (python, javascript, etc.)
            context: Request context

        Returns:
            Dictionary indicating success or failure
        """
        logger.info(
            f"ToolExecutor.install_packages: Installing {language} packages for thread_id={context.thread_id}"
        )

        # Check if E2B client is initialized
        if not self.e2b_client:
            error_msg = "E2B sandbox is not initialized"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

        # Generate a unique installation ID
        installation_id = f"{context.thread_id}_{language}_{','.join(packages)}"

        # Check if this exact installation is already in progress
        if installation_id in self.ongoing_installations:
            # Return the status of the ongoing installation
            status = self.ongoing_installations[installation_id]
            if status["completed"]:
                # Installation completed, remove from ongoing installations
                result = status["result"]
                del self.ongoing_installations[installation_id]
                return result
            else:
                # Installation still in progress
                return {
                    "success": True,
                    "status": "in_progress",
                    "progress": status.get("progress", 0),
                    "message": f"Installing packages: {', '.join(packages)}. This may take a few minutes.",
                } # Closing the dictionary returned on line 407

        # Start the actual installation logic wit{y block
        try:
            # Filter out already install}d and blocked packages
            language_key = (
                "python" if language.lower() == "python" else "npm"
            )  # Assuming only python/npm for now
            packages_to_install = []
            blocked_packages_str = settings.BLOCKED_PACKAGES  # Read from settings/env
            blocked_packages_set = (
                set(p.strip() for p in blocked_packages_str.split(",") if p.strip())
                if blocked_packages_str
                else set()
            )
            skipped_blocked = []

            for pkg in packages:
                # Extract base package name for checking
                pkg_name = (
                    pkg.split("==")[0]
                    if "==" in pkg
                    else pkg.split("@")[0] if "@" in pkg else pkg
                ).strip()

                if not pkg_name:  # Skip empty package names
                    continue

                # Check if blocked
                if pkg_name in blocked_packages_set:
                    logger.warning(
                        f"Attempt to install blocked package '{pkg_name}' skipped. "
                        f"Requested: '{pkg}'"
                    )
                    skipped_blocked.append(pkg_name)
                    continue  # Skip this package

                # Check if already installed
                if pkg_name in self.installed_packages.get(language_key, set()):
                    logger.info(f"Package {pkg_name} is already installed, skipping")
                else:
                    # Check for potentially problematic characters (basic sanitization)
                    # More robust validation might be needed depending on requirements
                    if not all(
                        c.isalnum() or c in ["-", "_", ".", "@", "="] for c in pkg
                    ):
                        logger.warning(
                            f"Skipping package with potentially unsafe characters: {pkg}"
                        )
                        continue
                    packages_to_install.append(pkg)

            # If all packages are already installed, return success immediately
            if not packages_to_install:
                completion_message = "All requested packages were already installed."
                if skipped_blocked:
                    completion_message += (
                        f" Skipped blocked packages: {', '.join(skipped_blocked)}."
                    )

                return {
                    "success": True,
                    "status": "completed",
                    "message": completion_message,
                    "stdout": "",
                    "stderr": "",
                    "skipped_blocked": skipped_blocked,
                }

            # Initialize ongoing installation status
            self.ongoing_installations[installation_id] = {
                "completed": False,
                "progress": 0,
                "result": None,
            }

            # Start installation in background task
            asyncio.create_task(
                self._install_packages_background(
                    packages_to_install, language, context, installation_id
                )
            )

            # Return immediate response
            return {
                "success": True,
                "status": "in_progress",
                "message": f"Starting installation for: {', '.join(packages_to_install)}. This may take a few minutes."
                + (
                    f" Skipped blocked: {', '.join(skipped_blocked)}."
                    if skipped_blocked
                    else ""
                ),
                "skipped_blocked": skipped_blocked,
            }
        # This except block corresponds to the try starting on line 415
        except Exception as e:
            error_msg = f"Error preparing package installation: {str(e)}"
            logger.error(error_msg, exc_info=True)
            # Log audit event for preparation error
            audit_details = {
                "action": "install_packages_prepare", # Different action name for clarity
                "language": language,
                "packages": packages,
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": False,
                "error": str(e),
            }
            logger.info(f"AUDIT: {audit_details}")
            # Clean up if installation was marked as ongoing
            if installation_id in self.ongoing_installations:
                 del self.ongoing_installations[installation_id]
            return {"success": False, "error": error_msg}
    # End of install_packages method (Correctly indented)

    async def _install_packages_background(
        self,
        packages: List[str],
        language: str,
        context: RequestContext,
        installation_id: str,
    ):
        """
        Background task to install packages with extended timeout

        Args:
            packages: List of packages to install
            language: Programming language
            context: Request context
            installation_id: Unique ID for this installation
        """
        try:
            # Update progress
            self.ongoing_installations[installation_id]["progress"] = 10

            # Determine if any large packages are being installed
            large_packages = []
            if language.lower() == "python":
                large_packages = [
                    pkg
                    for pkg in packages
                    if any(
                        lp in pkg
                        for lp in [
                            "tensorflow",
                            "torch",
                            "transformers",
                            "opencv",
                            "scipy",
                            "scikit-learn",
                            "pandas",
                        ]
                    )
                ]
            elif language.lower() in ["javascript", "typescript"]:
                large_packages = [
                    pkg
                    for pkg in packages
                    if any(
                        lp in pkg
                        for lp in [
                            "react",
                            "vue",
                            "angular",
                            "next",
                            "webpack",
                            "babel",
                        ]
                    )
                ]

            # Set timeout based on package size
            timeout = (
                600 if large_packages else 180
            )  # 10 minutes for large packages, 3 minutes for others

            # Update progress
            self.ongoing_installations[installation_id]["progress"] = 20

            # Install packages with extended timeout
            if language.lower() == "python":
                result = await self.e2b_client.install_python_packages(
                    packages, timeout=timeout
                )
                # Update installed packages
                for pkg in packages:
                    pkg_name = pkg.split("==")[0] if "==" in pkg else pkg
                    self.installed_packages["python"].add(pkg_name)
            elif language.lower() in ["javascript", "typescript"]:
                result = await self.e2b_client.install_npm_packages(
                    packages, timeout=timeout
                )
                # Update installed packages
                for pkg in packages:
                    pkg_name = pkg.split("@")[0] if "@" in pkg else pkg
                    self.installed_packages["npm"].add(pkg_name)
            else:
                raise ValueError(f"Package installation not supported for {language}")

            # Update progress
            self.ongoing_installations[installation_id]["progress"] = 90

            # Log audit event
            audit_details = {
                "action": "install_packages",
                "language": language,
                "packages": packages,
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": True,
            }
            logger.info(f"AUDIT: {audit_details}")

            # Update installation status
            self.ongoing_installations[installation_id].update(
                {
                    "completed": True,
                    "progress": 100,
                    "result": {
                        "success": True,
                        "status": "completed",
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                    },
                }
            )

        except Exception as e:
            error_msg = f"Error installing packages in background: {str(e)}"
            logger.error(error_msg)

            # Log audit event for error
            audit_details = {
                "action": "install_packages_background",
                "language": language,
                "packages": packages,
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": False,
                "error": str(e),
            }
            logger.info(f"AUDIT: {audit_details}")

            # Update installation status with error
            self.ongoing_installations[installation_id].update(
                {
                    "completed": True,
                    "progress": 100,
                    "result": {
                        "success": False,
                        "status": "failed",
                        "error": error_msg,
                    },
                }
            )

    async def get_package_installation_status(
        self, installation_id: str, context: RequestContext
    ) -> Dict[str, Any]:
        """
        Get the status of a package installation

        Args:
            installation_id: Unique ID for the installation
            context: Request context

        Returns:
            Dictionary containing installation status
        """
        if installation_id not in self.ongoing_installations:
            return {"success": False, "error": "Installation not found"}

        status = self.ongoing_installations[installation_id]

        if status["completed"]:
            # Installation completed, remove from ongoing installations
            result = status["result"]
            del self.ongoing_installations[installation_id]
            return result
        else:
            # Installation still in progress
            return {
                "success": True,
                "status": "in_progress",
                "progress": status.get("progress", 0),
            }

    async def add_graphiti_episode(
        self, episode_text: str, context: RequestContext, name: str = "interaction"
    ) -> bool:
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
            logger.info(
                f"ToolExecutor.add_graphiti_episode: Agent {context.agent_definition['agent_id']} does not use Graphiti, skipping"
            )
            return False

        logger.info(
            f"ToolExecutor.add_graphiti_episode: Adding episode for thread_id={context.thread_id}"
        )

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
                "success": True,
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
                "error": str(e),
            }
            logger.info(f"AUDIT: {audit_details}")

            return False

    async def search_graphiti(
        self, query: str, context: RequestContext
    ) -> List[Dict[str, Any]]:
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
            logger.info(
                f"ToolExecutor.search_graphiti: Agent {context.agent_definition['agent_id']} does not use Graphiti, skipping"
            )
            return []

        logger.info(
            f"ToolExecutor.search_graphiti: Searching with query '{query}' for thread_id={context.thread_id}"
        )

        try:
            # In a real implementation, we would:
            # 1. Call graphiti.search
            # 2. Log query/results/errors

            # For now, just return placeholder results
            results = [
                {
                    "type": "episode",
                    "id": "ep123",
                    "text": "This is a placeholder episode result",
                    "score": 0.95,
                },
                {
                    "type": "entity",
                    "id": "ent456",
                    "name": "Example Entity",
                    "score": 0.85,
                },
            ]

            # Log audit event
            audit_details = {
                "action": "search_graphiti",
                "query": query,
                "result_count": len(results),
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": True,
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
                "error": str(e),
            }
            logger.info(f"AUDIT: {audit_details}")

            return []

    async def call_specialized_model(
        self, model_name: str, prompt: str, context: RequestContext
    ) -> str:
        """
        Call a specialized model

        Args:
            model_name: Name of the model to call
            prompt: Prompt to send to the model
            context: Request context

        Returns:
            Model response as string
        """
        logger.info(
            f"ToolExecutor.call_specialized_model: Calling model '{model_name}' for thread_id={context.thread_id}"
        )

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
                "success": True,
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
                "error": str(e),
            }
            logger.info(f"AUDIT: {audit_details}")

            return error_msg

    async def retrieve_relevant_context(
        self, query: str, context: RequestContext
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from Qdrant

        Args:
            query: Search query
            context: Request context

        Returns:
            List of relevant text chunks
        """
        logger.info(
            f"ToolExecutor.retrieve_relevant_context: Retrieving context for query '{query}' for thread_id={context.thread_id}"
        )

        try:
            # In a real implementation, we would:
            # 1. Embed query using sentence-transformers
            # 2. Search Qdrant collection (filter by context.thread_id)
            # 3. Return top N text chunks

            # For now, just return placeholder results
            results = [
                {"text": "This is a placeholder RAG result 1", "score": 0.92},
                {"text": "This is a placeholder RAG result 2", "score": 0.85},
            ]

            # Log audit event
            audit_details = {
                "action": "retrieve_relevant_context",
                "query": query,
                "result_count": len(results),
                "thread_id": context.thread_id,
                "agent_id": context.agent_definition["agent_id"],
                "success": True,
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
                "error": str(e),
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
        # End of class ToolExecutor
