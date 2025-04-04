# AtlasChat Deployment Guide

This document provides comprehensive instructions for deploying AtlasChat in a production environment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Docker Deployment](#docker-deployment)
7. [Security Considerations](#security-considerations)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying AtlasChat, ensure you have the following:

- Docker and Docker Compose (recommended deployment method)
- Python 3.10+ (for non-Docker backend deployment)
- Node.js 16+ (for non-Docker frontend deployment)
- PostgreSQL database (Supabase recommended)
- Neo4j database (optional, for knowledge graph features)
- Qdrant vector database (for RAG capabilities)
- E2B API key (for code execution sandbox)
- JWT secret key (for authentication)

## Environment Setup

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```
# Application settings
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://your-frontend-domain.com
JWT_SECRET_KEY=your-secure-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database connections
DATABASE_URL=postgresql://username:password@host:port/database
QDRANT_URL=http://qdrant-host:6333
NEO4J_URI=bolt://neo4j-host:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-neo4j-password

# E2B configuration
E2B_API_KEY=your-e2b-api-key
E2B_WARMUP_ON_STARTUP=true

# Security settings
MAX_CODE_LENGTH=10000
ALLOWED_FILE_DIRECTORIES=workspace,data,temp
BLOCKED_PACKAGES=subprocess,shutil,os
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# Server settings
UVICORN_WORKERS=4
```

### Frontend Environment Variables

Create a `.env.production` file in the frontend directory:

```
NEXT_PUBLIC_BACKEND_URL=https://your-backend-domain.com
```

## Database Configuration

### Supabase Setup

1. Create a new Supabase project
2. Create the required tables using the SQL schema provided in `backend/database_setup.md`
3. Set up row-level security policies for each table
4. Get the PostgreSQL connection string from Supabase dashboard

### Neo4j Setup (Optional)

1. Deploy Neo4j using Docker or a cloud provider
2. Create a new database and user
3. Enable APOC plugin for advanced graph operations
4. Configure the connection in your environment variables

### Qdrant Setup

1. Deploy Qdrant using Docker or a cloud provider
2. No initial configuration is needed; collections will be created automatically

## Backend Deployment

### Using Docker (Recommended)

1. Build the Docker image:
   ```bash
   docker build -t atlaschat-backend -f backend/Dockerfile .
   ```

2. Run the container:
   ```bash
   docker run -d --name atlaschat-backend \
     -p 8000:8000 \
     --env-file backend/.env \
     atlaschat-backend
   ```

### Manual Deployment

1. Create a Python virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```bash
   alembic upgrade head
   ```

4. Start the application:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

## Frontend Deployment

### Using Docker (Recommended)

1. Build the Docker image:
   ```bash
   docker build -t atlaschat-frontend -f frontend/Dockerfile .
   ```

2. Run the container:
   ```bash
   docker run -d --name atlaschat-frontend \
     -p 3000:3000 \
     -e NEXT_PUBLIC_BACKEND_URL=https://your-backend-domain.com \
     atlaschat-frontend
   ```

### Manual Deployment

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Build the application:
   ```bash
   npm run build
   ```

3. Start the production server:
   ```bash
   npm start
   ```

## Docker Deployment

For a complete deployment using Docker Compose:

1. Ensure you have the `.env` file in the project root
2. Run Docker Compose:
   ```bash
   docker-compose up -d
   ```

This will start:
- Backend API
- Frontend application
- Qdrant vector database
- Neo4j database (if enabled)

## Security Considerations

### SSL/TLS

Always use HTTPS in production. Configure your reverse proxy (Nginx, Traefik, etc.) to handle SSL termination.

### API Security

The backend implements several security measures:
- JWT authentication
- Rate limiting
- Input validation
- Password strength enforcement

### E2B Sandbox Security

The E2B sandbox provides isolated code execution. Additional security measures:
- Code validation to prevent dangerous patterns
- File path validation to prevent directory traversal
- Package name validation to block potentially harmful packages

## Monitoring and Logging

### Log Configuration

Logs are written to `logs/app.log` with daily rotation. In production, consider using a centralized logging solution like ELK Stack or Datadog.

### Health Checks

The backend provides a health check endpoint at `/api/ping` that can be used by monitoring tools.

### Metrics

For advanced monitoring, integrate with Prometheus and Grafana using the provided exporters.

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify connection strings in `.env`
   - Check network connectivity and firewall rules
   - Ensure database user has proper permissions

2. **Authentication Issues**
   - Verify JWT_SECRET_KEY is consistent
   - Check token expiration settings

3. **E2B Sandbox Errors**
   - Verify E2B_API_KEY is valid
   - Check E2B service status

4. **Performance Issues**
   - Increase UVICORN_WORKERS for higher concurrency
   - Optimize database queries
   - Consider scaling horizontally

### Getting Help

For additional support, please refer to the project documentation or open an issue on the GitHub repository.
