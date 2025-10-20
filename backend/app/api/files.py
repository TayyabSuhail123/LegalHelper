"""File upload and processing API endpoints."""

import logging
import traceback
from typing import Dict, Any, Optional
from uuid import UUID
from functools import lru_cache

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.models.file_processing import (
    FileUploadResponse,
    ProcessingStatus,
    ProcessingProgress,
    UploadedFile
)
from app.core.dependencies import FileProcessingServiceDep, FileServiceDep, AnalysisServiceDep
from app.services.file_service import FileService
from app.services.analysis_service import AnalysisService

# Configure logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_PAGE_SIZE = 50
DEFAULT_CLEANUP_AGE_HOURS = 24
MAX_PAGE_SIZE = 100

# Create router
router = APIRouter()


# Response Models
class StorageStatsResponse(BaseModel):
    """Storage statistics response model."""
    storage_stats: Dict[str, Any]
    cleanup_enabled: bool
    cleanup_interval_hours: float


class CleanupResponse(BaseModel):
    """Cleanup operation response model."""
    success: bool
    message: str
    files_removed: int
    space_freed_mb: float
    stats_before: Dict[str, Any]
    stats_after: Dict[str, Any]


def validate_file_id(file_id: str) -> str:
    """Validate file ID format."""
    try:
        UUID(file_id)
        return file_id
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid file ID format"
        )


def validate_pagination(limit: int, offset: int) -> tuple[int, int]:
    """Validate pagination parameters."""
    if limit <= 0 or limit > MAX_PAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Limit must be between 1 and {MAX_PAGE_SIZE}"
        )
    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="Offset must be non-negative"
        )
    return limit, offset


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(..., description="Contract file to upload (PDF, DOCX, TXT)"),
    file_service: FileService = Depends()
) -> FileUploadResponse:
    """
    Upload a contract file for processing.
    
    Supports PDF, DOCX, and TXT files up to 50MB.
    Returns immediately with file_id for tracking processing status.
    """
    try:
        logger.info(f"Starting file upload for: {file.filename}")
        
        # Use service layer for file processing
        uploaded_file = await file_service.upload_file(file)
        
        logger.info(f"File upload successful - File ID: {uploaded_file.file_id}")
        
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
    analysis_service: AnalysisService = Depends()
) -> Dict[str, Any]:
    """
    Start comprehensive AI analysis of an uploaded document using LangGraph workflow.
    
    Args:
        file_id: Unique identifier for the uploaded file
        
    Returns:
        Analysis initiation response with tracking information
    """
    try:
        # Validate file ID format
        validate_file_id(file_id)
        
        # Use service layer for analysis
        result = await analysis_service.start_analysis(file_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document analysis failed for {file_id}: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/analysis/{file_id}")
async def get_analysis_result(
    file_id: str,
    analysis_service: AnalysisService = Depends()
) -> Dict[str, Any]:
    """
    Get AI analysis result for a document.
    
    Args:
        file_id: Unique identifier for the uploaded file
        
    Returns:
        Complete analysis result
    """
    try:
        validate_file_id(file_id)
        
        result = await analysis_service.get_result(file_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis result for file {file_id} not found"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis result for {file_id}: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve analysis result"
        )


@router.get("/status/{file_id}", response_model=ProcessingProgress)
async def get_processing_status(
    file_id: str,
    file_service: FileService = Depends()
) -> ProcessingProgress:
    """
    Get processing status for an uploaded file or analysis.
    """
    validate_file_id(file_id)
    
    try:
        return await file_service.get_processing_status(file_id)
    except Exception as e:
        logger.error(f"Failed to get processing status for {file_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve processing status"
        )


@router.get("/files/{file_id}", response_model=UploadedFile)
async def get_file_details(
    file_id: str,
    file_service: FileService = Depends()
) -> UploadedFile:
    """Get detailed information about an uploaded file."""
    validate_file_id(file_id)
    
    try:
        file_details = await file_service.get_file_details(file_id)
        if not file_details:
            raise HTTPException(
                status_code=404,
                detail=f"File with ID {file_id} not found"
            )
        return file_details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file details for {file_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve file details"
        )


@router.get("/files", response_model=Dict[str, Any])
async def list_uploaded_files(
    limit: int = DEFAULT_PAGE_SIZE,
    offset: int = 0,
    file_service: FileService = Depends()
) -> Dict[str, Any]:
    """List all uploaded files with pagination."""
    limit, offset = validate_pagination(limit, offset)
    
    try:
        return await file_service.list_files(limit=limit, offset=offset)
    except Exception as e:
        logger.error(f"Failed to list files: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve file list"
        )


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    file_service: FileService = Depends()
) -> JSONResponse:
    """Delete an uploaded file and its data."""
    validate_file_id(file_id)
    
    try:
        success = await file_service.delete_file(file_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"File with ID {file_id} not found"
            )
        
        return JSONResponse(
            content={
                "success": True,
                "message": f"File {file_id} deleted successfully"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete file"
        )


@router.get("/supported-formats")
async def get_supported_formats(
    file_service: FileProcessingServiceDep = Depends()
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


@router.get("/storage/stats", response_model=StorageStatsResponse)
async def get_storage_stats(
    file_service: FileService = Depends()
) -> StorageStatsResponse:
    """Get storage statistics."""
    try:
        stats_data = await file_service.get_storage_stats()
        return StorageStatsResponse(
            storage_stats=stats_data["storage_stats"],
            cleanup_enabled=stats_data["cleanup_enabled"],
            cleanup_interval_hours=stats_data["cleanup_interval_hours"]
        )
    except Exception as e:
        logger.error(f"Failed to get storage stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve storage statistics"
        )


@router.post("/admin/cleanup", response_model=CleanupResponse)
async def manual_cleanup(
    max_age_hours: int = DEFAULT_CLEANUP_AGE_HOURS,
    file_service: FileProcessingServiceDep = Depends()
) -> CleanupResponse:
    """
    Manually trigger file cleanup.
    
    Args:
        max_age_hours: Maximum age of files to keep (default 24 hours)
        
    Returns:
        Cleanup operation result
    """
    if max_age_hours <= 0:
        raise HTTPException(
            status_code=400,
            detail="max_age_hours must be positive"
        )
    
    try:
        # Get stats before cleanup
        stats_before = await file_service.storage_manager.get_storage_stats()
        
        # Perform cleanup
        await file_service.storage_manager.cleanup_old_files(max_age_hours)
        
        # Get stats after cleanup
        stats_after = await file_service.storage_manager.get_storage_stats()
        
        files_removed = stats_before["total_files"] - stats_after["total_files"]
        space_freed_mb = (stats_before["total_size_mb"] - stats_after["total_size_mb"])
        
        return CleanupResponse(
            success=True,
            message="Cleanup completed successfully",
            files_removed=files_removed,
            space_freed_mb=round(space_freed_mb, 2),
            stats_before=stats_before,
            stats_after=stats_after
        )
        
    except Exception as e:
        logger.error(f"Manual cleanup failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Cleanup failed: {str(e)}"
        )
