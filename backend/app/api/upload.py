import json
import logging
import os
import shutil
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import aioredis
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from pydantic import BaseModel
from unstructured.partition.auto import partition

from app.core.config import settings  # Assuming settings loads env vars
from app.core.security import get_current_user

router = APIRouter(prefix="/upload", tags=["upload"])

# Configure upload directory
UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "uploads")
CHUNK_DIR = os.path.join(UPLOAD_DIR, "chunks")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHUNK_DIR, exist_ok=True)

# Redis Session TTL (e.g., 24 hours)
SESSION_TTL_SECONDS = int(timedelta(hours=24).total_seconds())


# --- Redis Connection ---
async def get_redis(request: Request) -> aioredis.Redis:
    """FastAPI dependency to get Redis connection pool."""
    # Store pool on app state to reuse connection
    if not hasattr(request.app.state, "redis_pool") or request.app.state.redis_pool is None:
        try:
            request.app.state.redis_pool = aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                password=settings.REDIS_PASSWORD,
                encoding="utf-8",
                decode_responses=True,  # Decode responses to strings
            )
            # Test connection
            await request.app.state.redis_pool.ping()
            logging.info("Redis connection established.")
        except Exception as e:
            logging.error(f"Failed to connect to Redis: {e}")
            request.app.state.redis_pool = None  # Ensure it's None if connection fails
            raise HTTPException(status_code=503, detail="Could not connect to Redis service.")
    # Check if pool was successfully created on retry
    if request.app.state.redis_pool is None:
        raise HTTPException(status_code=503, detail="Redis service unavailable.")

    return request.app.state.redis_pool


# --- Helper Functions ---
def get_session_key(upload_id: str) -> str:
    """Generates the Redis key for an upload session."""
    return f"upload_session:{upload_id}"


async def get_session_data(redis: aioredis.Redis, upload_id: str) -> Optional[Dict]:
    """Retrieves and deserializes session data from Redis."""
    session_key = get_session_key(upload_id)
    data_json = await redis.get(session_key)
    if data_json:
        return json.loads(data_json)
    return None


async def save_session_data(
    redis: aioredis.Redis,
    upload_id: str,
    data: Dict,
    expire: Optional[int] = SESSION_TTL_SECONDS,
):
    """Serializes and saves session data to Redis with optional TTL."""
    session_key = get_session_key(upload_id)
    await redis.set(session_key, json.dumps(data), ex=expire)


# --- Pydantic Models (Optional, for clarity) ---
class UploadSessionData(BaseModel):
    user_id: str
    filename: str
    file_size: int
    file_type: str
    total_chunks: int
    uploaded_chunks: int
    chunk_files: List[str]  # Store paths relative to CHUNK_DIR? No, store full path for now.
    session_dir: str
    metadata: Dict
    status: str  # initialized, uploading, completed, aborted, failed
    created_at: str
    output_path: Optional[str] = None
    processing_status: Optional[str] = None  # pending, completed, failed
    processing_error: Optional[str] = None
    processing_results: Optional[Dict] = None


# --- API Endpoints ---


