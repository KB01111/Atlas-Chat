from typing import Dict, List, Optional, Any, Union
import asyncio
import time
import base64
import logging
import os
import json
from e2b import Session, Filesystem, Process as E2BProcess
from e2b.api.process import ProcessOpts, ProcessOutput

logger = logging.getLogger(__name__)

class E2BSession:
    """
    Wrapper for E2B SDK session to interact with the E2B sandbox environment.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the E2B session.
        
        Args:
            api_key: The E2B API key
        """
        self.id = f"session_{int(time.time())}"
        self.api_key = api_key or os.environ.get("E2B_API_KEY")
        
        # Initialize the actual E2B SDK session
        self.session = Session(
            id=self.id,
            api_key=self.api_key,
            template="base"  # Use the base template for general purpose tasks
        )
        
        self.process = ProcessManager(self)
        self.filesystem = FileSystemManager(self)
        logger.info(f"Initialized E2B session: {self.id}")
    
    async def close(self):
        """
        Close the E2B session and clean up resources.
        """
        logger.info(f"Closing E2B session: {self.id}")
        try:
            await self.session.close()
            logger.info(f"Successfully closed E2B session: {self.id}")
        except Exception as e:
            logger.error(f"Error closing E2B session {self.id}: {str(e)}")
            raise


class ProcessManager:
    """
    Manager for processes in the E2B sandbox.
    """
    
    def __init__(self, session: E2BSession):
        """
        Initialize the process manager.
        
        Args:
            session: The E2B session
        """
        self.session = session
    
    async def start(self, options: Dict[str, Any]) -> "Process":
        """
        Start a process in the E2B sandbox.
        
        Args:
            options: Process options including command and environment variables
            
        Returns:
            Process object
        """
        cmd = options.get("cmd", [])
        env = options.get("env", {})
        cwd = options.get("cwd", "/")
        
        logger.info(f"Starting process with command: {cmd}")
        
        try:
            process_opts = ProcessOpts(
                cmd=cmd,
                env=env,
                cwd=cwd
            )
            
            e2b_process = await self.session.session.process.start(process_opts)
            return Process(self.session, options, e2b_process)
        except Exception as e:
            logger.error(f"Error starting process: {str(e)}")
            raise
    
    async def list(self) -> List[Dict[str, Any]]:
        """
        List all running processes in the E2B sandbox.
        
        Returns:
            List of process information
        """
        try:
            processes = await self.session.session.process.list()
            return [
                {
                    "pid": process.pid,
                    "cmd": process.cmd,
                    "status": process.status
                }
                for process in processes
            ]
        except Exception as e:
            logger.error(f"Error listing processes: {str(e)}")
            return []


class Process:
    """
    Represents a process running in the E2B sandbox.
    """
    
    def __init__(self, session: E2BSession, options: Dict[str, Any], e2b_process: E2BProcess):
        """
        Initialize the process.
        
        Args:
            session: The E2B session
            options: Process options
            e2b_process: The actual E2B process object
        """
        self.session = session
        self.options = options
        self.e2b_process = e2b_process
        self.stdin = StdinStream(self)
        self.stdout = ""
        self.stderr = ""
    
    async def wait(self) -> "ProcessResult":
        """
        Wait for the process to complete.
        
        Returns:
            Process result
        """
        try:
            # Wait for the process to complete and get the output
            output: ProcessOutput = await self.e2b_process.wait()
            
            # Store the output
            self.stdout = output.stdout
            self.stderr = output.stderr
            
            return ProcessResult(
                output.exit_code,
                output.stdout,
                output.stderr
            )
        except Exception as e:
            logger.error(f"Error waiting for process: {str(e)}")
            return ProcessResult(1, "", str(e))
    
    async def kill(self):
        """
        Kill the process.
        """
        logger.info(f"Killing process in session: {self.session.id}")
        try:
            await self.e2b_process.kill()
            logger.info(f"Successfully killed process in session: {self.session.id}")
        except Exception as e:
            logger.error(f"Error killing process: {str(e)}")
            raise


