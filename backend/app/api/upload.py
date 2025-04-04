from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
import os
import uuid
import shutil
from datetime import datetime
import logging
from app.core.security import get_current_user
from app.core.config import settings
from unstructured.partition.auto import partition

router = APIRouter()

# Store upload sessions in memory (in production, use Redis or another persistent store)
upload_sessions = {}

# Configure upload directory
UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "uploads")
CHUNK_DIR = os.path.join(UPLOAD_DIR, "chunks")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHUNK_DIR, exist_ok=True)

@router.post("/upload/init")
async def initialize_upload(
    background_tasks: BackgroundTasks,
    filename: str,
    fileSize: int,
    fileType: str,
    totalChunks: int,
    metadata: Optional[Dict] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Initialize a chunked file upload session"""
    try:
        # Generate unique upload ID
        upload_id = str(uuid.uuid4())
        
        # Create session directory for chunks
        session_dir = os.path.join(CHUNK_DIR, upload_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Store session info
        upload_sessions[upload_id] = {
            "user_id": current_user["user_id"],
            "filename": filename,
            "file_size": fileSize,
            "file_type": fileType,
            "total_chunks": totalChunks,
            "uploaded_chunks": 0,
            "chunk_files": [],
            "session_dir": session_dir,
            "metadata": metadata or {},
            "status": "initialized",
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": None  # Set expiration in production
        }
        
        # Set up automatic cleanup after 24 hours in production
        # background_tasks.add_task(cleanup_expired_session, upload_id)
        
        return {"uploadId": upload_id, "status": "initialized"}
    
    except Exception as e:
        logging.error(f"Error initializing upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize upload: {str(e)}")

@router.post("/upload/chunk")
async def upload_chunk(
    uploadId: str = Form(...),
    chunkIndex: int = Form(...),
    chunk: UploadFile = File(...)
):
    """Upload a single chunk of a file"""
    try:
        # Validate upload session
        if uploadId not in upload_sessions:
            raise HTTPException(status_code=404, detail="Upload session not found")
        
        session = upload_sessions[uploadId]
        
        # Validate chunk index
        if chunkIndex < 0 or chunkIndex >= session["total_chunks"]:
            raise HTTPException(status_code=400, detail="Invalid chunk index")
        
        # Save chunk to session directory
        chunk_filename = f"{chunkIndex}.chunk"
        chunk_path = os.path.join(session["session_dir"], chunk_filename)
        
        with open(chunk_path, "wb") as f:
            shutil.copyfileobj(chunk.file, f)
        
        # Update session info
        session["chunk_files"].append(chunk_path)
        session["uploaded_chunks"] += 1
        
        return {
            "uploadId": uploadId,
            "chunkIndex": chunkIndex,
            "received": True,
            "progress": {
                "uploaded": session["uploaded_chunks"],
                "total": session["total_chunks"],
                "percentage": round((session["uploaded_chunks"] / session["total_chunks"]) * 100)
            }
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logging.error(f"Error uploading chunk: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload chunk: {str(e)}")

@router.post("/upload/complete")
async def complete_upload(
    uploadId: str,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """Complete a chunked file upload by combining chunks"""
    try:
        # Validate upload session
        if uploadId not in upload_sessions:
            raise HTTPException(status_code=404, detail="Upload session not found")
        
        session = upload_sessions[uploadId]
        
        # Validate user
        if session["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized to complete this upload")
        
        # Validate all chunks are uploaded
        if session["uploaded_chunks"] != session["total_chunks"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Upload incomplete. Expected {session['total_chunks']} chunks, got {session['uploaded_chunks']}"
            )
        
        # Combine chunks into final file
        output_filename = session["filename"]
        output_path = os.path.join(UPLOAD_DIR, f"{uploadId}_{output_filename}")
        
        with open(output_path, "wb") as output_file:
            # Sort chunks by index (extracted from filename)
            sorted_chunks = sorted(
                session["chunk_files"],
                key=lambda x: int(os.path.basename(x).split('.')[0])
            )
            
            # Combine chunks
            for chunk_path in sorted_chunks:
                with open(chunk_path, "rb") as chunk_file:
                    shutil.copyfileobj(chunk_file, output_file)
        
        # Update session status
        session["status"] = "completed"
        session["output_path"] = output_path
        
        # Process file with Unstructured if appropriate
        file_elements = None
        if session["file_type"] in ["application/pdf", "text/plain", "text/html"]:
            try:
                # Process file with Unstructured in background
                background_tasks.add_task(process_file_with_unstructured, output_path, uploadId)
            except Exception as e:
                logging.error(f"Error processing file with Unstructured: {str(e)}")
                # Continue even if processing fails
        
        # Clean up chunks in background
        background_tasks.add_task(cleanup_chunks, session["session_dir"])
        
        return {
            "uploadId": uploadId,
            "filename": output_filename,
            "fileSize": session["file_size"],
            "fileType": session["file_type"],
            "status": "completed",
            "processingStatus": "pending" if file_elements is None else "completed"
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logging.error(f"Error completing upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to complete upload: {str(e)}")

@router.post("/upload/abort")
async def abort_upload(
    uploadId: str,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """Abort an in-progress upload and clean up resources"""
    try:
        # Validate upload session
        if uploadId not in upload_sessions:
            raise HTTPException(status_code=404, detail="Upload session not found")
        
        session = upload_sessions[uploadId]
        
        # Validate user
        if session["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized to abort this upload")
        
        # Update session status
        session["status"] = "aborted"
        
        # Clean up chunks in background
        background_tasks.add_task(cleanup_chunks, session["session_dir"])
        
        return {"uploadId": uploadId, "status": "aborted"}
    
    except HTTPException:
        raise
    
    except Exception as e:
        logging.error(f"Error aborting upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to abort upload: {str(e)}")

@router.get("/upload/status/{uploadId}")
async def get_upload_status(
    uploadId: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get the status of an upload session"""
    try:
        # Validate upload session
        if uploadId not in upload_sessions:
            raise HTTPException(status_code=404, detail="Upload session not found")
        
        session = upload_sessions[uploadId]
        
        # Validate user
        if session["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized to view this upload")
        
        return {
            "uploadId": uploadId,
            "filename": session["filename"],
            "fileSize": session["file_size"],
            "fileType": session["file_type"],
            "status": session["status"],
            "progress": {
                "uploaded": session["uploaded_chunks"],
                "total": session["total_chunks"],
                "percentage": round((session["uploaded_chunks"] / session["total_chunks"]) * 100)
            }
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logging.error(f"Error getting upload status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get upload status: {str(e)}")

# Background tasks

def cleanup_chunks(session_dir: str):
    """Clean up chunk files after successful upload"""
    try:
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)
    except Exception as e:
        logging.error(f"Error cleaning up chunks: {str(e)}")

def process_file_with_unstructured(file_path: str, upload_id: str):
    """Process uploaded file with Unstructured library"""
    try:
        # Skip processing if file doesn't exist
        if not os.path.exists(file_path):
            logging.error(f"File not found for processing: {file_path}")
            return
        
        # Process file with Unstructured
        elements = partition(filename=file_path)
        
        # Store processing results
        if upload_id in upload_sessions:
            upload_sessions[upload_id]["processing_results"] = {
                "element_count": len(elements),
                "element_types": [type(el).__name__ for el in elements],
                "processed_at": datetime.utcnow().isoformat()
            }
            upload_sessions[upload_id]["processing_status"] = "completed"
        
        logging.info(f"Successfully processed file with Unstructured: {file_path}")
    except Exception as e:
        logging.error(f"Error processing file with Unstructured: {str(e)}")
        if upload_id in upload_sessions:
            upload_sessions[upload_id]["processing_status"] = "failed"
            upload_sessions[upload_id]["processing_error"] = str(e)