@router.post("/init")
async def initialize_upload(
    background_tasks: BackgroundTasks,
    filename: str = Form(...),
    fileSize: int = Form(...),
    fileType: str = Form(...),
    totalChunks: int = Form(...),
    metadata: Optional[str] = Form(None),  # Receive metadata as JSON string
    current_user: Dict = Depends(get_current_user),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Initialize a chunked file upload session"""
    try:
        upload_id = str(uuid.uuid4())
        session_dir = os.path.join(CHUNK_DIR, upload_id)
        os.makedirs(session_dir, exist_ok=True)

        parsed_metadata = {}
        if metadata:
            try:
                parsed_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid metadata format (must be JSON string)",
                )

        session_data = UploadSessionData(
            user_id=current_user["user_id"],
            filename=filename,  # Consider sanitizing filename
            file_size=fileSize,
            file_type=fileType,
            total_chunks=totalChunks,
            uploaded_chunks=0,
            chunk_files=[],
            session_dir=session_dir,
            metadata=parsed_metadata,
            status="initialized",
            created_at=datetime.utcnow().isoformat(),
        )

        await save_session_data(redis, upload_id, session_data.dict())

        return {"uploadId": upload_id, "status": "initialized"}

    except HTTPException:  # Re-raise HTTPExceptions directly
        raise
    except aioredis.RedisError as e:
        logging.error(f"Redis error initializing upload: {e}", exc_info=True)
        raise HTTPException(
            status_code=503, detail="Upload service dependency unavailable (Redis)."
        )
    except Exception as e:
        logging.error(f"Error initializing upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize upload: {str(e)}")


@router.post("/chunk")
async def upload_chunk(
    uploadId: str = Form(...),
    chunkIndex: int = Form(...),
    chunk: UploadFile = File(...),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Upload a single chunk of a file"""
    try:
        session_data_dict = await get_session_data(redis, uploadId)
        if not session_data_dict:
            raise HTTPException(status_code=404, detail="Upload session not found or expired")

        session = UploadSessionData(**session_data_dict)

        if session.status not in ["initialized", "uploading"]:
            raise HTTPException(
                status_code=400,
                detail=f"Upload session status is '{session.status}', cannot upload chunks.",
            )

        if chunkIndex < 0 or chunkIndex >= session.total_chunks:
            raise HTTPException(status_code=400, detail="Invalid chunk index")

        # Check if chunk already uploaded (simple check based on count)
        # More robust check could involve checking redis list/set of uploaded indices
        if chunkIndex in [int(os.path.basename(p).split(".")[0]) for p in session.chunk_files]:
            logging.warning(f"Chunk {chunkIndex} for upload {uploadId} already uploaded. Skipping.")
            # Return current progress instead of error?
            return {
                "uploadId": uploadId,
                "chunkIndex": chunkIndex,
                "received": True,  # Indicate it was received (even if duplicate)
                "status": "duplicate",
                "progress": {
                    "uploaded": session.uploaded_chunks,
                    "total": session.total_chunks,
                    "percentage": (
                        round((session.uploaded_chunks / session.total_chunks) * 100)
                        if session.total_chunks > 0
                        else 0
                    ),
                },
            }

        chunk_filename = f"{chunkIndex}.chunk"
        chunk_path = os.path.join(session.session_dir, chunk_filename)

        try:
            with open(chunk_path, "wb") as f:
                shutil.copyfileobj(chunk.file, f)
        except Exception as e:
            logging.error(f"Failed to save chunk {chunkIndex} for upload {uploadId}: {e}")
            raise HTTPException(status_code=500, detail="Failed to save file chunk")
        finally:
            await chunk.close()  # Ensure file handle is closed

        session.chunk_files.append(chunk_path)
        session.uploaded_chunks += 1
        session.status = "uploading"

        await save_session_data(redis, uploadId, session.dict())

        return {
            "uploadId": uploadId,
            "chunkIndex": chunkIndex,
            "received": True,
            "status": "success",
            "progress": {
                "uploaded": session.uploaded_chunks,
                "total": session.total_chunks,
                "percentage": (
                    round((session.uploaded_chunks / session.total_chunks) * 100)
                    if session.total_chunks > 0
                    else 0
                ),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error uploading chunk for {uploadId}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload chunk: {str(e)}")


@router.post("/complete")
async def complete_upload(
    background_tasks: BackgroundTasks,
    uploadId: str = Form(...),
    current_user: Dict = Depends(get_current_user),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Complete a chunked file upload by combining chunks"""
    session_data_dict = await get_session_data(redis, uploadId)
    if not session_data_dict:
        raise HTTPException(status_code=404, detail="Upload session not found or expired")

    session = UploadSessionData(**session_data_dict)

    try:
        if session.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized to complete this upload")

        if session.status == "completed":
            logging.warning(f"Upload {uploadId} already completed.")
            return {
                "uploadId": uploadId,
                "filename": session.filename,
                "fileSize": session.file_size,
                "fileType": session.file_type,
                "status": "completed",  # Already completed
                "processingStatus": session.processing_status or "unknown",
            }

        if session.status not in ["initialized", "uploading"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot complete upload with status '{session.status}'",
            )

        if session.uploaded_chunks != session.total_chunks:
            raise HTTPException(
                status_code=400,
                detail=f"Upload incomplete. Expected {session.total_chunks} chunks, got {session.uploaded_chunks}",
            )

        # Sanitize filename before joining path
        # Basic sanitization: remove path separators
        safe_filename = os.path.basename(session.filename)
        output_filename = f"{uploadId}_{safe_filename}"
        output_path = os.path.join(UPLOAD_DIR, output_filename)

        # Combine chunks
        sorted_chunks = sorted(
            session.chunk_files,
            key=lambda x: int(os.path.basename(x).split(".")[0]),
        )

        with open(output_path, "wb") as output_file:
            for chunk_path in sorted_chunks:
                try:
                    with open(chunk_path, "rb") as chunk_file:
                        shutil.copyfileobj(chunk_file, output_file)
                except FileNotFoundError:
                    logging.error(f"Chunk file not found during completion: {chunk_path}")
                    session.status = "failed"
                    await save_session_data(
                        redis, uploadId, session.dict(), expire=SESSION_TTL_SECONDS
                    )  # Keep session info for debugging
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to combine chunks: missing chunk file.",
                    )
                except Exception as e:
                    logging.error(f"Error combining chunk {chunk_path}: {e}")
                    session.status = "failed"
                    await save_session_data(
                        redis, uploadId, session.dict(), expire=SESSION_TTL_SECONDS
                    )
                    raise HTTPException(status_code=500, detail="Failed to combine chunks.")

        session.status = "completed"
        session.output_path = output_path

        # Process file with Unstructured if appropriate
        session.processing_status = "not_applicable"
        if session.file_type in [
            "application/pdf",
            "text/plain",
            "text/html",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]:
            session.processing_status = "pending"
            background_tasks.add_task(process_file_with_unstructured, output_path, uploadId, redis)

        # Save final completed state (keep TTL for now)
        await save_session_data(redis, uploadId, session.dict())

        # Clean up chunks in background
        background_tasks.add_task(cleanup_chunks, session.session_dir)

        return {
            "uploadId": uploadId,
            "filename": session.filename,  # Return original filename
            "fileSize": session.file_size,
            "fileType": session.file_type,
            "status": "completed",
            "processingStatus": session.processing_status,
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error completing upload {uploadId}: {str(e)}")
        # Update status to failed in Redis if possible
        try:
            session.status = "failed"
            await save_session_data(redis, uploadId, session.dict(), expire=SESSION_TTL_SECONDS)
        except Exception as redis_e:
            logging.error(
                f"Failed to update upload {uploadId} status to failed in Redis: {redis_e}"
            )

        raise HTTPException(status_code=500, detail=f"Failed to complete upload: {str(e)}")


@router.post("/abort")
async def abort_upload(
    background_tasks: BackgroundTasks,
    uploadId: str = Form(...),
    current_user: Dict = Depends(get_current_user),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Abort an in-progress upload and clean up resources"""
    session_data_dict = await get_session_data(redis, uploadId)
    if not session_data_dict:
        # If session doesn't exist, maybe it expired or was already cleaned up. Return success.
        logging.warning(f"Attempted to abort non-existent or expired upload session: {uploadId}")
        return {"uploadId": uploadId, "status": "aborted (or expired)"}

    session = UploadSessionData(**session_data_dict)

    try:
        if session.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized to abort this upload")

        # Clean up chunks regardless of current status if abort is requested
        background_tasks.add_task(cleanup_chunks, session.session_dir)

        # Delete session from Redis
        await redis.delete(get_session_key(uploadId))

        return {"uploadId": uploadId, "status": "aborted"}

    except HTTPException:  # Re-raise HTTPExceptions directly
        raise
    except aioredis.RedisError as e:
        logging.error(f"Redis error during upload abort for {uploadId}: {e}", exc_info=True)
        # Still try to return success-like response if session is gone, but log the Redis error
        # If Redis fails during delete, the key might remain until TTL expires.
        raise HTTPException(
            status_code=503,
            detail="Upload service dependency unavailable (Redis). Could not guarantee session removal.",
        )
    except Exception as e:
        logging.error(f"Error aborting upload {uploadId}: {e}", exc_info=True)  # Log full traceback
        # Return generic 500 error
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while aborting the upload.",
        )


@router.get("/status/{uploadId}")
async def get_upload_status(
    uploadId: str,
    current_user: Dict = Depends(get_current_user),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Get the status of an upload session"""
    try:
        session_data_dict = await get_session_data(redis, uploadId)
        if not session_data_dict:
            raise HTTPException(status_code=404, detail="Upload session not found or expired")

        session = UploadSessionData(**session_data_dict)

        if session.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized to view this upload")

        return {
            "uploadId": uploadId,
            "filename": session.filename,
            "fileSize": session.file_size,
            "fileType": session.file_type,
            "status": session.status,
            "progress": {
                "uploaded": session.uploaded_chunks,
                "total": session.total_chunks,
                "percentage": (
                    round((session.uploaded_chunks / session.total_chunks) * 100)
                    if session.total_chunks > 0
                    else 0
                ),
            },
            "processingStatus": session.processing_status,
            "processingError": session.processing_error,
            # Avoid sending full processing results here, maybe a summary?
            "metadata": session.metadata,
            "createdAt": session.created_at,
        }

    except HTTPException:  # Re-raise HTTPExceptions directly
        raise
    except aioredis.RedisError as e:
        logging.error(f"Redis error getting upload status for {uploadId}: {e}", exc_info=True)
        raise HTTPException(
            status_code=503, detail="Upload service dependency unavailable (Redis)."
        )
    except Exception as e:
        logging.error(
            f"Error getting upload status for {uploadId}: {e}", exc_info=True
        )  # Log full traceback
        # Return generic 500 error
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while retrieving upload status.",
        )


# --- Background Tasks ---


def cleanup_chunks(session_dir: str):
    """Clean up chunk files (run in background)."""
    try:
        if os.path.exists(session_dir) and os.path.isdir(session_dir):
            shutil.rmtree(session_dir)
            logging.info(f"Cleaned up chunk directory: {session_dir}")
        else:
            logging.warning(f"Chunk directory not found for cleanup: {session_dir}")
    except Exception as e:
        logging.error(f"Error cleaning up chunks in {session_dir}: {str(e)}")


async def process_file_with_unstructured(file_path: str, upload_id: str, redis: aioredis.Redis):
    """Process uploaded file with Unstructured library (run in background)."""
    session_data_dict = await get_session_data(redis, upload_id)
    if not session_data_dict:
        logging.error(f"Upload session {upload_id} not found for Unstructured processing.")
        return

    session = UploadSessionData(**session_data_dict)
    processing_status = "failed"
    error_message = None
    results = None

    try:
        if not os.path.exists(file_path):
            error_message = f"File not found for processing: {file_path}"
            logging.error(error_message)
        else:
            logging.info(
                f"Starting Unstructured processing for: {file_path} (Upload ID: {upload_id})"
            )
            # Use unstructured partition function
            elements = partition(filename=file_path)
            results = {
                "element_count": len(elements),
                # Optionally include element types or a sample if needed, avoid storing large elements
                # "element_types": list(set(type(el).__name__ for el in elements)),
                "processed_at": datetime.utcnow().isoformat(),
            }
            processing_status = "completed"
            logging.info(f"Successfully processed file with Unstructured: {file_path}")

    except Exception as e:
        error_message = f"Error processing file {file_path} with Unstructured: {str(e)}"
        logging.error(error_message)
        processing_status = "failed"

    # Update session in Redis
    try:
        # Re-fetch session data in case it was modified concurrently (less likely for background task)
        current_session_data_dict = await get_session_data(redis, upload_id)
        if current_session_data_dict:
            current_session = UploadSessionData(**current_session_data_dict)
            current_session.processing_status = processing_status
            current_session.processing_error = error_message
            current_session.processing_results = results
            # Save back, preserving original TTL if possible, otherwise reset
            await save_session_data(
                redis, upload_id, current_session.dict(), expire=SESSION_TTL_SECONDS
            )
        else:
            logging.warning(
                f"Session {upload_id} disappeared before Unstructured results could be saved."
            )

    except Exception as redis_e:
        logging.error(
            f"Failed to save Unstructured processing status for {upload_id} to Redis: {redis_e}"
        )


# --- Add Redis shutdown logic to main app ---
# This should ideally be in main.py's shutdown event
async def close_redis_pool(app_state):
    if hasattr(app_state, "redis_pool") and app_state.redis_pool:
        logging.info("Closing Redis connection pool.")
        await app_state.redis_pool.close()
        # await app_state.redis_pool.wait_closed() # Optional: wait for pool to close
        app_state.redis_pool = None


# Example of how to integrate into main.py:
# @app.on_event("startup")
# async def startup_event():
#     logger.info("AtlasChat backend starting up")
#     # Initialize Redis pool on startup (optional, can be lazy loaded by dependency)
#     # try:
#     #     app.state.redis_pool = aioredis.from_url(...)
#     #     await app.state.redis_pool.ping()
#     # except Exception as e:
#     #     logger.error(f"Failed to connect to Redis on startup: {e}")
#     #     app.state.redis_pool = None


# @app.on_event("shutdown")
# async def shutdown_event():
#     logger.info("AtlasChat backend shutting down")
#     await close_redis_pool(app.state)
