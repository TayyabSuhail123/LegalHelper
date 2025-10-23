"""File upload and processing API endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.core.dependencies import AnalysisServiceDep, FileProcessingServiceDep, FileServiceDep
from app.core.error_handlers import APIErrorHandler, ValidationUtils, error_context
from app.schemas.file_schemas import (
    CleanupResponse,
    FileDetailsResponse,
    FileUploadResponse,
    ProcessingProgressResponse,
    StorageStatsResponse,
)

# Configure logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_PAGE_SIZE = 50
DEFAULT_CLEANUP_AGE_HOURS = 24
MAX_PAGE_SIZE = 100

# Create router
router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file_service: FileServiceDep,
    file: UploadFile = File(..., description="Contract file to upload (PDF, DOCX, TXT)"),
) -> FileUploadResponse:
    """
    Upload a contract file for processing.

    Supports PDF, DOCX, and TXT files up to 50MB.
    Returns immediately with file_id for tracking processing status.
    """
    with error_context("file_upload"):
        logger.info(f"Starting file upload for: {file.filename}")

        # Use service layer for file processing
        uploaded_file = await file_service.upload_file(file)

        logger.info(f"File upload successful - File ID: {uploaded_file.file_id}")

        return FileUploadResponse(
            success=True,
            message="File uploaded successfully",
            file_id=uploaded_file.file_id,
            processing_status=uploaded_file.processing_status,
            estimated_processing_time=None,
        )


@router.post("/analyze/{file_id}")
async def analyze_document(
    file_id: str, analysis_service: AnalysisServiceDep, file_service: FileServiceDep
) -> dict[str, Any]:
    """
    Start comprehensive AI analysis of an uploaded document using LangGraph workflow.

    Args:
        file_id: Unique identifier for the uploaded file

    Returns:
        Analysis initiation response with tracking information
    """
    with error_context("document_analysis", file_id):
        # Validate file ID format
        ValidationUtils.validate_file_id(file_id)

        # Get file content and metadata
        file_content = await file_service.get_file_content(file_id)
        if not file_content:
            raise APIErrorHandler.handle_not_found_error("File", file_id)

        file_details = await file_service.get_file_details(file_id)
        if not file_details:
            raise APIErrorHandler.handle_not_found_error("File details", file_id)

        # Use core analysis service directly
        result = await analysis_service.analyze_document(
            file_id=file_id,
            file_content=file_content,
            filename=file_details.get("filename", "unknown.pdf"),
        )

        return result


@router.get("/analysis/{file_id}")
async def get_analysis_result(file_id: str, analysis_service: AnalysisServiceDep) -> dict[str, Any]:
    """
    Get AI analysis result for a document.

    Args:
        file_id: Unique identifier for the uploaded file

    Returns:
        Complete analysis result
    """
    try:
        ValidationUtils.validate_file_id(file_id)

        result = await analysis_service.get_analysis_result(file_id)

        if not result:
            raise HTTPException(
                status_code=404, detail=f"Analysis result for file {file_id} not found"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis result for {file_id}: {str(e)}")

        raise HTTPException(status_code=500, detail="Failed to retrieve analysis result")


@router.get("/status/{file_id}", response_model=ProcessingProgressResponse)
async def get_processing_progress(
    file_id: str, file_service: FileServiceDep
) -> ProcessingProgressResponse:
    """
    Get processing status for an uploaded file or analysis.
    """
    ValidationUtils.validate_file_id(file_id)

    try:
        return await file_service.get_processing_status(file_id)
    except Exception as e:
        logger.error(f"Failed to get processing status for {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve processing status")


@router.get("/files/{file_id}", response_model=FileDetailsResponse)
async def get_file_details(file_id: str, file_service: FileServiceDep) -> FileDetailsResponse:
    """Get detailed information about an uploaded file."""
    ValidationUtils.validate_file_id(file_id)

    try:
        file_details = await file_service.get_file_details(file_id)
        if not file_details:
            raise HTTPException(status_code=404, detail=f"File with ID {file_id} not found")
        return file_details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file details for {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve file details")


@router.get("/files", response_model=dict[str, Any])
async def list_uploaded_files(
    file_service: FileServiceDep, limit: int = DEFAULT_PAGE_SIZE, offset: int = 0
) -> dict[str, Any]:
    """List all uploaded files with pagination."""
    limit, offset = ValidationUtils.validate_pagination(limit, offset)

    try:
        return await file_service.list_files(limit=limit, offset=offset)
    except Exception as e:
        logger.error(f"Failed to list files: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve file list")


@router.delete("/files/{file_id}")
async def delete_file(file_id: str, file_service: FileServiceDep) -> JSONResponse:
    """Delete an uploaded file and its data."""
    ValidationUtils.validate_file_id(file_id)

    try:
        success = await file_service.delete_file(file_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"File with ID {file_id} not found")

        return JSONResponse(
            content={"success": True, "message": f"File {file_id} deleted successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete file")


@router.get("/supported-formats")
async def get_supported_formats(file_service: FileProcessingServiceDep) -> dict[str, Any]:
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
                "description": "Portable Document Format files",
            },
            {
                "type": "DOCX",
                "extensions": [".docx"],
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "description": "Microsoft Word documents",
            },
            {
                "type": "TXT",
                "extensions": [".txt"],
                "mime_type": "text/plain",
                "description": "Plain text files",
            },
        ],
        "max_file_size": f"{file_service.max_file_size / (1024 * 1024):.0f} MB",
        "max_file_size_bytes": file_service.max_file_size,
    }


@router.get("/storage/stats", response_model=StorageStatsResponse)
async def get_storage_stats(file_service: FileServiceDep) -> StorageStatsResponse:
    """Get storage statistics."""
    try:
        stats_data = await file_service.get_storage_stats()
        return StorageStatsResponse(
            storage_stats=stats_data["storage_stats"],
            cleanup_enabled=stats_data["cleanup_enabled"],
            cleanup_interval_hours=stats_data["cleanup_interval_hours"],
        )
    except Exception as e:
        logger.error(f"Failed to get storage stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve storage statistics")


@router.post("/admin/cleanup", response_model=CleanupResponse)
async def manual_cleanup(
    file_service: FileProcessingServiceDep, max_age_hours: int = DEFAULT_CLEANUP_AGE_HOURS
) -> CleanupResponse:
    """
    Manually trigger file cleanup.

    Args:
        max_age_hours: Maximum age of files to keep (default 24 hours)

    Returns:
        Cleanup operation result
    """
    if max_age_hours <= 0:
        raise HTTPException(status_code=400, detail="max_age_hours must be positive")

    try:
        # Get stats before cleanup
        stats_before = await file_service.storage_manager.get_storage_stats()

        # Perform cleanup
        await file_service.storage_manager.cleanup_old_files(max_age_hours)

        # Get stats after cleanup
        stats_after = await file_service.storage_manager.get_storage_stats()

        files_removed = stats_before["total_files"] - stats_after["total_files"]
        space_freed_mb = stats_before["total_size_mb"] - stats_after["total_size_mb"]

        return CleanupResponse(
            success=True,
            message="Cleanup completed successfully",
            files_removed=files_removed,
            space_freed_mb=round(space_freed_mb, 2),
            stats_before=stats_before,
            stats_after=stats_after,
        )

    except Exception as e:
        logger.error(f"Manual cleanup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")
