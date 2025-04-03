from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, chat, agent_definitions, auth, code
from app.core.logging_config import setup_logging

logger = setup_logging()

app = FastAPI(title="AtlasChat Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
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

@app.on_event("startup")
async def startup_event():
    logger.info("AtlasChat backend starting up")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("AtlasChat backend shutting down")
