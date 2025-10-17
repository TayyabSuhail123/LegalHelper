"""File upload and processing API endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.file_processing import (
    FileUploadResponse,
    ProcessingStatus,
    ProcessingProgress,
    UploadedFile
)
from app.core.dependencies import FileProcessingServiceDep

# Create router
router = APIRouter()

# In-memory storage for demo (replace with database in production)
uploaded_files: Dict[str, UploadedFile] = {}


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Contract file to upload (PDF, DOCX, TXT)"),
    file_service: FileProcessingServiceDep = None
) -> FileUploadResponse:
    """
    Upload a contract file for processing.
    
    Supports PDF, DOCX, and TXT files up to 50MB.
    Returns immediately with file_id for tracking processing status.
    """
    try:
        # Process file
        uploaded_file = await file_service.process_file(file)
        
        # Store in memory (replace with database)
        uploaded_files[uploaded_file.file_id] = uploaded_file
        
        return FileUploadResponse(
            success=True,
            message="File uploaded and processed successfully",
            file_id=uploaded_file.file_id,
            processing_status=uploaded_file.processing_status,
            estimated_processing_time=None  # Immediate processing for now
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the actual error for debugging but don't expose it to users
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error during file upload: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your file. Please try again."
        )


@router.get("/status/{file_id}", response_model=ProcessingProgress)
async def get_processing_status(file_id: str) -> ProcessingProgress:
    """
    Get processing status for an uploaded file.
    
    Args:
        file_id: Unique identifier for the uploaded file
        
    Returns:
        Current processing status and progress information
    """
    if file_id not in uploaded_files:
        raise HTTPException(
            status_code=404,
            detail=f"File with ID {file_id} not found"
        )
    
    uploaded_file = uploaded_files[file_id]
    
    # Determine progress percentage based on status
    progress_map = {
        ProcessingStatus.UPLOADED: 10.0,
        ProcessingStatus.PROCESSING: 50.0,
        ProcessingStatus.COMPLETED: 100.0,
        ProcessingStatus.FAILED: 0.0,
    }
    
    # Determine current step based on status
    step_map = {
        ProcessingStatus.UPLOADED: "File uploaded, queued for processing",
        ProcessingStatus.PROCESSING: "Extracting text from document",
        ProcessingStatus.COMPLETED: "Processing completed successfully",
        ProcessingStatus.FAILED: "Processing failed",
    }
    
    return ProcessingProgress(
        file_id=file_id,
        status=uploaded_file.processing_status,
        progress_percentage=progress_map[uploaded_file.processing_status],
        current_step=step_map[uploaded_file.processing_status],
        estimated_time_remaining=None,
        error_message=uploaded_file.error_message
    )


@router.get("/files/{file_id}", response_model=UploadedFile)
async def get_file_details(file_id: str) -> UploadedFile:
    """
    Get detailed information about an uploaded file.
    
    Args:
        file_id: Unique identifier for the uploaded file
        
    Returns:
        Complete file information including extracted text
    """
    if file_id not in uploaded_files:
        raise HTTPException(
            status_code=404,
            detail=f"File with ID {file_id} not found"
        )
    
    return uploaded_files[file_id]


@router.get("/files", response_model=Dict[str, Any])
async def list_uploaded_files(
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    List all uploaded files with pagination.
    
    Args:
        limit: Maximum number of files to return (default: 50)
        offset: Number of files to skip (default: 0)
        
    Returns:
        List of uploaded files with pagination info
    """
    all_files = list(uploaded_files.values())
    total_count = len(all_files)
    
    # Apply pagination
    paginated_files = all_files[offset:offset + limit]
    
    return {
        "files": [
            {
                "file_id": f.file_id,
                "filename": f.filename,
                "file_type": f.file_type,
                "file_size": f.file_size,
                "upload_timestamp": f.upload_timestamp,
                "processing_status": f.processing_status,
                "has_extracted_text": bool(f.extracted_text),
                "has_error": bool(f.error_message)
            }
            for f in paginated_files
        ],
        "pagination": {
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_next": offset + limit < total_count,
            "has_previous": offset > 0
        }
    }


@router.delete("/files/{file_id}")
async def delete_file(file_id: str) -> JSONResponse:
    """
    Delete an uploaded file and its data.
    
    Args:
        file_id: Unique identifier for the uploaded file
        
    Returns:
        Success confirmation
    """
    if file_id not in uploaded_files:
        raise HTTPException(
            status_code=404,
            detail=f"File with ID {file_id} not found"
        )
    
    # Remove from storage
    del uploaded_files[file_id]
    
    return JSONResponse(
        content={
            "success": True,
            "message": f"File {file_id} deleted successfully"
        }
    )


@router.get("/supported-formats")
async def get_supported_formats(
    file_service: FileProcessingServiceDep = None
) -> Dict[str, Any]:
    """
    Get information about supported file formats.
    
    Returns:
        Supported file formats and their specifications
    """
    return {
        "supported_formats": [
            {
                "type": "PDF",
                "extensions": [".pdf"],
                "mime_type": "application/pdf",
                "description": "Portable Document Format files"
            },
            {
                "type": "DOCX",
                "extensions": [".docx"],
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "description": "Microsoft Word documents"
            },
            {
                "type": "TXT",
                "extensions": [".txt"],
                "mime_type": "text/plain",
                "description": "Plain text files"
            }
        ],
        "max_file_size": f"{file_service.max_file_size / (1024 * 1024):.0f} MB",
        "max_file_size_bytes": file_service.max_file_size
    }


@router.get("/storage/stats")
async def get_storage_stats(
    file_service: FileProcessingServiceDep = None
) -> Dict[str, Any]:
    """
    Get storage statistics.
    
    Returns:
        Current storage usage and statistics
    """
    stats = await file_service.storage_manager.get_storage_stats()
    return {
        "storage_stats": stats,
        "cleanup_enabled": True,
        "cleanup_interval_hours": file_service.storage_manager.cleanup_interval / 3600
    }
