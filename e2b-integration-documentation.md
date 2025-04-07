# E2B Code Execution Integration Documentation

## Overview

This document provides comprehensive documentation for the E2B code execution integration in AtlasChat. The integration enables secure code execution capabilities within the AI assistant, allowing users to run code in various programming languages, manage files, and install packages in an isolated sandbox environment.

## Architecture

The E2B integration follows a layered architecture:

1. **Frontend Layer**: React components for code editing and execution
2. **API Layer**: FastAPI endpoints for code execution, file operations, and package management
3. **Service Layer**: ToolExecutor service that interfaces with E2B SDK
4. **Security Layer**: Validation and security measures to prevent malicious code execution
5. **E2B Sandbox**: Isolated environment for secure code execution

## Components

### 1. ToolExecutor Service

The `ToolExecutor` service is the core component that interfaces with the E2B SDK. It provides methods for:

- Executing code in various languages
- Reading and writing files
- Installing packages
- Managing sandbox lifecycle

Location: `/app/core/services/tool_executor.py`

Key methods:

- `execute_code(code, language, context)`: Executes code in the specified language
- `write_file(file_path, content, context)`: Writes content to a file in the sandbox
- `read_file(file_path, context)`: Reads content from a file in the sandbox
- `install_packages(packages, language, context)`: Installs packages in the sandbox

### 2. Code Execution API

The API layer exposes endpoints for interacting with the E2B sandbox:

Location: `/app/api/code.py`

Endpoints:

- `POST /code/execute`: Execute code in the sandbox
- `POST /code/write-file`: Write content to a file in the sandbox
- `POST /code/read-file`: Read content from a file in the sandbox
- `POST /code/install-packages`: Install packages in the sandbox

### 3. Frontend Components

The frontend includes a comprehensive code execution component:

Location: `/frontend/client/src/components/CodeExecution/CodeExecutionComponent.jsx`

Features:

- Monaco code editor with syntax highlighting
- Language selection (Python, JavaScript, TypeScript, Bash)
- File management (create, save, load)
- Package installation
- Real-time output display

### 4. Security Measures

Security is implemented at multiple levels:

Location: `/app/core/security.py`

Features:

- JWT authentication for API access
- Code validation to prevent dangerous patterns
- File path validation to prevent directory traversal
- Package name validation to prevent malicious packages
- Resource limitations in the E2B sandbox

### 5. Integration with Agent Service

The E2B code execution capability is integrated with the agent service:

Location: `/app/core/services/agent_service.py`

Integration points:

- Agent definitions include allowed tools
- Executors (SDK and LangGraph) have access to the ToolExecutor
- Tools are exposed to agents based on allowed_tools configuration

## Configuration

### E2B SDK Configuration

The E2B sandbox is configured in the ToolExecutor initialization:

```python
self.e2b_client = e2b.Sandbox(
    timeout=60,  # 60 second timeout
    on_stderr=self._handle_stderr,
    on_stdout=self._handle_stdout
)
```

### Security Configuration

Security settings are defined in the security module:

- JWT token expiration time
- Dangerous code patterns
- Suspicious file extensions
- Suspicious package names

## Usage Examples

### Executing Code

```python
# Backend API call
result = await tool_executor.execute_code(
    code="print('Hello, World!')",
    language="python",
    context=request_context
)

# Frontend API call
const result = await api.executeCode(
    "print('Hello, World!')",
    "python",
    threadId,
    agentId
);
```

### File Operations

```python
# Writing a file
result = await tool_executor.write_file(
    file_path="example.py",
    content="print('Hello, World!')",
    context=request_context
)

# Reading a file
result = await tool_executor.read_file(
    file_path="example.py",
    context=request_context
)
```

### Package Installation

```python
# Installing packages
result = await tool_executor.install_packages(
    packages=["numpy", "pandas"],
    language="python",
    context=request_context
)
```

## Security Considerations

### Sandbox Isolation

E2B provides a secure, isolated environment for code execution with:

- Resource limitations (CPU, memory, execution time)
- Network isolation
- File system isolation

### Code Validation

The security module validates code before execution:

- Checks for dangerous patterns
- Validates language support
- Prevents potentially malicious operations

### File Path Validation

File paths are validated to prevent:

- Directory traversal attacks
- Access to system files
- Creation of potentially dangerous files

### Package Validation

Package installation requests are validated to prevent:

- Installation of suspicious packages
- Command injection via package names

## Testing

Comprehensive tests are provided for the E2B integration:

Location: `/backend/tests/test_code_execution.py`

Test cases:

- Successful code execution
- Error handling
- File operations
- Package installation
- Security validation

## Deployment Considerations

When deploying the E2B integration:

1. Ensure the E2B SDK is properly installed
2. Configure appropriate timeouts for code execution
3. Set resource limits based on expected usage
4. Monitor sandbox usage and performance
5. Implement rate limiting for code execution requests

## Troubleshooting

Common issues and solutions:

1. **Sandbox initialization failure**:

   - Check E2B SDK installation
   - Verify network connectivity to E2B services

2. **Code execution timeouts**:

   - Increase timeout setting in E2B sandbox configuration
   - Optimize code to reduce execution time

3. **Package installation failures**:

   - Check package name validity
   - Verify network connectivity from sandbox
   - Ensure package is available in the repository

4. **Security validation errors**:
   - Review code for dangerous patterns
   - Check file paths for traversal attempts
   - Verify package names are not suspicious

## Conclusion

The E2B integration provides AtlasChat with secure code execution capabilities, enabling users to run code, manage files, and install packages within an isolated sandbox environment. The implementation follows best practices for security, usability, and performance.
