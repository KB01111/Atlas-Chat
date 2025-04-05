import os
import re
import json
import logging
import hashlib
import secrets
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

# Configure logging
logger = logging.getLogger(__name__)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/auth/token",
    scopes={
        "user": "Standard user access",
        "admin": "Administrator access",
        "execute_code": "Execute code in sandbox",
        "manage_teams": "Create and manage agent teams",
        "manage_artifacts": "Access and manage artifacts"
    }
)

# Security models
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []
    exp: Optional[datetime] = None


class SecurityAuditLog(BaseModel):
    timestamp: datetime
    user_id: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    ip_address: str
    user_agent: str
    status: str
    details: Optional[Dict[str, Any]] = None


# Security utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if the password matches the hash, False otherwise
    """
    # In a real implementation, use a proper password hashing library like passlib
    password_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    return password_hash == hashed_password


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    # In a real implementation, use a proper password hashing library like passlib
    return hashlib.sha256(password.encode()).hexdigest()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
        
    Returns:
        JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """
    Decode a JWT token.
    
    Args:
        token: JWT token
        
    Returns:
        TokenData object
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        token_scopes = payload.get("scopes", [])
        exp = datetime.fromtimestamp(payload.get("exp"))
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token_data = TokenData(username=username, scopes=token_scopes, exp=exp)
        return token_data
    
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current user from a JWT token.
    
    Args:
        security_scopes: Security scopes required for the endpoint
        token: JWT token
        db: Database session
        
    Returns:
        User object
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        token_data = decode_token(token)
        
        if token_data.exp < datetime.utcnow():
            raise credentials_exception
        
        user = db.query(User).filter(User.username == token_data.username).first()
        
        if user is None:
            raise credentials_exception
        
        # Check if the user has the required scopes
        for scope in security_scopes.scopes:
            if scope not in token_data.scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not enough permissions. Required scope: {scope}",
                    headers={"WWW-Authenticate": authenticate_value},
                )
        
        return user
    
    except (jwt.PyJWTError, ValidationError):
        raise credentials_exception


def get_current_active_user(
    current_user: User = Security(get_current_user, scopes=["user"])
) -> User:
    """
    Get the current active user.
    
    Args:
        current_user: Current user
        
    Returns:
        User object
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_admin_user(
    current_user: User = Security(get_current_user, scopes=["admin"])
) -> User:
    """
    Get the current admin user.
    
    Args:
        current_user: Current user
        
    Returns:
        User object
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required.",
        )
    return current_user


def get_user_with_code_execution_permission(
    current_user: User = Security(get_current_user, scopes=["user", "execute_code"])
) -> User:
    """
    Get the current user with code execution permission.
    
    Args:
        current_user: Current user
        
    Returns:
        User object
    """
    return current_user


def get_user_with_team_management_permission(
    current_user: User = Security(get_current_user, scopes=["user", "manage_teams"])
) -> User:
    """
    Get the current user with team management permission.
    
    Args:
        current_user: Current user
        
    Returns:
        User object
    """
    return current_user


def get_user_with_artifact_management_permission(
    current_user: User = Security(get_current_user, scopes=["user", "manage_artifacts"])
) -> User:
    """
    Get the current user with artifact management permission.
    
    Args:
        current_user: Current user
        
    Returns:
        User object
    """
    return current_user


