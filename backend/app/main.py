"""
Main application module for Atlas-Chat.

This module initializes the FastAPI application and includes all routers.
"""
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://8fefa654965adb4e179f35821b7d1dad@o4508916501970944.ingest.de.sentry.io/4509118163451984",
    integrations=[FastApiIntegration()],
    send_default_pii=True,
    traces_sample_rate=1.0,
    profile_session_sample_rate=1.0,
    profile_lifecycle="trace",
)


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import chat, integration, models, users
import logging

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
    logging.getLogger("atlaschat").info("Health check endpoint called")
    return {"status": "healthy"}


@app.get("/sentry-debug")
async def trigger_error():
    """Endpoint to trigger an error for Sentry testing"""
    1 / 0  # This will raise ZeroDivisionError
