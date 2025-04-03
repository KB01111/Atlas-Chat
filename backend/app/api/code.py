from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.core.services.tool_executor import ToolExecutor
from app.models.models import RequestContext
from app.core.auth import get_current_user

# Create a dependency to get the ToolExecutor instance
def get_tool_executor():
    executor = ToolExecutor()
    try:
        yield executor
    finally:
        executor.close()

# Define request models
class CodeExecutionRequest(BaseModel):
    code: str
    language: str
    thread_id: str
    agent_id: str

class FileOperationRequest(BaseModel):
    file_path: str
    content: Optional[str] = None
    thread_id: str
    agent_id: str

class PackageInstallRequest(BaseModel):
    packages: List[str]
    language: str
    thread_id: str
    agent_id: str

# Create router
router = APIRouter(prefix="/code", tags=["code"])

@router.post("/execute")
async def execute_code(
    request: CodeExecutionRequest,
    tool_executor: ToolExecutor = Depends(get_tool_executor),
    user: dict = Depends(get_current_user)
):
    """
    Execute code in the E2B sandbox
    """
    # Create request context
    context = RequestContext(
        thread_id=request.thread_id,
        user_id=user["user_id"],
        agent_definition={"agent_id": request.agent_id}
    )
    
    # Execute code
    result = await tool_executor.execute_code(
        code=request.code,
        language=request.language,
        context=context
    )
    
    return result

@router.post("/write-file")
async def write_file(
    request: FileOperationRequest,
    tool_executor: ToolExecutor = Depends(get_tool_executor),
    user: dict = Depends(get_current_user)
):
    """
    Write content to a file in the E2B sandbox
    """
    if not request.content:
        raise HTTPException(status_code=400, detail="Content is required")
    
    # Create request context
    context = RequestContext(
        thread_id=request.thread_id,
        user_id=user["user_id"],
        agent_definition={"agent_id": request.agent_id}
    )
    
    # Write file
    result = await tool_executor.write_file(
        file_path=request.file_path,
        content=request.content,
        context=context
    )
    
    return result

@router.post("/read-file")
async def read_file(
    request: FileOperationRequest,
    tool_executor: ToolExecutor = Depends(get_tool_executor),
    user: dict = Depends(get_current_user)
):
    """
    Read content from a file in the E2B sandbox
    """
    # Create request context
    context = RequestContext(
        thread_id=request.thread_id,
        user_id=user["user_id"],
        agent_definition={"agent_id": request.agent_id}
    )
    
    # Read file
    result = await tool_executor.read_file(
        file_path=request.file_path,
        context=context
    )
    
    return result

@router.post("/install-packages")
async def install_packages(
    request: PackageInstallRequest,
    tool_executor: ToolExecutor = Depends(get_tool_executor),
    user: dict = Depends(get_current_user)
):
    """
    Install packages in the E2B sandbox
    """
    # Create request context
    context = RequestContext(
        thread_id=request.thread_id,
        user_id=user["user_id"],
        agent_definition={"agent_id": request.agent_id}
    )
    
    # Install packages
    result = await tool_executor.install_packages(
        packages=request.packages,
        language=request.language,
        context=context
    )
    
    return result