# Code security functions
def sanitize_code(code: str) -> str:
    """
    Sanitize code to prevent security vulnerabilities.
    
    Args:
        code: Code to sanitize
        
    Returns:
        Sanitized code
    """
    # Remove potentially dangerous imports
    dangerous_imports = [
        r"import\s+os\s*;",
        r"import\s+subprocess\s*;",
        r"import\s+sys\s*;",
        r"import\s+shutil\s*;",
        r"from\s+os\s+import\s+.*",
        r"from\s+subprocess\s+import\s+.*",
        r"from\s+sys\s+import\s+.*",
        r"from\s+shutil\s+import\s+.*",
        r"__import__\s*\(\s*['\"]os['\"].*\)",
        r"__import__\s*\(\s*['\"]subprocess['\"].*\)",
        r"__import__\s*\(\s*['\"]sys['\"].*\)",
        r"__import__\s*\(\s*['\"]shutil['\"].*\)",
    ]
    
    for pattern in dangerous_imports:
        code = re.sub(pattern, "# Removed for security reasons", code, flags=re.IGNORECASE)
    
    # Remove potentially dangerous functions
    dangerous_functions = [
        r"eval\s*\(",
        r"exec\s*\(",
        r"execfile\s*\(",
        r"compile\s*\(",
        r"open\s*\(",
        r"file\s*\(",
        r"os\.system\s*\(",
        r"os\.popen\s*\(",
        r"os\.spawn\w*\s*\(",
        r"os\.exec\w*\s*\(",
        r"subprocess\.Popen\s*\(",
        r"subprocess\.call\s*\(",
        r"subprocess\.run\s*\(",
        r"subprocess\.check_output\s*\(",
        r"subprocess\.check_call\s*\(",
        r"subprocess\.getoutput\s*\(",
        r"subprocess\.getstatusoutput\s*\(",
        r"subprocess\.CalledProcessError\s*\(",
        r"subprocess\.PIPE\s*",
        r"subprocess\.STDOUT\s*",
        r"subprocess\.DEVNULL\s*",
        r"sys\.exit\s*\(",
        r"sys\.argv",
        r"sys\.path",
        r"sys\.modules",
        r"sys\.meta_path",
        r"sys\.path_hooks",
        r"sys\.path_importer_cache",
        r"sys\.path_hooks_cache",
        r"sys\.builtin_module_names",
        r"sys\.modules",
        r"sys\.flags",
        r"sys\.getframe\s*\(",
        r"sys\.exc_info\s*\(",
        r"sys\.excepthook\s*\(",
        r"sys\.settrace\s*\(",
        r"sys\.setprofile\s*\(",
        r"sys\.setrecursionlimit\s*\(",
        r"sys\.setswitchinterval\s*\(",
        r"sys\.setcheckinterval\s*\(",
        r"sys\.setdlopenflags\s*\(",
        r"sys\.setaudiothreads\s*\(",
        r"sys\.settscdump\s*\(",
        r"sys\.setrecursionlimit\s*\(",
        r"sys\.setaudiothreads\s*\(",
        r"sys\.setdlopenflags\s*\(",
        r"sys\.setcheckinterval\s*\(",
        r"sys\.setswitchinterval\s*\(",
        r"sys\.setprofile\s*\(",
        r"sys\.settrace\s*\(",
        r"sys\.settscdump\s*\(",
        r"sys\.excepthook\s*\(",
        r"sys\.exc_info\s*\(",
        r"sys\.getframe\s*\(",
        r"sys\.flags",
        r"sys\.modules",
        r"sys\.builtin_module_names",
        r"sys\.path_hooks_cache",
        r"sys\.path_importer_cache",
        r"sys\.path_hooks",
        r"sys\.meta_path",
        r"sys\.modules",
        r"sys\.path",
        r"sys\.argv",
        r"shutil\.rmtree\s*\(",
        r"shutil\.move\s*\(",
        r"shutil\.copy\s*\(",
        r"shutil\.copy2\s*\(",
        r"shutil\.copyfile\s*\(",
        r"shutil\.copyfileobj\s*\(",
        r"shutil\.copytree\s*\(",
        r"shutil\.make_archive\s*\(",
        r"shutil\.get_archive_formats\s*\(",
        r"shutil\.get_unpack_formats\s*\(",
        r"shutil\.register_archive_format\s*\(",
        r"shutil\.register_unpack_format\s*\(",
        r"shutil\.unpack_archive\s*\(",
        r"shutil\.unregister_archive_format\s*\(",
        r"shutil\.unregister_unpack_format\s*\(",
        r"shutil\.which\s*\(",
        r"shutil\.disk_usage\s*\(",
        r"shutil\.chown\s*\(",
        r"shutil\.get_terminal_size\s*\(",
    ]
    
    for pattern in dangerous_functions:
        code = re.sub(pattern, "# Removed for security reasons(", code, flags=re.IGNORECASE)
    
    return code


