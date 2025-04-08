import os

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import agent_definitions, auth, chat, code, health, integration, upload
from app.core.logging_config import setup_logging

logger = setup_logging()


# Sentry SDK initialization moved to startup_event

app = FastAPI(title="AtlasChat Backend")


@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(agent_definitions.router)
app.include_router(auth.router)
app.include_router(code.router)  # Add the code execution router
app.include_router(upload.router)
app.include_router(integration.router)


@app.on_event("startup")
async def startup_event():
    logger.info("AtlasChat backend starting up")
    # Initialize Sentry SDK here for async compatibility
    sentry_sdk.init(
        dsn="https://564d495992853763135956f1cda59187@o4508916501970944.ingest.de.sentry.io/4509068803178576",
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        # Enable PII data collection (be careful with GDPR/privacy regulations)
        send_default_pii=True,
        # Enable profiling
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )
    logger.info("Sentry SDK initialized.")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("AtlasChat backend shutting down")
