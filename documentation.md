# Atlas-Chat Documentation

## Overview

Atlas-Chat is a sophisticated AI assistant application with a Python/FastAPI backend and React frontend. It features dual execution capabilities (OpenAI Agents SDK and LangGraph), secure code execution, file management, and multiple database integrations.

This documentation provides a comprehensive guide to the application's architecture, features, and usage.

## Table of Contents

1. [Architecture](#architecture)
2. [Features](#features)
3. [E2B Code Interpreter](#e2b-code-interpreter)
4. [Agent Delegation System](#agent-delegation-system)
5. [UI Components](#ui-components)
6. [Security](#security)
7. [Performance Optimizations](#performance-optimizations)
8. [Docker Configuration](#docker-configuration)
9. [Installation](#installation)
10. [Usage](#usage)
11. [API Reference](#api-reference)
12. [Contributing](#contributing)
13. [License](#license)

## Architecture

Atlas-Chat follows a modern microservices architecture with the following components:

### Backend

- **FastAPI Framework**: High-performance asynchronous API framework
- **Dual Execution Engines**:
  - OpenAI Agents SDK for standard agent operations
  - LangGraph for complex multi-agent workflows
- **Database Layer**: Support for MongoDB, PostgreSQL, and Redis
- **E2B Integration**: Secure code execution environment
- **Authentication**: JWT-based authentication with role-based access control

### Frontend

- **React**: Component-based UI library
- **Redux**: State management
- **TailwindCSS**: Utility-first CSS framework
- **Socket.IO**: Real-time communication
- **React Router**: Client-side routing

### Infrastructure

- **Docker**: Containerization for consistent deployment
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy and static file serving

## Features

### Core Features

- **AI Chat Interface**: Conversational interface with AI assistants
- **Code Execution**: Secure execution of code in multiple languages
- **File Management**: Upload, download, and manage files
- **Team Collaboration**: Multi-agent teams with specialized roles
- **Artifact Generation**: Create and share artifacts from code execution
- **Model Switching**: Intelligent selection of AI models based on task

### Advanced Features

- **Agent Delegation**: Supervisor agents can delegate tasks to specialized agents
- **Code Interpreter**: E2B-powered secure code execution environment
- **Multi-Language Support**: Execute code in Python, JavaScript, and more
- **Artifact Visualization**: Rich display of various artifact types
- **Responsive Design**: Optimized for desktop and mobile devices

## E2B Code Interpreter

The E2B Code Interpreter provides secure code execution capabilities with support for multiple programming languages.

### Features

- **Secure Sandbox**: Isolated execution environment
- **Multi-Language Support**: Python, JavaScript, TypeScript, and more
- **Package Installation**: Install dependencies on-demand
- **Artifact Generation**: Create and share visualizations, data, and more
- **Timeout Handling**: Robust handling of long-running processes
- **Error Recovery**: Automatic recovery from execution errors

### Usage

```python
# Example of using the E2B Code Interpreter
from app.core.services.e2b.session import E2BSession

async def execute_code():
    session = E2BSession(session_id="example-session")
    await session.initialize()

    result = await session.execute_code(
        code="print('Hello, World!')",
        language="python",
        timeout=30
    )

    print(result)
    await session.close()
```

## Agent Delegation System

The Agent Delegation System enables team-based collaboration with specialized agents.

### Features

- **Team Creation**: Create teams of AI agents
- **Role-Based Agents**: Specialized agents for coding, reviewing, testing, etc.
- **Task Delegation**: Assign tasks to appropriate agents
- **Error Recovery**: Robust error handling and recovery
- **Roo-Code Integration**: Enhanced autonomous agent capabilities

### Usage

```python
# Example of using the Agent Delegation System
from app.core.services.agent_service import AgentService

async def delegate_task():
    agent_service = AgentService(db=db_session)

    # Create a team
    team = await agent_service.create_team(
        name="Development Team",
        supervisor_name="Tech Lead",
        user_id="user123"
    )

    # Add an agent
    agent = await agent_service.add_agent(
        team_id=team["id"],
        name="Python Coder",
        role="coder",
        languages=["python"],
        user_id="user123"
    )

    # Create a task
    task = await agent_service.create_task(
        team_id=team["id"],
        title="Implement Factorial Function",
        description="Write a function to calculate factorial",
        assigned_to=agent["id"],
        user_id="user123"
    )

    print(task)
```

## UI Components

Atlas-Chat includes a comprehensive set of UI components for a complete user experience.

### Core Components

- **Chat Interface**: Conversational UI with message history
- **Code Editor**: Monaco-based code editor with syntax highlighting
- **Artifact Display**: Rich visualization of various artifact types
- **Team Management**: Interface for managing agent teams
- **Settings Panel**: User preferences and configuration

### Responsive Design

The UI is fully responsive and optimized for both desktop and mobile devices, with adaptive layouts and touch support.

## Security

Atlas-Chat implements comprehensive security measures to protect user data and prevent malicious code execution.

### Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Fine-grained permission management
- **Code Sanitization**: Prevention of malicious code execution
- **Input Validation**: Validation of all user inputs
- **Rate Limiting**: Protection against abuse
- **Audit Logging**: Comprehensive logging of security events

## Performance Optimizations

Atlas-Chat includes various performance optimizations to ensure a smooth user experience.

### Optimizations

- **Lazy Loading**: Load components and data on-demand
- **Pagination**: Efficient handling of large datasets
- **Caching**: Redis-based caching for frequently accessed data
- **Asynchronous Processing**: Non-blocking API endpoints
- **Database Indexing**: Optimized database queries
- **Code Splitting**: Reduced bundle sizes for faster loading

## Docker Configuration

Atlas-Chat uses Docker for containerization and easy deployment.

### Components

- **Backend Container**: FastAPI application
- **Frontend Container**: React application with Nginx
- **E2B Container**: Code interpreter environment
- **Database Containers**: MongoDB, PostgreSQL, and Redis
- **Nginx Container**: Reverse proxy and static file serving

### Configuration

The `docker-compose.yml` file defines all services and their configurations, including:

- Network configuration
- Volume mounts
- Environment variables
- Health checks
- Restart policies

## Installation

### Prerequisites

- Docker and Docker Compose
- Node.js 16+ (for local development)
- Python 3.9+ (for local development)

### Docker Installation

1. Clone the repository:


   ```bash
   git clone https://github.com/KB01111/Atlas-Chat.git
   cd Atlas-Chat
   ```


2. Create a `.env` file with required environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```


3. Start the application:

   ```bash
   docker-compose up -d
   ```

4. Access the application at `http://localhost:3000`


### Local Development

1. Clone the repository:

   ```bash
   git clone https://github.com/KB01111/Atlas-Chat.git

   cd Atlas-Chat
   ```

2. Install backend dependencies:

   ```bash

   cd backend
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:


   ```bash
   cd frontend/client
   npm install
   ```

4. Start the backend:


   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

5. Start the frontend:

   ```bash
   cd frontend/client
   npm start
   ```

6. Access the application at `http://localhost:3000`

## Usage

### Creating a Conversation


1. Navigate to the chat interface
2. Click "New Chat" to start a new conversation
3. Type your message and press Enter
4. The AI assistant will respond to your message


### Executing Code

1. In a conversation, use code blocks with language specification:

   ````
   ```python
   print("Hello, World!")
   ````

   ```

   ```

2. Click the "Run" button to execute the code
3. View the execution results and any generated artifacts

### Managing Teams

1. Navigate to the Teams section
2. Click "Create Team" to create a new team
3. Add agents with specific roles to the team
4. Create tasks and assign them to agents
5. Monitor task progress and results

## API Reference

### Authentication

- `POST /api/auth/token`: Get JWT token
- `POST /api/auth/refresh`: Refresh JWT token
- `POST /api/auth/register`: Register new user
- `POST /api/auth/logout`: Logout user

### Conversations

- `GET /api/conversations`: List conversations
- `POST /api/conversations`: Create conversation
- `GET /api/conversations/{id}`: Get conversation
- `DELETE /api/conversations/{id}`: Delete conversation

### Messages

- `GET /api/conversations/{id}/messages`: List messages
- `POST /api/conversations/{id}/messages`: Create message
- `DELETE /api/messages/{id}`: Delete message

### Code Execution

- `POST /api/code/execute`: Execute code
- `GET /api/code/languages`: List supported languages
- `POST /api/code/install`: Install package

### Artifacts

- `GET /api/artifacts`: List artifacts
- `GET /api/artifacts/{id}`: Get artifact
- `DELETE /api/artifacts/{id}`: Delete artifact
- `GET /api/artifacts/{id}/download`: Download artifact

### Teams

- `GET /api/teams`: List teams
- `POST /api/teams`: Create team
- `GET /api/teams/{id}`: Get team
- `DELETE /api/teams/{id}`: Delete team
- `POST /api/teams/{id}/agents`: Add agent
- `DELETE /api/teams/{id}/agents/{agent_id}`: Remove agent
- `POST /api/teams/{id}/tasks`: Create task
- `GET /api/teams/{id}/tasks`: List tasks

## Contributing

We welcome contributions to Atlas-Chat! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

Please ensure your code follows our coding standards and includes appropriate tests.

## License

Atlas-Chat is licensed under the MIT License. See the LICENSE file for details.
