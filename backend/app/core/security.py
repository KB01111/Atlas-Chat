from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional

from app.core.config import settings

# Security scheme for JWT authentication
security = HTTPBearer()

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time
        
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict:
    """
    Validate JWT token and return user information
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        User information from token
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        # Check if token has expired
        if datetime.fromtimestamp(payload.get("exp")) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token has expired")
        
        # Extract user information
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {"user_id": user_id}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def validate_code_execution_request(code: str, language: str) -> None:
    """
    Validate code execution request for security
    
    Args:
        code: Code to execute
        language: Programming language
        
    Raises:
        HTTPException: If request is invalid or potentially malicious
    """
    # Check for empty code
    if not code or not code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    
    # Check for supported languages
    supported_languages = ["python", "javascript", "typescript", "bash"]
    if language.lower() not in supported_languages:
        raise HTTPException(
            status_code=400, 
            detail=f"Language {language} not supported. Supported languages: {', '.join(supported_languages)}"
        )
    
    # Basic security checks for potentially dangerous operations
    dangerous_patterns = {
        "python": [
            "import os; os.system", 
            "subprocess.call", 
            "subprocess.Popen",
            "__import__('os').system",
            "eval(input",
            "exec(input"
        ],
        "javascript": [
            "process.env",
            "require('child_process')",
            "exec(",
            "spawn("
        ],
        "typescript": [
            "process.env",
            "require('child_process')",
            "exec(",
            "spawn("
        ],
        "bash": [
            "rm -rf /",
            "> /dev/sda",
            "mkfs",
            ":(){:|:&};:"  # Fork bomb
        ]
    }
    
    # Check for dangerous patterns based on language
    for pattern in dangerous_patterns.get(language.lower(), []):
        if pattern in code:
            raise HTTPException(
                status_code=400, 
                detail=f"Potentially dangerous code pattern detected: {pattern}"
            )

def validate_file_path(file_path: str) -> None:
    """
    Validate file path for security
    
    Args:
        file_path: Path to validate
        
    Raises:
        HTTPException: If path is invalid or potentially malicious
    """
    # Check for empty path
    if not file_path or not file_path.strip():
        raise HTTPException(status_code=400, detail="File path cannot be empty")
    
    # Check for path traversal attempts
    if ".." in file_path or file_path.startswith("/"):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file path. Path cannot contain '..' or start with '/'"
        )
    
    # Check for suspicious file extensions
    suspicious_extensions = [".sh", ".exe", ".bat", ".cmd", ".com", ".vbs", ".ps1"]
    for ext in suspicious_extensions:
        if file_path.endswith(ext):
            raise HTTPException(
                status_code=400, 
                detail=f"Suspicious file extension: {ext}"
            )

def validate_package_names(packages: list) -> None:
    """
    Validate package names for security
    
    Args:
        packages: List of package names
        
    Raises:
        HTTPException: If package names are invalid or potentially malicious
    """
    # Check for empty package list
    if not packages:
        raise HTTPException(status_code=400, detail="Package list cannot be empty")
    
    # Check for suspicious package names
    suspicious_packages = ["cryptography", "pycrypto", "paramiko", "fabric", "pyinstaller"]
    for package in packages:
        if package.strip() in suspicious_packages:
            raise HTTPException(
                status_code=400, 
                detail=f"Suspicious package name: {package}"
            )
    
    # Check for shell command injection
    for package in packages:
        if ";" in package or "&" in package or "|" in package or ">" in package or "<" in package:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid package name: {package}"
            )