def validate_code_security(code: str) -> Dict[str, Any]:
    """
    Validate code security.
    
    Args:
        code: Code to validate
        
    Returns:
        Validation result
    """
    # Check for potentially dangerous patterns
    dangerous_patterns = [
        (r"import\s+os", "Importing os module is not allowed"),
        (r"import\s+subprocess", "Importing subprocess module is not allowed"),
        (r"import\s+sys", "Importing sys module is not allowed"),
        (r"import\s+shutil", "Importing shutil module is not allowed"),
        (r"from\s+os\s+import", "Importing from os module is not allowed"),
        (r"from\s+subprocess\s+import", "Importing from subprocess module is not allowed"),
        (r"from\s+sys\s+import", "Importing from sys module is not allowed"),
        (r"from\s+shutil\s+import", "Importing from shutil module is not allowed"),
        (r"__import__\s*\(\s*['\"]os['\"]", "Importing os module using __import__ is not allowed"),
        (r"__import__\s*\(\s*['\"]subprocess['\"]", "Importing subprocess module using __import__ is not allowed"),
        (r"__import__\s*\(\s*['\"]sys['\"]", "Importing sys module using __import__ is not allowed"),
        (r"__import__\s*\(\s*['\"]shutil['\"]", "Importing shutil module using __import__ is not allowed"),
        (r"eval\s*\(", "Using eval() is not allowed"),
        (r"exec\s*\(", "Using exec() is not allowed"),
        (r"execfile\s*\(", "Using execfile() is not allowed"),
        (r"compile\s*\(", "Using compile() is not allowed"),
        (r"open\s*\(", "Using open() is not allowed"),
        (r"file\s*\(", "Using file() is not allowed"),
        (r"os\.system\s*\(", "Using os.system() is not allowed"),
        (r"os\.popen\s*\(", "Using os.popen() is not allowed"),
        (r"os\.spawn\w*\s*\(", "Using os.spawn*() is not allowed"),
        (r"os\.exec\w*\s*\(", "Using os.exec*() is not allowed"),
        (r"subprocess\.Popen\s*\(", "Using subprocess.Popen() is not allowed"),
        (r"subprocess\.call\s*\(", "Using subprocess.call() is not allowed"),
        (r"subprocess\.run\s*\(", "Using subprocess.run() is not allowed"),
        (r"subprocess\.check_output\s*\(", "Using subprocess.check_output() is not allowed"),
        (r"subprocess\.check_call\s*\(", "Using subprocess.check_call() is not allowed"),
        (r"subprocess\.getoutput\s*\(", "Using subprocess.getoutput() is not allowed"),
        (r"subprocess\.getstatusoutput\s*\(", "Using subprocess.getstatusoutput() is not allowed"),
        (r"sys\.exit\s*\(", "Using sys.exit() is not allowed"),
        (r"shutil\.rmtree\s*\(", "Using shutil.rmtree() is not allowed"),
    ]
    
    issues = []
    for pattern, message in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append(message)
    
    # Check for resource usage
    if len(code) > 100000:
        issues.append("Code is too large (> 100KB)")
    
    # Check for infinite loops
    if re.search(r"while\s+True", code, re.IGNORECASE):
        issues.append("Potential infinite loop detected (while True)")
    
    # Check for network access
    if re.search(r"import\s+socket", code, re.IGNORECASE) or re.search(r"import\s+requests", code, re.IGNORECASE):
        issues.append("Network access is not allowed")
    
    return {
        "is_safe": len(issues) == 0,
        "issues": issues
    }


def log_security_event(
    db: Session,
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    ip_address: str = "0.0.0.0",
    user_agent: str = "Unknown",
    status: str = "success",
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log a security event.
    
    Args:
        db: Database session
        user_id: User ID
        action: Action performed
        resource_type: Type of resource
        resource_id: ID of the resource
        ip_address: IP address of the user
        user_agent: User agent of the user
        status: Status of the action
        details: Additional details
    """
    log_entry = SecurityAuditLog(
        timestamp=datetime.utcnow(),
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status,
        details=details
    )
    
    # In a real implementation, save to database
    logger.info(f"Security event: {json.dumps(log_entry.dict(), default=str)}")


def generate_secure_random_string(length: int = 32) -> str:
    """
    Generate a secure random string.
    
    Args:
        length: Length of the string
        
    Returns:
        Secure random string
    """
    return secrets.token_hex(length // 2)


def rate_limit_check(
    user_id: str,
    action: str,
    max_requests: int = 100,
    time_window: int = 3600
) -> bool:
    """
    Check if a user has exceeded the rate limit for an action.
    
    Args:
        user_id: User ID
        action: Action to check
        max_requests: Maximum number of requests allowed
        time_window: Time window in seconds
        
    Returns:
        True if the user has not exceeded the rate limit, False otherwise
    """
    # In a real implementation, use Redis or a similar cache to track rate limits
    # For now, always return True
    return True
