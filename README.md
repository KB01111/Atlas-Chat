# AtlasChat Development Documentation

## Project Overview
AtlasChat is a desktop AI assistant application built as a fork of LibreChat. It features a Python/FastAPI backend with dual execution capabilities (OpenAI Agents SDK and LangGraph), integrated with a React-based frontend. The application uses multiple databases for different purposes: Supabase (PostgreSQL) for relational data, Neo4j (Graphiti) for knowledge graphs, and Qdrant for vector storage.

## Architecture

### Backend Components
- **FastAPI Application**: Main backend server handling API requests
- **Dual Execution System**: Support for both OpenAI Agents SDK and LangGraph execution
- **ToolExecutor**: Centralized service for executing tools and managing capabilities
- **EmbeddingService**: Service for text embedding and vector storage/retrieval
- **Authentication**: JWT-based authentication system

### Database Structure
- **Supabase (PostgreSQL)**: Stores agent definitions, user data, conversation history, and audit logs
- **Neo4j (Graphiti)**: Stores knowledge graph for enhanced reasoning
- **Qdrant**: Vector database for RAG functionality

### Frontend Components
- **React Application**: User interface built with React
- **API Context**: Centralized API client for backend communication

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Node.js 20+
- Python 3.10+

### Development Setup
1. Clone the repository:
   ```
   git clone https://github.com/KB01111/AtlasChat.git
   cd AtlasChat
   ```

2. Set up environment variables:
   - Copy `.env.example` to `.env` in the backend directory
   - Update with your database credentials and API keys

3. Start the development environment:
   ```
   docker-compose up
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## API Documentation

### Authentication Endpoints
- `POST /api/auth/register`: Register a new user
- `POST /api/auth/token`: Login and get JWT token
- `GET /api/auth/me`: Get current user information

### Agent Definitions Endpoints
- `GET /api/agents`: List all agent definitions
- `GET /api/agents/{agent_id}`: Get a specific agent definition
- `POST /api/agents`: Create a new agent definition
- `PUT /api/agents/{agent_id}`: Update an agent definition
- `DELETE /api/agents/{agent_id}`: Delete an agent definition

### Chat Endpoints
- `POST /api/chat`: Send a message to an agent (streaming response)

## Deployment

The application can be deployed using Docker Compose:

```
docker-compose -f docker-compose.yml up -d
```

This will start all required services:
- Backend API
- Frontend web application
- PostgreSQL database
- Neo4j graph database
- Qdrant vector database

## Development Roadmap

### Phase 1: Core Services & Dual Execution (Completed)
- [x] Define context/state models
- [x] Implement ToolExecutor
- [x] Update executors with tool integration
- [x] Implement agent definitions API
- [x] Setup web-backend communication
- [x] Implement authentication
- [x] Implement specialized tools
- [x] Test core functionality

### Phase 2: Deployment & Documentation
- [x] Prepare for deployment
- [ ] Push changes to repository
- [ ] Create documentation

### Future Phases
- Implement Tauri 2.0 integration for desktop application
- Add more specialized tools
- Enhance RAG capabilities
- Implement user workspace management
- Add collaborative features

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
