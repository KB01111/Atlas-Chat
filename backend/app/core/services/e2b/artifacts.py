import base64
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .session import E2BSession

logger = logging.getLogger(__name__)


class Artifact:
    """
    Represents an artifact generated during code execution.
    """

    def __init__(
        self,
        artifact_id: str,
        name: str,
        content_type: str,
        content: Union[bytes, str],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize an artifact.

        Args:
            artifact_id: Unique identifier for the artifact
            name: Name of the artifact
            content_type: MIME type of the artifact
            content: Content of the artifact
            metadata: Additional metadata for the artifact
        """
        self.id = artifact_id
        self.name = name
        self.content_type = content_type
        self.content = (
            content if isinstance(content, bytes) else content.encode("utf-8")
        )
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the artifact to a dictionary.

        Returns:
            Dictionary representation of the artifact
        """
        return {
            "id": self.id,
            "name": self.name,
            "content_type": self.content_type,
            "content_base64": base64.b64encode(self.content).decode("utf-8"),
            "metadata": self.metadata,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Artifact":
        """
        Create an artifact from a dictionary.

        Args:
            data: Dictionary representation of the artifact

        Returns:
            Artifact object
        """
        content = base64.b64decode(data["content_base64"])
        return cls(
            artifact_id=data["id"],
            name=data["name"],
            content_type=data["content_type"],
            content=content,
            metadata=data.get("metadata", {}),
        )


class ArtifactManager:
    """
    Manager for artifacts generated during code execution.
    """

    def __init__(self, session: E2BSession, artifacts_dir: str = "./artifacts"):
        """
        Initialize the artifact manager.

        Args:
            session: The E2B session
            artifacts_dir: Directory to store artifacts in the E2B sandbox
        """
        self.session = session
        self.artifacts_dir = artifacts_dir
        self.artifacts: Dict[str, Artifact] = {}

    async def initialize(self):
        """
        Initialize the artifact manager by creating the artifacts directory.
        """
        # Create the artifacts directory if it doesn't exist
        process = await self.session.process.start(
            {"cmd": ["mkdir", "-p", self.artifacts_dir]}
        )
        result = await process.wait()
        if result.exit_code != 0:
            logger.error(f"Failed to create artifacts directory: {result.stderr}")
            raise RuntimeError(f"Failed to create artifacts directory: {result.stderr}")

    async def create_artifact_from_file(
        self,
        file_path: str,
        name: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Artifact:
        """
        Create an artifact from a file in the E2B sandbox.

        Args:
            file_path: Path to the file in the E2B sandbox
            name: Name of the artifact (defaults to the file name)
            content_type: MIME type of the artifact (auto-detected if not provided)
            metadata: Additional metadata for the artifact

        Returns:
            Artifact object
        """
        # Read the file content
        content = await self.session.filesystem.read_file(file_path)

        # Determine the name if not provided
        if name is None:
            name = os.path.basename(file_path)

        # Auto-detect content type if not provided
        if content_type is None:
            content_type = self._detect_content_type(file_path)

        # Create the artifact
        artifact_id = str(uuid.uuid4())
        artifact = Artifact(
            artifact_id=artifact_id,
            name=name,
            content_type=content_type,
            content=content,
            metadata=metadata,
        )

        # Store the artifact
        self.artifacts[artifact_id] = artifact

        return artifact

    async def create_artifact(
        self,
        content: Union[bytes, str],
        name: str,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Artifact:
        """
        Create an artifact with the provided content.

        Args:
            content: Content of the artifact
            name: Name of the artifact
            content_type: MIME type of the artifact
            metadata: Additional metadata for the artifact

        Returns:
            Artifact object
        """
        # Create the artifact
        artifact_id = str(uuid.uuid4())
        artifact = Artifact(
            artifact_id=artifact_id,
            name=name,
            content_type=content_type,
            content=content,
            metadata=metadata,
        )

        # Store the artifact
        self.artifacts[artifact_id] = artifact

        # Write the artifact to the E2B sandbox
        artifact_path = f"{self.artifacts_dir}/{name}"
        await self.session.filesystem.write_file(artifact_path, artifact.content)

        return artifact

    async def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        """
        Get an artifact by ID.

        Args:
            artifact_id: ID of the artifact

        Returns:
            Artifact object or None if not found
        """
        return self.artifacts.get(artifact_id)

    async def list_artifacts(self) -> List[Artifact]:
        """
        List all artifacts.

        Returns:
            List of artifacts
        """
        return list(self.artifacts.values())

    async def delete_artifact(self, artifact_id: str) -> bool:
        """
        Delete an artifact.

        Args:
            artifact_id: ID of the artifact

        Returns:
            True if the artifact was deleted, False otherwise
        """
        if artifact_id in self.artifacts:
            artifact = self.artifacts[artifact_id]
            artifact_path = f"{self.artifacts_dir}/{artifact.name}"

            # Delete the artifact file from the E2B sandbox
            process = await self.session.process.start(
                {"cmd": ["rm", "-f", artifact_path]}
            )
            result = await process.wait()
            if result.exit_code != 0:
                logger.warning(f"Failed to delete artifact file: {result.stderr}")

            # Remove the artifact from the manager
            del self.artifacts[artifact_id]
            return True

        return False

    async def scan_for_artifacts(self, pattern: str = "*") -> List[Artifact]:
        """
        Scan the artifacts directory for files matching the pattern and create artifacts.

        Args:
            pattern: Glob pattern to match files

        Returns:
            List of created artifacts
        """
        # Find files matching the pattern
        matching_files = await self.session.filesystem.glob(
            f"{self.artifacts_dir}/{pattern}"
        )

        # Create artifacts for each file
        created_artifacts = []
        for file_path in matching_files:
            artifact = await self.create_artifact_from_file(file_path)
            created_artifacts.append(artifact)

        return created_artifacts

    def _detect_content_type(self, file_path: str) -> str:
        """
        Detect the MIME type of a file based on its extension.

        Args:
            file_path: Path to the file

        Returns:
            MIME type
        """
        extension = os.path.splitext(file_path)[1].lower()

        # Map common extensions to MIME types
        mime_types = {
            ".txt": "text/plain",
            ".html": "text/html",
            ".htm": "text/html",
            ".css": "text/css",
            ".js": "application/javascript",
            ".json": "application/json",
            ".xml": "application/xml",
            ".csv": "text/csv",
            ".md": "text/markdown",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".pdf": "application/pdf",
            ".zip": "application/zip",
            ".tar": "application/x-tar",
            ".gz": "application/gzip",
            ".mp3": "audio/mpeg",
            ".mp4": "video/mp4",
            ".wav": "audio/wav",
            ".py": "text/x-python",
            ".java": "text/x-java",
            ".c": "text/x-c",
            ".cpp": "text/x-c++",
            ".h": "text/x-c",
            ".hpp": "text/x-c++",
            ".rb": "text/x-ruby",
            ".go": "text/x-go",
            ".rs": "text/x-rust",
            ".ts": "text/x-typescript",
            ".jsx": "text/x-jsx",
            ".tsx": "text/x-tsx",
        }

        return mime_types.get(extension, "application/octet-stream")
