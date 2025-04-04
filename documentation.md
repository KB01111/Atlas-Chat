# AtlasChat Documentation

## Overview

AtlasChat is a powerful desktop AI assistant built as a fork of LibreChat, featuring a Tauri 2.0 desktop application with enhanced capabilities for code execution, file management, and agent selection. This documentation provides comprehensive information about the application, its features, installation, and usage.

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Usage Guide](#usage-guide)
5. [Code Execution](#code-execution)
6. [Agent Selection](#agent-selection)
7. [File Management](#file-management)
8. [Configuration](#configuration)
9. [Troubleshooting](#troubleshooting)
10. [Recent Improvements](#recent-improvements)

## Features

AtlasChat offers a rich set of features designed to enhance productivity and provide a seamless AI assistant experience:

- **Multiple AI Agents**: Choose from different specialized AI agents for various tasks
- **Secure Code Execution**: Run code in multiple programming languages in a secure sandbox
- **File Management**: Upload, process, and manage files with support for large files
- **Chat Interface**: Intuitive chat interface with support for long conversations
- **Responsive Design**: Works seamlessly across desktop and mobile devices
- **Authentication**: Secure user authentication and session management
- **Customization**: Personalize your experience with themes and settings

## Architecture

AtlasChat follows a modern architecture with clear separation of concerns:

### Backend

- **FastAPI Framework**: High-performance API with async support
- **SQLAlchemy ORM**: Database abstraction and management
- **Alembic**: Database migrations
- **E2B Integration**: Secure code execution sandbox
- **Qdrant Vector Database**: For efficient retrieval augmented generation
- **JWT Authentication**: Secure token-based authentication

### Frontend

- **React**: Component-based UI library
- **Tauri 2.0**: Desktop application framework
- **Monaco Editor**: Code editor with syntax highlighting
- **React Window**: Virtualized rendering for performance
- **CSS Variables**: Comprehensive design system

## Installation

### Prerequisites

- Node.js 20.x or higher
- Python 3.10 or higher
- Docker (for containerized deployment)

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/KB01111/AtlasChat.git
   cd AtlasChat
   ```

2. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```bash
   cd ../frontend
   npm install
   ```

4. Configure environment variables:
   ```bash
   cp backend/.env.example backend/.env
   # Edit .env file with your configuration
   ```

5. Start the development servers:
   ```bash
   # Terminal 1 - Backend
   cd backend
   python main.py

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

### Production Deployment

For production deployment, use Docker Compose:

```bash
docker-compose up -d
```

See the [Deployment Guide](deployment-guide.md) for detailed instructions.

## Usage Guide

### Getting Started

1. **Registration/Login**: Create an account or log in with existing credentials
2. **Select an Agent**: Choose an AI agent from the dropdown menu
3. **Start a Conversation**: Type your message in the input field and press Enter
4. **Use Code Execution**: Click "Show Code Editor" to access the code execution environment
5. **Upload Files**: Use the file upload button to share files with the AI

### Chat Interface

The chat interface supports:

- Text messages with markdown formatting
- Code blocks with syntax highlighting
- Image display with smooth loading
- File attachments
- Long conversation history with efficient scrolling

## Code Execution

AtlasChat provides a powerful code execution environment:

### Supported Languages

- Python
- JavaScript
- TypeScript
- Bash

### Features

- Syntax highlighting
- Code completion
- Package installation
- File operations (read/write)
- Progressive loading for large files
- Output display with error handling

### Security

Code execution happens in a secure sandbox environment using E2B integration, with:

- Resource limitations
- Network isolation
- Filesystem restrictions
- Execution timeouts

## Agent Selection

AtlasChat offers multiple specialized AI agents:

- **General Assistant**: All-purpose AI assistant
- **Code Specialist**: Focused on programming and development
- **Research Assistant**: Optimized for information gathering and analysis
- **Creative Writer**: Specialized in creative content generation

Each agent has specific capabilities and optimizations for different tasks.

## File Management

### Supported File Types

- Text files (.txt, .md, .csv, etc.)
- Code files (.py, .js, .html, etc.)
- Images (.jpg, .png, .gif, etc.)
- Documents (.pdf, .docx, etc.)

### Features

- Chunked uploads for large files
- Progress tracking
- Document processing with Unstructured library
- Secure storage and management

## Configuration

AtlasChat can be configured through environment variables:

### Backend Configuration

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT secret key
- `OPENAI_API_KEY`: OpenAI API key (if using OpenAI models)
- `E2B_API_KEY`: E2B API key for code execution
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Frontend Configuration

- `VITE_API_URL`: Backend API URL
- `VITE_DEFAULT_AGENT`: Default agent ID
- `VITE_ENABLE_HISTORY`: Enable/disable conversation history

## Troubleshooting

### Common Issues

1. **Connection Issues**
   - Check if the backend server is running
   - Verify network connectivity
   - Ensure correct API URL configuration

2. **Authentication Problems**
   - Clear browser cookies and local storage
   - Reset password if necessary
   - Check for token expiration

3. **Code Execution Failures**
   - Verify package installation
   - Check for syntax errors
   - Ensure code doesn't exceed resource limits

4. **File Upload Issues**
   - Check file size limits
   - Ensure supported file format
   - Verify network stability for large uploads

## Recent Improvements

AtlasChat has recently undergone significant improvements:

### Performance Enhancements

- **Chunked File Upload System**: Reliable handling of large files with progress tracking
- **Virtualized Chat Rendering**: Optimized performance for long conversations
- **Progressive Code File Loading**: Smooth handling of large code files

### UI Improvements

- **Comprehensive Design System**: Consistent styling with CSS variables
- **Responsive Design**: Optimized for all screen sizes
- **Accessibility Enhancements**: Improved keyboard navigation and screen reader support
- **Image Loading Improvements**: Smooth transitions and placeholders

### Functionality Upgrades

- **Enhanced Package Installation**: Background processing and extended timeouts
- **Agent Selection Debounce**: Prevented UI flicker during rapid switching
- **Code Editor Focus Management**: Maintained focus after operations
- **Unstructured Library Integration**: Improved document processing capabilities

For a detailed list of all improvements, see the [Improvements Documentation](improvements-documentation.md).

---

© 2025 AtlasChat. All rights reserved.
