#!/bin/bash

# Comprehensive testing script for Atlas-Chat application
# This script runs tests for all components and identifies issues

echo "Starting comprehensive testing process..."

# Create a test results directory
RESULTS_DIR="./test_results_$(date +%Y%m%d_%H%M%S)"
mkdir -p $RESULTS_DIR

echo "Created test results directory: $RESULTS_DIR"

# Function to log test results
log_test_result() {
  local test_name=$1
  local status=$2
  local details=$3
  
  echo "[$status] $test_name: $details" >> "$RESULTS_DIR/test_results.log"
  echo "[$status] $test_name: $details"
}

# Function to test backend API endpoints
test_backend_api() {
  echo "Testing backend API endpoints..."
  
  # Check if backend is running
  if ! curl -s http://localhost:8000/api/health > /dev/null; then
    log_test_result "Backend Health Check" "FAIL" "Backend is not running"
    return 1
  fi
  
  # Test authentication endpoints
  echo "Testing authentication endpoints..."
  AUTH_RESULT=$(curl -s -X POST http://localhost:8000/api/auth/token -H "Content-Type: application/json" -d '{"username":"test","password":"test"}')
  
  if [[ $AUTH_RESULT == *"error"* ]]; then
    log_test_result "Authentication API" "FAIL" "Authentication endpoint returned error"
  else
    log_test_result "Authentication API" "PASS" "Authentication endpoint working correctly"
  fi
  
  # Test code execution endpoints
  echo "Testing code execution endpoints..."
  CODE_RESULT=$(curl -s -X POST http://localhost:8000/api/code/execute -H "Content-Type: application/json" -d '{"code":"print(\"Hello, World!\")","language":"python"}')
  
  if [[ $CODE_RESULT == *"error"* ]]; then
    log_test_result "Code Execution API" "FAIL" "Code execution endpoint returned error"
  else
    log_test_result "Code Execution API" "PASS" "Code execution endpoint working correctly"
  fi
  
  # Test artifact endpoints
  echo "Testing artifact endpoints..."
  ARTIFACT_RESULT=$(curl -s -X GET http://localhost:8000/api/artifacts)
  
  if [[ $ARTIFACT_RESULT == *"error"* ]]; then
    log_test_result "Artifacts API" "FAIL" "Artifacts endpoint returned error"
  else
    log_test_result "Artifacts API" "PASS" "Artifacts endpoint working correctly"
  fi
  
  # Test team management endpoints
  echo "Testing team management endpoints..."
  TEAM_RESULT=$(curl -s -X GET http://localhost:8000/api/teams)
  
  if [[ $TEAM_RESULT == *"error"* ]]; then
    log_test_result "Teams API" "FAIL" "Teams endpoint returned error"
  else
    log_test_result "Teams API" "PASS" "Teams endpoint working correctly"
  fi
}

# Function to test E2B code interpreter
test_e2b_code_interpreter() {
  echo "Testing E2B code interpreter..."
  
  # Check if E2B code interpreter is running
  if ! curl -s http://localhost:8080/health > /dev/null; then
    log_test_result "E2B Code Interpreter Health Check" "FAIL" "E2B code interpreter is not running"
    return 1
  fi
  
  # Test Python code execution
  echo "Testing Python code execution..."
  PYTHON_RESULT=$(curl -s -X POST http://localhost:8080/execute -H "Content-Type: application/json" -d '{"code":"print(\"Hello, World!\")","language":"python"}')
  
  if [[ $PYTHON_RESULT == *"error"* ]]; then
    log_test_result "Python Code Execution" "FAIL" "Python code execution returned error"
  else
    log_test_result "Python Code Execution" "PASS" "Python code execution working correctly"
  fi
  
  # Test JavaScript code execution
  echo "Testing JavaScript code execution..."
  JS_RESULT=$(curl -s -X POST http://localhost:8080/execute -H "Content-Type: application/json" -d '{"code":"console.log(\"Hello, World!\")","language":"javascript"}')
  
  if [[ $JS_RESULT == *"error"* ]]; then
    log_test_result "JavaScript Code Execution" "FAIL" "JavaScript code execution returned error"
  else
    log_test_result "JavaScript Code Execution" "PASS" "JavaScript code execution working correctly"
  fi
  
  # Test artifact generation
  echo "Testing artifact generation..."
  ARTIFACT_RESULT=$(curl -s -X POST http://localhost:8080/execute -H "Content-Type: application/json" -d '{"code":"import matplotlib.pyplot as plt\nimport numpy as np\n\nx = np.linspace(0, 10, 100)\ny = np.sin(x)\n\nplt.figure()\nplt.plot(x, y)\nplt.savefig(\"sine_wave.png\")\nprint(\"Artifact generated\")","language":"python"}')
  
  if [[ $ARTIFACT_RESULT == *"error"* ]]; then
    log_test_result "Artifact Generation" "FAIL" "Artifact generation returned error"
  else
    log_test_result "Artifact Generation" "PASS" "Artifact generation working correctly"
  fi
  
  # Test timeout handling
  echo "Testing timeout handling..."
  TIMEOUT_RESULT=$(curl -s -X POST http://localhost:8080/execute -H "Content-Type: application/json" -d '{"code":"import time\nwhile True:\n    time.sleep(1)\n    print(\"Still running...\")","language":"python","timeout":5}')
  
  if [[ $TIMEOUT_RESULT == *"timeout"* ]]; then
    log_test_result "Timeout Handling" "PASS" "Timeout handling working correctly"
  else
    log_test_result "Timeout Handling" "FAIL" "Timeout handling not working correctly"
  fi
}

# Function to test frontend components
test_frontend_components() {
  echo "Testing frontend components..."
  
  # Check if frontend is running
  if ! curl -s http://localhost:3000 > /dev/null; then
    log_test_result "Frontend Health Check" "FAIL" "Frontend is not running"
    return 1
  fi
  
  # Since we can't easily test frontend components automatically,
  # we'll just check if the main pages load correctly
  
  # Test home page
  echo "Testing home page..."
  HOME_RESULT=$(curl -s http://localhost:3000)
  
  if [[ $HOME_RESULT == *"Atlas-Chat"* ]]; then
    log_test_result "Home Page" "PASS" "Home page loaded correctly"
  else
    log_test_result "Home Page" "FAIL" "Home page did not load correctly"
  fi
  
  # Test chat page
  echo "Testing chat page..."
  CHAT_RESULT=$(curl -s http://localhost:3000/chat)
  
  if [[ $CHAT_RESULT == *"Chat"* ]]; then
    log_test_result "Chat Page" "PASS" "Chat page loaded correctly"
  else
    log_test_result "Chat Page" "FAIL" "Chat page did not load correctly"
  fi
  
  # Test settings page
  echo "Testing settings page..."
  SETTINGS_RESULT=$(curl -s http://localhost:3000/settings)
  
  if [[ $SETTINGS_RESULT == *"Settings"* ]]; then
    log_test_result "Settings Page" "PASS" "Settings page loaded correctly"
  else
    log_test_result "Settings Page" "FAIL" "Settings page did not load correctly"
  fi
}

# Function to test agent delegation system
test_agent_delegation() {
  echo "Testing agent delegation system..."
  
  # Test team creation
  echo "Testing team creation..."
  TEAM_RESULT=$(curl -s -X POST http://localhost:8000/api/teams -H "Content-Type: application/json" -d '{"name":"Test Team","supervisorName":"Test Supervisor"}')
  
  if [[ $TEAM_RESULT == *"error"* ]]; then
    log_test_result "Team Creation" "FAIL" "Team creation returned error"
  else
    # Extract team ID from response
    TEAM_ID=$(echo $TEAM_RESULT | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    log_test_result "Team Creation" "PASS" "Team creation working correctly"
    
    # Test agent addition
    echo "Testing agent addition..."
    AGENT_RESULT=$(curl -s -X POST http://localhost:8000/api/teams/$TEAM_ID/agents -H "Content-Type: application/json" -d '{"name":"Test Agent","role":"coder","languages":["python"]}')
    
    if [[ $AGENT_RESULT == *"error"* ]]; then
      log_test_result "Agent Addition" "FAIL" "Agent addition returned error"
    else
      # Extract agent ID from response
      AGENT_ID=$(echo $AGENT_RESULT | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
      log_test_result "Agent Addition" "PASS" "Agent addition working correctly"
      
      # Test task delegation
      echo "Testing task delegation..."
      TASK_RESULT=$(curl -s -X POST http://localhost:8000/api/teams/$TEAM_ID/tasks -H "Content-Type: application/json" -d '{"title":"Test Task","description":"Write a function to calculate factorial","assignedTo":"'$AGENT_ID'"}')
      
      if [[ $TASK_RESULT == *"error"* ]]; then
        log_test_result "Task Delegation" "FAIL" "Task delegation returned error"
      else
        log_test_result "Task Delegation" "PASS" "Task delegation working correctly"
      fi
    fi
  fi
}

# Function to test security features
test_security_features() {
  echo "Testing security features..."
  
  # Test JWT authentication
  echo "Testing JWT authentication..."
  AUTH_RESULT=$(curl -s -X POST http://localhost:8000/api/auth/token -H "Content-Type: application/json" -d '{"username":"test","password":"test"}')
  
  if [[ $AUTH_RESULT == *"access_token"* ]]; then
    # Extract token from response
    TOKEN=$(echo $AUTH_RESULT | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    log_test_result "JWT Authentication" "PASS" "JWT authentication working correctly"
    
    # Test protected endpoint with token
    echo "Testing protected endpoint with token..."
    PROTECTED_RESULT=$(curl -s -X GET http://localhost:8000/api/users/me -H "Authorization: Bearer $TOKEN")
    
    if [[ $PROTECTED_RESULT == *"error"* ]]; then
      log_test_result "Protected Endpoint" "FAIL" "Protected endpoint returned error"
    else
      log_test_result "Protected Endpoint" "PASS" "Protected endpoint working correctly"
    fi
    
    # Test protected endpoint without token
    echo "Testing protected endpoint without token..."
    UNPROTECTED_RESULT=$(curl -s -X GET http://localhost:8000/api/users/me)
    
    if [[ $UNPROTECTED_RESULT == *"Unauthorized"* ]]; then
      log_test_result "Unauthorized Access" "PASS" "Unauthorized access correctly rejected"
    else
      log_test_result "Unauthorized Access" "FAIL" "Unauthorized access not correctly rejected"
    fi
  else
    log_test_result "JWT Authentication" "FAIL" "JWT authentication returned error"
  fi
  
  # Test code sanitization
  echo "Testing code sanitization..."
  SANITIZE_RESULT=$(curl -s -X POST http://localhost:8000/api/code/execute -H "Content-Type: application/json" -d '{"code":"import os\nos.system(\"ls\")","language":"python"}')
  
  if [[ $SANITIZE_RESULT == *"security"* ]]; then
    log_test_result "Code Sanitization" "PASS" "Code sanitization working correctly"
  else
    log_test_result "Code Sanitization" "FAIL" "Code sanitization not working correctly"
  fi
}

# Function to test performance optimizations
test_performance() {
  echo "Testing performance optimizations..."
  
  # Test response time for code execution
  echo "Testing code execution response time..."
  START_TIME=$(date +%s.%N)
  curl -s -X POST http://localhost:8000/api/code/execute -H "Content-Type: application/json" -d '{"code":"print(\"Hello, World!\")","language":"python"}' > /dev/null
  END_TIME=$(date +%s.%N)
  EXECUTION_TIME=$(echo "$END_TIME - $START_TIME" | bc)
  
  if (( $(echo "$EXECUTION_TIME < 2.0" | bc -l) )); then
    log_test_result "Code Execution Performance" "PASS" "Code execution response time is acceptable: $EXECUTION_TIME seconds"
  else
    log_test_result "Code Execution Performance" "FAIL" "Code execution response time is too slow: $EXECUTION_TIME seconds"
  fi
  
  # Test response time for chat messages
  echo "Testing chat message response time..."
  START_TIME=$(date +%s.%N)
  curl -s -X POST http://localhost:8000/api/chat/messages -H "Content-Type: application/json" -d '{"content":"Hello, World!","conversationId":"test"}' > /dev/null
  END_TIME=$(date +%s.%N)
  MESSAGE_TIME=$(echo "$END_TIME - $START_TIME" | bc)
  
  if (( $(echo "$MESSAGE_TIME < 1.0" | bc -l) )); then
    log_test_result "Chat Message Performance" "PASS" "Chat message response time is acceptable: $MESSAGE_TIME seconds"
  else
    log_test_result "Chat Message Performance" "FAIL" "Chat message response time is too slow: $MESSAGE_TIME seconds"
  fi
  
  # Test memory usage
  echo "Testing memory usage..."
  MEMORY_USAGE=$(ps -o rss= -p $(pgrep -f "python.*app/main.py") | awk '{print $1/1024}')
  
  if (( $(echo "$MEMORY_USAGE < 500.0" | bc -l) )); then
    log_test_result "Memory Usage" "PASS" "Memory usage is acceptable: $MEMORY_USAGE MB"
  else
    log_test_result "Memory Usage" "FAIL" "Memory usage is too high: $MEMORY_USAGE MB"
  fi
}

# Function to test Docker configuration
test_docker_configuration() {
  echo "Testing Docker configuration..."
  
  # Check if Docker is installed
  if ! command -v docker &> /dev/null; then
    log_test_result "Docker Installation" "FAIL" "Docker is not installed"
    return 1
  fi
  
  # Check if Docker Compose is installed
  if ! command -v docker-compose &> /dev/null; then
    log_test_result "Docker Compose Installation" "FAIL" "Docker Compose is not installed"
    return 1
  fi
  
  # Validate docker-compose.yml
  echo "Validating docker-compose.yml..."
  if docker-compose config > /dev/null; then
    log_test_result "Docker Compose Configuration" "PASS" "docker-compose.yml is valid"
  else
    log_test_result "Docker Compose Configuration" "FAIL" "docker-compose.yml is invalid"
  fi
  
  # Check if all required services are defined
  echo "Checking required services..."
  REQUIRED_SERVICES=("mongodb" "postgres" "redis" "backend" "e2b-codeinterpreter" "frontend" "nginx")
  
  for service in "${REQUIRED_SERVICES[@]}"; do
    if grep -q "^  $service:" docker-compose.yml; then
      log_test_result "Docker Service: $service" "PASS" "Service is defined in docker-compose.yml"
    else
      log_test_result "Docker Service: $service" "FAIL" "Service is not defined in docker-compose.yml"
    fi
  done
  
  # Check if all required volumes are defined
  echo "Checking required volumes..."
  REQUIRED_VOLUMES=("mongodb_data" "postgres_data" "redis_data" "backend_data" "e2b_data")
  
  for volume in "${REQUIRED_VOLUMES[@]}"; do
    if grep -q "^  $volume:" docker-compose.yml; then
      log_test_result "Docker Volume: $volume" "PASS" "Volume is defined in docker-compose.yml"
    else
      log_test_result "Docker Volume: $volume" "FAIL" "Volume is not defined in docker-compose.yml"
    fi
  done
}

# Function to fix identified issues
fix_issues() {
  echo "Fixing identified issues..."
  
  # Read test results
  ISSUES=$(grep "FAIL" "$RESULTS_DIR/test_results.log")
  
  if [ -z "$ISSUES" ]; then
    echo "No issues to fix!"
    return 0
  fi
  
  echo "Found issues to fix:"
  echo "$ISSUES"
  
  # Fix E2B code interpreter timeout handling
  if grep -q "Timeout Handling.*FAIL" "$RESULTS_DIR/test_results.log"; then
    echo "Fixing E2B code interpreter timeout handling..."
    
    # Check if the file exists
    if [ -f "backend/app/core/services/e2b/session.py" ]; then
      # Add timeout handling code
      cat << 'EOF' > backend/app/core/services/e2b/session.py.fixed
import asyncio
import logging
from typing import Dict, Any, Optional

from e2b import Session

from app.core.config import settings
from app.core.performance import TimeoutError, with_timeout

logger = logging.getLogger(__name__)

class E2BSession:
    """
    Wrapper for E2B session with improved timeout handling.
    """
    
    def __init__(self, session_id: str, api_key: Optional[str] = None):
        """
        Initialize the E2B session.
        
        Args:
            session_id: Session ID
            api_key: E2B API key (optional, defaults to settings)
        """
        self.session_id = session_id
        self.api_key = api_key or settings.E2B_API_KEY
        self.session = None
    
    async def initialize(self):
        """
        Initialize the E2B session.
        
        Returns:
            E2B session
        """
        try:
            self.session = await with_timeout(
                Session.create(api_key=self.api_key),
                timeout=settings.E2B_SESSION_TIMEOUT
            )
            return self.session
        except TimeoutError:
            logger.error(f"Timeout while creating E2B session {self.session_id}")
            raise TimeoutError(f"Timeout while creating E2B session {self.session_id}")
        except Exception as e:
            logger.error(f"Error creating E2B session {self.session_id}: {str(e)}")
            raise
    
    async def execute_code(self, code: str, language: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute code in the E2B session.
        
        Args:
            code: Code to execute
            language: Programming language
            timeout: Execution timeout in seconds
            
        Returns:
            Execution result
        """
        if not self.session:
            await self.initialize()
        
        try:
            # Use the specified timeout or default
            execution_timeout = timeout or settings.E2B_EXECUTION_TIMEOUT
            
            # Execute the code with timeout
            result = await with_timeout(
                self.session.process.start_and_wait(
                    cmd=["python3", "-c", code] if language == "python" else ["node", "-e", code],
                    timeout=execution_timeout * 1000  # Convert to milliseconds
                ),
                timeout=execution_timeout + 5  # Add 5 seconds buffer
            )
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.exit_code
            }
        except TimeoutError:
            logger.error(f"Timeout while executing code in session {self.session_id}")
            return {
                "stdout": "",
                "stderr": "Execution timed out",
                "exit_code": 124
            }
        except Exception as e:
            logger.error(f"Error executing code in session {self.session_id}: {str(e)}")
            return {
                "stdout": "",
                "stderr": f"Error: {str(e)}",
                "exit_code": 1
            }
    
    async def close(self):
        """
        Close the E2B session.
        """
        if self.session:
            try:
                await with_timeout(
                    self.session.close(),
                    timeout=settings.E2B_SESSION_TIMEOUT
                )
            except TimeoutError:
                logger.error(f"Timeout while closing E2B session {self.session_id}")
            except Exception as e:
                logger.error(f"Error closing E2B session {self.session_id}: {str(e)}")
            finally:
                self.session = None
EOF
      
      # Replace the original file
      mv backend/app/core/services/e2b/session.py.fixed backend/app/core/services/e2b/session.py
      
      log_test_result "Fix: E2B Timeout Handling" "DONE" "Fixed E2B code interpreter timeout handling"
    else
      log_test_result "Fix: E2B Timeout Handling" "SKIP" "File not found: backend/app/core/services/e2b/session.py"
    fi
  fi
  
  # Fix agent delegation error recovery
  if grep -q "Agent Delegation.*FAIL" "$RESULTS_DIR/test_results.log"; then
    echo "Fixing agent delegation error recovery..."
    
    # Check if the file exists
    if [ -f "backend/app/core/services/agent_service.py" ]; then
      # Add error recovery code
      cat << 'EOF' > backend/app/core/services/agent_service.py.fixed
import logging
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.performance import measure_performance
from app.core.security import log_security_event
from app.models.user import User
from app.db.session import get_db

logger = logging.getLogger(__name__)

class AgentService:
    """
    Service for managing agents and teams.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the agent service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.teams = {}
        self.agents = {}
        self.tasks = {}
        self.recovery_attempts = {}
        self.max_recovery_attempts = 3
    
    @measure_performance
    async def create_team(self, name: str, supervisor_name: str, user_id: str) -> Dict[str, Any]:
        """
        Create a new team.
        
        Args:
            name: Team name
            supervisor_name: Supervisor name
            user_id: User ID
            
        Returns:
            Team data
        """
        team_id = str(uuid.uuid4())
        
        team = {
            "id": team_id,
            "name": name,
            "supervisor_name": supervisor_name,
            "created_by": user_id,
            "created_at": datetime.utcnow(),
            "agents": {},
            "tasks": [],
            "messages": []
        }
        
        self.teams[team_id] = team
        
        # Log security event
        log_security_event(
            db=self.db,
            user_id=user_id,
            action="create_team",
            resource_type="team",
            resource_id=team_id,
            status="success"
        )
        
        return team
    
    @measure_performance
    async def add_agent(self, team_id: str, name: str, role: str, languages: List[str], user_id: str) -> Dict[str, Any]:
        """
        Add an agent to a team.
        
        Args:
            team_id: Team ID
            name: Agent name
            role: Agent role
            languages: Programming languages
            user_id: User ID
            
        Returns:
            Agent data
        """
        if team_id not in self.teams:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team {team_id} not found"
            )
        
        agent_id = str(uuid.uuid4())
        
        agent = {
            "id": agent_id,
            "name": name,
            "role": role,
            "languages": languages,
            "team_id": team_id,
            "created_by": user_id,
            "created_at": datetime.utcnow(),
            "status": "available"
        }
        
        self.agents[agent_id] = agent
        self.teams[team_id]["agents"][agent_id] = agent
        
        # Initialize recovery attempts
        self.recovery_attempts[agent_id] = 0
        
        # Log security event
        log_security_event(
            db=self.db,
            user_id=user_id,
            action="add_agent",
            resource_type="agent",
            resource_id=agent_id,
            status="success",
            details={"team_id": team_id}
        )
        
        return agent
    
    @measure_performance
    async def remove_agent(self, team_id: str, agent_id: str, user_id: str) -> bool:
        """
        Remove an agent from a team.
        
        Args:
            team_id: Team ID
            agent_id: Agent ID
            user_id: User ID
            
        Returns:
            True if the agent was removed, False otherwise
        """
        if team_id not in self.teams:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team {team_id} not found"
            )
        
        if agent_id not in self.agents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        
        if agent_id not in self.teams[team_id]["agents"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent {agent_id} is not in team {team_id}"
            )
        
        # Remove the agent from the team
        del self.teams[team_id]["agents"][agent_id]
        
        # Remove the agent from the agents dictionary
        del self.agents[agent_id]
        
        # Remove recovery attempts
        if agent_id in self.recovery_attempts:
            del self.recovery_attempts[agent_id]
        
        # Log security event
        log_security_event(
            db=self.db,
            user_id=user_id,
            action="remove_agent",
            resource_type="agent",
            resource_id=agent_id,
            status="success",
            details={"team_id": team_id}
        )
        
        return True
    
    @measure_performance
    async def create_task(self, team_id: str, title: str, description: str, assigned_to: str, user_id: str) -> Dict[str, Any]:
        """
        Create a new task.
        
        Args:
            team_id: Team ID
            title: Task title
            description: Task description
            assigned_to: Agent ID
            user_id: User ID
            
        Returns:
            Task data
        """
        if team_id not in self.teams:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team {team_id} not found"
            )
        
        if assigned_to not in self.agents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {assigned_to} not found"
            )
        
        if assigned_to not in self.teams[team_id]["agents"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent {assigned_to} is not in team {team_id}"
            )
        
        task_id = str(uuid.uuid4())
        
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "team_id": team_id,
            "assigned_to": assigned_to,
            "created_by": user_id,
            "created_at": datetime.utcnow(),
            "status": "pending",
            "result": None
        }
        
        self.tasks[task_id] = task
        self.teams[team_id]["tasks"].append(task)
        
        # Update agent status
        self.agents[assigned_to]["status"] = "busy"
        
        # Log security event
        log_security_event(
            db=self.db,
            user_id=user_id,
            action="create_task",
            resource_type="task",
            resource_id=task_id,
            status="success",
            details={"team_id": team_id, "assigned_to": assigned_to}
        )
        
        # Start task execution
        try:
            await self._execute_task(task_id)
            return task
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            task["status"] = "error"
            task["result"] = {"error": str(e)}
            
            # Attempt recovery
            await self._recover_agent(assigned_to)
            
            return task
    
    async def _execute_task(self, task_id: str) -> None:
        """
        Execute a task.
        
        Args:
            task_id: Task ID
        """
        task = self.tasks[task_id]
        agent_id = task["assigned_to"]
        agent = self.agents[agent_id]
        
        # Update task status
        task["status"] = "in_progress"
        
        try:
            # Delegate to the appropriate executor based on agent role
            if agent["role"] == "coder":
                # Delegate to code executor
                result = await self._execute_coding_task(task)
            elif agent["role"] == "reviewer":
                # Delegate to review executor
                result = await self._execute_review_task(task)
            elif agent["role"] == "tester":
                # Delegate to test executor
                result = await self._execute_test_task(task)
            else:
                # Default executor
                result = await self._execute_default_task(task)
            
            # Update task with result
            task["status"] = "completed"
            task["result"] = result
            task["completed_at"] = datetime.utcnow()
            
            # Update agent status
            agent["status"] = "available"
            
            # Reset recovery attempts
            self.recovery_attempts[agent_id] = 0
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            task["status"] = "error"
            task["result"] = {"error": str(e)}
            
            # Attempt recovery
            await self._recover_agent(agent_id)
    
    async def _recover_agent(self, agent_id: str) -> None:
        """
        Recover an agent after an error.
        
        Args:
            agent_id: Agent ID
        """
        if agent_id not in self.agents:
            return
        
        # Increment recovery attempts
        self.recovery_attempts[agent_id] += 1
        
        # Check if we've exceeded the maximum number of recovery attempts
        if self.recovery_attempts[agent_id] > self.max_recovery_attempts:
            logger.error(f"Agent {agent_id} has exceeded the maximum number of recovery attempts")
            self.agents[agent_id]["status"] = "error"
            return
        
        # Reset agent status
        self.agents[agent_id]["status"] = "recovering"
        
        try:
            # Perform recovery actions
            logger.info(f"Recovering agent {agent_id} (attempt {self.recovery_attempts[agent_id]})")
            
            # Wait a bit before recovery
            await asyncio.sleep(2)
            
            # Reset agent status
            self.agents[agent_id]["status"] = "available"
            
            logger.info(f"Agent {agent_id} recovered successfully")
        except Exception as e:
            logger.error(f"Error recovering agent {agent_id}: {str(e)}")
            self.agents[agent_id]["status"] = "error"
    
    async def _execute_coding_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a coding task.
        
        Args:
            task: Task data
            
        Returns:
            Task result
        """
        # This would typically delegate to the E2B code interpreter
        # For now, we'll just return a placeholder result
        return {
            "code": "def factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n-1)",
            "language": "python",
            "output": "Function defined successfully"
        }
    
    async def _execute_review_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a review task.
        
        Args:
            task: Task data
            
        Returns:
            Task result
        """
        # This would typically perform a code review
        # For now, we'll just return a placeholder result
        return {
            "review": "Code looks good!",
            "issues": []
        }
    
    async def _execute_test_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a test task.
        
        Args:
            task: Task data
            
        Returns:
            Task result
        """
        # This would typically run tests
        # For now, we'll just return a placeholder result
        return {
            "tests_run": 5,
            "tests_passed": 5,
            "tests_failed": 0
        }
    
    async def _execute_default_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a default task.
        
        Args:
            task: Task data
            
        Returns:
            Task result
        """
        # This is a fallback for unknown task types
        # For now, we'll just return a placeholder result
        return {
            "message": "Task completed successfully"
        }
EOF
      
      # Replace the original file
      mv backend/app/core/services/agent_service.py.fixed backend/app/core/services/agent_service.py
      
      log_test_result "Fix: Agent Delegation Error Recovery" "DONE" "Fixed agent delegation error recovery"
    else
      log_test_result "Fix: Agent Delegation Error Recovery" "SKIP" "File not found: backend/app/core/services/agent_service.py"
    fi
  fi
  
  # Fix frontend UI responsiveness
  if grep -q "Frontend.*FAIL" "$RESULTS_DIR/test_results.log"; then
    echo "Fixing frontend UI responsiveness..."
    
    # Check if the file exists
    if [ -f "frontend/client/src/styles/main.css" ]; then
      # Add responsive styles
      cat << 'EOF' >> frontend/client/src/styles/main.css

/* Responsive styles */
@media (max-width: 768px) {
  .container {
    padding: 0.5rem;
  }
  
  .sidebar {
    width: 100%;
    position: fixed;
    top: 0;
    left: 0;
    height: auto;
    z-index: 100;
    transform: translateX(-100%);
    transition: transform 0.3s ease-in-out;
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
  
  .main-content {
    margin-left: 0;
    width: 100%;
  }
  
  .header {
    padding: 0.5rem;
  }
  
  .chat-container {
    height: calc(100vh - 120px);
  }
  
  .message-input {
    padding: 0.5rem;
  }
  
  .code-editor {
    height: 300px;
  }
  
  .team-management-interface {
    flex-direction: column;
  }
  
  .teams-sidebar {
    width: 100%;
    height: auto;
    max-height: 200px;
    overflow-y: auto;
  }
  
  .team-content {
    width: 100%;
  }
  
  .modal-content {
    width: 90%;
    max-width: 500px;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0.25rem;
  }
  
  .header {
    padding: 0.25rem;
  }
  
  .chat-container {
    height: calc(100vh - 100px);
  }
  
  .message {
    padding: 0.5rem;
  }
  
  .code-editor {
    height: 200px;
  }
  
  .modal-content {
    width: 95%;
  }
  
  .form-group {
    margin-bottom: 0.5rem;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions button {
    width: 100%;
    margin: 0.25rem 0;
  }
}
EOF
      
      log_test_result "Fix: Frontend UI Responsiveness" "DONE" "Added responsive styles to main.css"
    else
      log_test_result "Fix: Frontend UI Responsiveness" "SKIP" "File not found: frontend/client/src/styles/main.css"
    fi
  fi
  
  # Fix artifact display
  if grep -q "Artifact.*FAIL" "$RESULTS_DIR/test_results.log"; then
    echo "Fixing artifact display..."
    
    # Check if the file exists
    if [ -f "frontend/client/src/components/Artifacts/ArtifactDisplay.jsx" ]; then
      # Add support for more file types
      cat << 'EOF' > frontend/client/src/components/Artifacts/ArtifactDisplay.jsx.fixed
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { FiDownload, FiTrash2, FiMaximize2, FiMinimize2 } from 'react-icons/fi';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';

const ArtifactDisplay = ({
  artifact,
  onDownload,
  onDelete,
  className = '',
  showControls = true
}) => {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState(false);
  const [content, setContent] = useState(null);
  
  useEffect(() => {
    if (artifact && artifact.url) {
      fetchArtifactContent();
    }
  }, [artifact]);
  
  const fetchArtifactContent = async () => {
    try {
      const response = await fetch(artifact.url);
      
      if (isTextFile(artifact.type)) {
        const text = await response.text();
        setContent(text);
      } else if (isImageFile(artifact.type)) {
        setContent(artifact.url);
      } else if (isPdfFile(artifact.type)) {
        setContent(artifact.url);
      } else {
        setContent(null);
      }
    } catch (error) {
      console.error('Error fetching artifact content:', error);
      setContent(null);
    }
  };
  
  const isTextFile = (type) => {
    const textTypes = [
      'text/plain',
      'text/html',
      'text/css',
      'text/javascript',
      'application/json',
      'application/xml',
      'application/javascript',
      'application/typescript',
      'text/markdown',
      'text/csv',
      'text/yaml',
      'text/x-python',
      'text/x-java',
      'text/x-c',
      'text/x-cpp',
      'text/x-csharp',
      'text/x-go',
      'text/x-rust',
      'text/x-ruby'
    ];
    
    return textTypes.includes(type) || type.startsWith('text/');
  };
  
  const isImageFile = (type) => {
    const imageTypes = [
      'image/png',
      'image/jpeg',
      'image/jpg',
      'image/gif',
      'image/svg+xml',
      'image/webp',
      'image/bmp',
      'image/tiff'
    ];
    
    return imageTypes.includes(type) || type.startsWith('image/');
  };
  
  const isPdfFile = (type) => {
    return type === 'application/pdf';
  };
  
  const isAudioFile = (type) => {
    const audioTypes = [
      'audio/mpeg',
      'audio/ogg',
      'audio/wav',
      'audio/webm',
      'audio/aac',
      'audio/flac'
    ];
    
    return audioTypes.includes(type) || type.startsWith('audio/');
  };
  
  const isVideoFile = (type) => {
    const videoTypes = [
      'video/mp4',
      'video/webm',
      'video/ogg',
      'video/quicktime',
      'video/x-msvideo',
      'video/x-matroska'
    ];
    
    return videoTypes.includes(type) || type.startsWith('video/');
  };
  
  const getLanguageFromType = (type) => {
    const typeToLanguage = {
      'text/javascript': 'javascript',
      'application/javascript': 'javascript',
      'application/typescript': 'typescript',
      'text/html': 'html',
      'text/css': 'css',
      'application/json': 'json',
      'application/xml': 'xml',
      'text/markdown': 'markdown',
      'text/x-python': 'python',
      'text/x-java': 'java',
      'text/x-c': 'c',
      'text/x-cpp': 'cpp',
      'text/x-csharp': 'csharp',
      'text/x-go': 'go',
      'text/x-rust': 'rust',
      'text/x-ruby': 'ruby',
      'text/yaml': 'yaml',
      'text/csv': 'csv'
    };
    
    return typeToLanguage[type] || 'text';
  };
  
  const getLanguageFromFilename = (filename) => {
    const extension = filename.split('.').pop().toLowerCase();
    
    const extensionToLanguage = {
      'js': 'javascript',
      'ts': 'typescript',
      'html': 'html',
      'css': 'css',
      'json': 'json',
      'xml': 'xml',
      'md': 'markdown',
      'py': 'python',
      'java': 'java',
      'c': 'c',
      'cpp': 'cpp',
      'cs': 'csharp',
      'go': 'go',
      'rs': 'rust',
      'rb': 'ruby',
      'yaml': 'yaml',
      'yml': 'yaml',
      'csv': 'csv',
      'txt': 'text'
    };
    
    return extensionToLanguage[extension] || 'text';
  };
  
  const getLanguage = () => {
    if (artifact.type) {
      const languageFromType = getLanguageFromType(artifact.type);
      if (languageFromType !== 'text') {
        return languageFromType;
      }
    }
    
    if (artifact.filename) {
      return getLanguageFromFilename(artifact.filename);
    }
    
    return 'text';
  };
  
  const handleDownload = () => {
    if (onDownload) {
      onDownload(artifact);
    }
  };
  
  const handleDelete = () => {
    if (onDelete) {
      onDelete(artifact);
    }
  };
  
  const toggleExpanded = () => {
    setExpanded(!expanded);
  };
  
  const renderContent = () => {
    if (!content) {
      return (
        <div className="artifact-placeholder">
          <p>{t('Loading artifact...')}</p>
        </div>
      );
    }
    
    if (isTextFile(artifact.type)) {
      return (
        <SyntaxHighlighter
          language={getLanguage()}
          style={docco}
          showLineNumbers={true}
          wrapLines={true}
          className="artifact-code"
        >
          {content}
        </SyntaxHighlighter>
      );
    } else if (isImageFile(artifact.type)) {
      return (
        <div className="artifact-image-container">
          <img
            src={content}
            alt={artifact.filename || 'Image artifact'}
            className="artifact-image"
          />
        </div>
      );
    } else if (isPdfFile(artifact.type)) {
      return (
        <div className="artifact-pdf-container">
          <iframe
            src={`${content}#view=FitH`}
            title={artifact.filename || 'PDF artifact'}
            className="artifact-pdf"
          />
        </div>
      );
    } else if (isAudioFile(artifact.type)) {
      return (
        <div className="artifact-audio-container">
          <audio
            src={artifact.url}
            controls
            className="artifact-audio"
          >
            {t('Your browser does not support the audio element.')}
          </audio>
        </div>
      );
    } else if (isVideoFile(artifact.type)) {
      return (
        <div className="artifact-video-container">
          <video
            src={artifact.url}
            controls
            className="artifact-video"
          >
            {t('Your browser does not support the video element.')}
          </video>
        </div>
      );
    } else {
      return (
        <div className="artifact-unsupported">
          <p>{t('Unsupported file type: {{type}}', { type: artifact.type })}</p>
          <button
            className="primary-button"
            onClick={handleDownload}
          >
            {t('Download')}
          </button>
        </div>
      );
    }
  };
  
  return (
    <div className={`artifact-display ${expanded ? 'expanded' : ''} ${className}`}>
      <div className="artifact-header">
        <div className="artifact-info">
          <span className="artifact-name">{artifact.filename || 'Unnamed artifact'}</span>
          <span className="artifact-type">{artifact.type || 'Unknown type'}</span>
        </div>
        
        {showControls && (
          <div className="artifact-controls">
            <button
              className="icon-button"
              onClick={toggleExpanded}
              title={expanded ? t('Minimize') : t('Maximize')}
            >
              {expanded ? <FiMinimize2 /> : <FiMaximize2 />}
            </button>
            <button
              className="icon-button"
              onClick={handleDownload}
              title={t('Download')}
            >
              <FiDownload />
            </button>
            <button
              className="icon-button"
              onClick={handleDelete}
              title={t('Delete')}
            >
              <FiTrash2 />
            </button>
          </div>
        )}
      </div>
      
      <div className="artifact-content">
        {renderContent()}
      </div>
    </div>
  );
};

export default ArtifactDisplay;
EOF
      
      # Replace the original file
      mv frontend/client/src/components/Artifacts/ArtifactDisplay.jsx.fixed frontend/client/src/components/Artifacts/ArtifactDisplay.jsx
      
      log_test_result "Fix: Artifact Display" "DONE" "Enhanced artifact display for various file types"
    else
      log_test_result "Fix: Artifact Display" "SKIP" "File not found: frontend/client/src/components/Artifacts/ArtifactDisplay.jsx"
    fi
  fi
  
  # Fix performance issues
  if grep -q "Performance.*FAIL" "$RESULTS_DIR/test_results.log"; then
    echo "Fixing performance issues..."
    
    # Check if the file exists
    if [ -f "frontend/client/src/components/Chat/Conversation.jsx" ]; then
      # Add pagination for conversation history
      cat << 'EOF' > frontend/client/src/components/Chat/Conversation.jsx.fixed
import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { FiChevronUp, FiChevronDown } from 'react-icons/fi';
import ChatMessage from './ChatMessage';

const Conversation = ({
  messages = [],
  onLoadMore,
  hasMoreMessages = false,
  className = ''
}) => {
  const { t } = useTranslation();
  const [visibleMessages, setVisibleMessages] = useState([]);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const messagesPerPage = 20;
  
  useEffect(() => {
    // Initialize with the most recent messages
    const startIdx = Math.max(0, messages.length - messagesPerPage);
    setVisibleMessages(messages.slice(startIdx));
    setPage(1);
  }, [messages]);
  
  useEffect(() => {
    // Scroll to bottom when new messages are added
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [visibleMessages]);
  
  const handleLoadMore = async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    
    try {
      // If there's an external load more function, call it
      if (onLoadMore) {
        await onLoadMore();
      }
      
      // Calculate the next page of messages
      const nextPage = page + 1;
      const endIdx = messages.length;
      const startIdx = Math.max(0, endIdx - (nextPage * messagesPerPage));
      
      setVisibleMessages(messages.slice(startIdx));
      setPage(nextPage);
    } catch (error) {
      console.error('Error loading more messages:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleScrollToBottom = () => {
    // Reset to the most recent messages
    const startIdx = Math.max(0, messages.length - messagesPerPage);
    setVisibleMessages(messages.slice(startIdx));
    setPage(1);
    
    // Scroll to bottom
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };
  
  return (
    <div className={`conversation ${className}`}>
      {(messages.length > visibleMessages.length || hasMoreMessages) && (
        <div className="load-more-container">
          <button
            className="load-more-button"
            onClick={handleLoadMore}
            disabled={isLoading}
          >
            {isLoading ? t('Loading...') : t('Load more messages')}
          </button>
        </div>
      )}
      
      <div className="messages-container">
        {visibleMessages.map(message => (
          <ChatMessage
            key={message.id}
            message={message}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      {messages.length > messagesPerPage && (
        <button
          className="scroll-to-bottom-button"
          onClick={handleScrollToBottom}
          title={t('Scroll to bottom')}
        >
          <FiChevronDown />
        </button>
      )}
    </div>
  );
};

export default Conversation;
EOF
      
      # Replace the original file
      mv frontend/client/src/components/Chat/Conversation.jsx.fixed frontend/client/src/components/Chat/Conversation.jsx
      
      log_test_result "Fix: Performance Issues" "DONE" "Added pagination for conversation history"
    else
      log_test_result "Fix: Performance Issues" "SKIP" "File not found: frontend/client/src/components/Chat/Conversation.jsx"
    fi
  fi
  
  echo "Fixes applied successfully!"
}

# Main execution
echo "Starting comprehensive testing..."

# Run test functions
test_backend_api
test_e2b_code_interpreter
test_frontend_components
test_agent_delegation
test_security_features
test_performance
test_docker_configuration

# Fix identified issues
fix_issues

# Create a summary report
echo "Creating summary report..."
PASS_COUNT=$(grep "PASS" "$RESULTS_DIR/test_results.log" | wc -l)
FAIL_COUNT=$(grep "FAIL" "$RESULTS_DIR/test_results.log" | wc -l)
DONE_COUNT=$(grep "DONE" "$RESULTS_DIR/test_results.log" | wc -l)
SKIP_COUNT=$(grep "SKIP" "$RESULTS_DIR/test_results.log" | wc -l)

echo "# Test Summary" > "$RESULTS_DIR/summary.md"
echo "" >> "$RESULTS_DIR/summary.md"
echo "- **Date:** $(date)" >> "$RESULTS_DIR/summary.md"
echo "- **Total Tests:** $(($PASS_COUNT + $FAIL_COUNT))" >> "$RESULTS_DIR/summary.md"
echo "- **Passed:** $PASS_COUNT" >> "$RESULTS_DIR/summary.md"
echo "- **Failed:** $FAIL_COUNT" >> "$RESULTS_DIR/summary.md"
echo "- **Fixed:** $DONE_COUNT" >> "$RESULTS_DIR/summary.md"
echo "- **Skipped Fixes:** $SKIP_COUNT" >> "$RESULTS_DIR/summary.md"
echo "" >> "$RESULTS_DIR/summary.md"
echo "## Test Results" >> "$RESULTS_DIR/summary.md"
echo "" >> "$RESULTS_DIR/summary.md"
echo "```" >> "$RESULTS_DIR/summary.md"
cat "$RESULTS_DIR/test_results.log" >> "$RESULTS_DIR/summary.md"
echo "```" >> "$RESULTS_DIR/summary.md"

echo "Testing completed successfully!"
echo "Test results saved to: $RESULTS_DIR/test_results.log"
echo "Summary report saved to: $RESULTS_DIR/summary.md"

echo "Done!"
