"""File upload and processing API endpoints."""

import logging
import traceback
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
from app.core.document_analysis_service import DocumentAnalysisService

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# In-memory storage for demo (replace with database in production)
uploaded_files: Dict[str, UploadedFile] = {}

# Document analysis service instance
analysis_service: DocumentAnalysisService = None


def get_analysis_service(file_service: FileProcessingServiceDep) -> DocumentAnalysisService:
    """Get or create document analysis service."""
    global analysis_service
    if analysis_service is None:
        analysis_service = DocumentAnalysisService(file_service)
    return analysis_service


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
        logger.info(f"Starting file upload for: {file.filename}")
        logger.debug(f"File size: {file.size if hasattr(file, 'size') else 'unknown'}")
        logger.debug(f"File content type: {file.content_type}")
        
        # Process file (basic upload and storage)
        uploaded_file = await file_service.process_file(file)
        
        logger.info(f"File upload successful - File ID: {uploaded_file.file_id}")
        
        # Store in memory (replace with database)
        uploaded_files[uploaded_file.file_id] = uploaded_file
        
        return FileUploadResponse(
            success=True,
            message="File uploaded successfully",
            file_id=uploaded_file.file_id,
            processing_status=uploaded_file.processing_status,
            estimated_processing_time=None
        )
        
    except HTTPException as he:
        logger.warning(f"HTTP exception during file upload: {he.status_code} - {he.detail}")
        logger.warning(f"File: {file.filename}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during file upload for file: {file.filename}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your file. Please try again."
        )


@router.post("/analyze/{file_id}")
async def analyze_document(
    file_id: str,
    file_service: FileProcessingServiceDep = None
) -> Dict[str, Any]:
    """
    Start comprehensive AI analysis of an uploaded document using LangGraph workflow.
    
    Args:
        file_id: Unique identifier for the uploaded file
        
    Returns:
        Analysis initiation response with tracking information
    """
    try:
        # Check if file exists
        if file_id not in uploaded_files:
            raise HTTPException(
                status_code=404,
                detail=f"File with ID {file_id} not found"
            )
        
        uploaded_file = uploaded_files[file_id]
        
        # Get file content for analysis
        file_content = await file_service.storage_manager.get_file_content(file_id)
        if not file_content:
            raise HTTPException(
                status_code=404,
                detail="File content not found"
            )
        
        # Get analysis service and start analysis
        service = get_analysis_service(file_service)
        result = await service.analyze_document(
            file_id=file_id,
            file_content=file_content,
            filename=uploaded_file.filename
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Document analysis failed for {file_id}: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/analysis/{file_id}")
async def get_analysis_result(
    file_id: str,
    file_service: FileProcessingServiceDep = None
) -> Dict[str, Any]:
    """
    Get AI analysis result for a document.
    
    Args:
        file_id: Unique identifier for the uploaded file
        
    Returns:
        Complete analysis result including legal analysis, risk assessment, and summary
    """
    try:
        service = get_analysis_service(file_service)
        result = await service.get_analysis_result(file_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis result for file {file_id} not found"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to get analysis result for {file_id}: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve analysis result"
        )


@router.get("/status/{file_id}", response_model=ProcessingProgress)
async def get_processing_status(
    file_id: str,
    file_service: FileProcessingServiceDep = None
) -> ProcessingProgress:
    """
    Get processing status for an uploaded file or analysis.
    
    Args:
        file_id: Unique identifier for the uploaded file
        
    Returns:
        Current processing status and progress information
    """
    # Check basic file upload status first
    if file_id not in uploaded_files:
        raise HTTPException(
            status_code=404,
            detail=f"File with ID {file_id} not found"
        )
    
    uploaded_file = uploaded_files[file_id]
    
    # Try to get LangGraph analysis status
    try:
        service = get_analysis_service(file_service)
        analysis_status = await service.get_processing_status(file_id)
        
        if analysis_status.get("status") != "not_found":
            # Return analysis status if available
            return ProcessingProgress(
                file_id=file_id,
                status=ProcessingStatus.PROCESSING if analysis_status["status"] == "processing" else ProcessingStatus.COMPLETED,
                progress_percentage=analysis_status.get("progress_percentage", 0.0),
                current_step=analysis_status.get("current_step", "Unknown"),
                estimated_time_remaining=None,
                error_message=analysis_status.get("error_message")
            )
    except Exception:
        # Fall back to basic file status if analysis status fails
        pass
    
    # Return basic file upload status
    progress_map = {
        ProcessingStatus.UPLOADED: 10.0,
        ProcessingStatus.PROCESSING: 50.0,
        ProcessingStatus.COMPLETED: 100.0,
        ProcessingStatus.FAILED: 0.0,
    }
    
    step_map = {
        ProcessingStatus.UPLOADED: "File uploaded, ready for analysis",
        ProcessingStatus.PROCESSING: "Extracting text from document",
        ProcessingStatus.COMPLETED: "File processing completed",
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
        "cleanup_enabled": file_service.settings.auto_cleanup_after_analysis,
        "cleanup_interval_hours": file_service.storage_manager.cleanup_interval / 3600
    }


@router.post("/admin/cleanup")
async def manual_cleanup(
    max_age_hours: int = 24,
    file_service: FileProcessingServiceDep = None
) -> Dict[str, Any]:
    """
    Manually trigger file cleanup.
    
    Args:
        max_age_hours: Maximum age of files to keep (default 24 hours)
        
    Returns:
        Cleanup operation result
    """
    try:
        # Get stats before cleanup
        stats_before = await file_service.storage_manager.get_storage_stats()
        
        # Perform cleanup
        await file_service.storage_manager.cleanup_old_files(max_age_hours)
        
        # Get stats after cleanup
        stats_after = await file_service.storage_manager.get_storage_stats()
        
        files_removed = stats_before["total_files"] - stats_after["total_files"]
        space_freed_mb = (stats_before["total_size_mb"] - stats_after["total_size_mb"])
        
        return {
            "success": True,
            "message": f"Cleanup completed successfully",
            "files_removed": files_removed,
            "space_freed_mb": round(space_freed_mb, 2),
            "stats_before": stats_before,
            "stats_after": stats_after
        }
        
    except Exception as e:
        logger.error(f"Manual cleanup failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Cleanup failed: {str(e)}"
        )
