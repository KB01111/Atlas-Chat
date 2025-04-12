import os

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import agent_definitions, auth, chat, code, health, integration, upload
from app.core.logging_config import setup_logging

logger = setup_logging()


# Sentry SDK initialization moved to startup_event

app = FastAPI(
    title="AtlasChat Backend",
    docs_url=None if os.getenv("ENVIRONMENT") == "production" else "/docs",
    redoc_url=None if os.getenv("ENVIRONMENT") == "production" else "/redoc",
    openapi_url=None if os.getenv("ENVIRONMENT") == "production" else "/openapi.json",
)


if os.getenv("ENVIRONMENT") != "production":
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
    # Initialize Sentry SDK only if DSN is provided
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        try:
            sentry_sdk.init(
                dsn=sentry_dsn,
                traces_sample_rate=1.0,
                send_default_pii=True,
                profiles_sample_rate=1.0,
            )
            logger.info("Sentry SDK initialized.")
        except sentry_sdk.utils.BadDsn:
            logger.warning("Invalid SENTRY_DSN provided. Sentry integration disabled.")
    else:
        logger.info("SENTRY_DSN not found. Sentry integration disabled.")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("AtlasChat backend shutting down")