class StdinStream:
    """
    Stream for writing to process standard input.
    """
    
    def __init__(self, process: Process):
        """
        Initialize the stdin stream.
        
        Args:
            process: The process
        """
        self.process = process
        self.buffer = ""
    
    async def write(self, data: str):
        """
        Write data to the process standard input.
        
        Args:
            data: The data to write
        """
        self.buffer += data
        try:
            await self.process.e2b_process.stdin.write(data)
        except Exception as e:
            logger.error(f"Error writing to stdin: {str(e)}")
            raise
    
    async def end(self):
        """
        End the standard input stream.
        """
        logger.info(f"Ending stdin stream for process in session: {self.process.session.id}")
        try:
            await self.process.e2b_process.stdin.end()
            logger.info(f"Successfully ended stdin stream for process in session: {self.process.session.id}")
        except Exception as e:
            logger.error(f"Error ending stdin stream: {str(e)}")
            raise


class ProcessResult:
    """
    Result of a process execution.
    """
    
    def __init__(self, exit_code: int, stdout: str, stderr: str):
        """
        Initialize the process result.
        
        Args:
            exit_code: The process exit code
            stdout: The process standard output
            stderr: The process standard error
        """
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


class FileSystemManager:
    """
    Manager for file system operations in the E2B sandbox.
    """
    
    def __init__(self, session: E2BSession):
        """
        Initialize the file system manager.
        
        Args:
            session: The E2B session
        """
        self.session = session
        self.fs: Filesystem = self.session.session.filesystem
    
    async def list(self, path: str) -> List[Dict[str, Any]]:
        """
        List files and directories in the specified path.
        
        Args:
            path: The path to list
            
        Returns:
            List of file and directory information
        """
        try:
            entries = await self.fs.list(path)
            return [
                {
                    "name": entry.name,
                    "type": "directory" if entry.is_dir else "file",
                    "size": entry.size if not entry.is_dir else 0,
                    "modified": entry.modified_at.isoformat() if entry.modified_at else None
                }
                for entry in entries
            ]
        except Exception as e:
            logger.error(f"Error listing files in {path}: {str(e)}")
            return []
    
    async def read_file(self, path: str) -> bytes:
        """
        Read a file from the E2B sandbox.
        
        Args:
            path: The path to the file
            
        Returns:
            File content as bytes
        """
        try:
            content = await self.fs.read_file(path)
            return content
        except Exception as e:
            logger.error(f"Error reading file {path}: {str(e)}")
            raise
    
    async def write_file(self, path: str, content: Union[bytes, str]) -> bool:
        """
        Write a file to the E2B sandbox.
        
        Args:
            path: The path to the file
            content: The file content
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert string to bytes if necessary
            if isinstance(content, str):
                content = content.encode('utf-8')
                
            logger.info(f"Writing file: {path} ({len(content)} bytes)")
            await self.fs.write_file(path, content)
            return True
        except Exception as e:
            logger.error(f"Error writing file {path}: {str(e)}")
            return False
    
    async def mkdir(self, path: str) -> bool:
        """
        Create a directory in the E2B sandbox.
        
        Args:
            path: The path to create
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.fs.mkdir(path)
            return True
        except Exception as e:
            logger.error(f"Error creating directory {path}: {str(e)}")
            return False
    
    async def remove(self, path: str) -> bool:
        """
        Remove a file or directory from the E2B sandbox.
        
        Args:
            path: The path to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.fs.remove(path)
            return True
        except Exception as e:
            logger.error(f"Error removing {path}: {str(e)}")
            return False
    
    async def glob(self, pattern: str) -> List[str]:
        """
        Find files matching the specified pattern.
        
        Args:
            pattern: The glob pattern
            
        Returns:
            List of matching file paths
        """
        try:
            matches = await self.fs.glob(pattern)
            return matches
        except Exception as e:
            logger.error(f"Error globbing {pattern}: {str(e)}")
            return []
