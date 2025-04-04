"""
Main application module for Atlas-Chat.

This module initializes the FastAPI application and includes all routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import chat, users, models, integration

app = FastAPI(title="Atlas-Chat API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(users.router)
app.include_router(models.router)
app.include_router(integration.router)  # Add integration router

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Atlas-Chat API"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
