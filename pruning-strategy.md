# AtlasChat Frontend Pruning Strategy

## Overview

This document outlines the strategy for aggressively pruning the LibreChat frontend to focus on the core functionality needed for AtlasChat. The goal is to remove unnecessary multi-endpoint configurations, direct LLM connection logic, internal API routes, and unused auth methods, while adapting the core components to work with our custom backend.

## Components to Prune

### 1. Multi-Endpoint Configurations

- **Files to Modify/Remove:**
  - `/client/src/data-provider/Endpoints/` - Remove or simplify to only support our custom backend
  - `/client/src/components/Endpoints/` - Remove UI for selecting different endpoints
  - `/client/src/data-provider/mutations.ts` - Remove endpoint-related mutations
  - `/client/src/data-provider/queries.ts` - Remove endpoint-related queries

### 2. Direct LLM Connection Logic

- **Files to Modify/Remove:**
  - `/client/src/data-provider/connection.ts` - Simplify to only connect to our backend
  - Any direct API calls to OpenAI, Anthropic, etc.
  - Remove model selection UI components that aren't relevant to our implementation

### 3. Internal API Routes

- **Files to Modify/Remove:**
  - Simplify API routes to only use our custom backend endpoints
  - Remove any internal routing logic that's not needed

### 4. Auth Methods

- **Files to Modify/Remove:**
  - `/client/src/data-provider/Auth/mutations.ts` - Remove two-factor authentication, backup codes, etc.
  - `/client/src/components/Auth/` - Simplify to only use our JWT-based authentication
  - Retain only basic login/logout functionality

## Refactoring Strategy

### 1. API Layer

- Create a simplified API client that connects to our FastAPI backend
- Replace all existing API calls with our custom implementation
- Use the api-context.tsx we've already created

### 2. Agent Selector Logic

- Modify to work with our agent definitions API
- Remove unnecessary model selection options
- Simplify the UI to focus on our agent types (SDK and LangGraph)

### 3. Auth Flow

- Streamline to use our JWT-based authentication
- Remove complex auth features like 2FA
- Integrate with our backend auth endpoints

## Implementation Plan

1. **Create Backup**: Before making changes, create a backup of the original code
2. **Remove Unnecessary Components**: Delete or comment out the identified components
3. **Refactor Core Components**: Adapt the remaining components to work with our backend
4. **Test Integration**: Ensure the frontend works correctly with our backend
5. **Document Changes**: Update documentation to reflect the simplified architecture

## Specific Tasks

1. **Remove Multi-Endpoint Configurations**

   - Replace endpoint selection with a single connection to our backend
   - Remove model selection UI that isn't relevant

2. **Strip Direct LLM Connection Logic**

   - Remove direct connections to LLM providers
   - Replace with calls to our backend API

3. **Clean Up Internal API Routes**

   - Simplify routing to use our backend endpoints
   - Remove unnecessary internal routes

4. **Simplify Auth Methods**

   - Remove 2FA, backup codes, and other complex auth features
   - Implement simple JWT-based authentication

5. **Integrate with Backend**
   - Ensure all frontend components work with our FastAPI backend
   - Test the integration thoroughly

## Expected Outcome

A streamlined frontend that focuses on the core functionality needed for AtlasChat, without the unnecessary complexity of the original LibreChat implementation. The pruned frontend will work seamlessly with our custom backend and provide a better foundation for future development.
