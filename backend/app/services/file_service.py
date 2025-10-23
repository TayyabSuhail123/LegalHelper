"""Simplified file service that delegates to file processing service."""

import logging
from typing import Any

from fastapi import HTTPException, UploadFile

from app.models.file_processing import DocumentFile, ProcessingStatus
from app.schemas.file_schemas import ProcessingProgressResponse
from app.services.file_processing import FileProcessingService

logger = logging.getLogger(__name__)


class FileService:
    """
    Simplified service layer for file-related business operations.

    This service provides a business logic layer over the file processing service,
    without complex repository patterns.
    """

    def __init__(self, file_processing_service: FileProcessingService):
        self.file_processing_service = file_processing_service

    async def upload_file(self, file: UploadFile) -> DocumentFile:
        """
        Upload a file with business validation.

        Args:
            file: FastAPI uploaded file

        Returns:
            Uploaded file metadata

        Raises:
            HTTPException: If upload fails or validation fails
        """
        try:
            logger.info(f"FileService: Processing upload for {file.filename}")

            # Delegate to file processing service
            uploaded_file = await self.file_processing_service.process_file(file)

            logger.info(f"FileService: File {uploaded_file.file_id} stored successfully")

            return uploaded_file

        except Exception as e:
            logger.error(f"FileService: Upload failed for {file.filename}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")

    async def get_file(self, file_id: str) -> dict[str, Any] | None:
        """Get file metadata by ID."""
        try:
            # Check if file still exists in storage
            file_path = await self.file_processing_service.storage_manager.get_file_path(file_id)
            if file_path and file_path.exists():
                # File exists, return basic metadata with completed status
                return {
                    "file_id": file_id,
                    "status": "completed",  # Changed from "processed" to "completed"
                    "file_path": str(file_path),
                    "progress_percentage": 100.0,
                    "current_step": "File processed",
                }
            else:
                # File doesn't exist or was cleaned up
                return None
        except Exception as e:
            logger.error(f"Failed to get file {file_id}: {e}")
            return None

    async def get_file_content(self, file_id: str) -> bytes | None:
        """Get file content by ID."""
        try:
            return await self.file_processing_service.storage_manager.get_file_content(file_id)
        except Exception as e:
            logger.error(f"Failed to get file content {file_id}: {e}")
            return None

    async def delete_file(self, file_id: str) -> bool:
        """Delete a file."""
        try:
            success = await self.file_processing_service.delete_file(file_id)
            if success:
                logger.info(f"FileService: Successfully deleted file {file_id}")
            return success
        except Exception as e:
            logger.error(f"FileService: Delete failed for {file_id}: {str(e)}")
            return False

    async def list_files(self, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        """List files with pagination."""
        try:
            files = await self.file_processing_service.list_files(limit=limit, offset=offset)
            return {
                "files": files,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total_count": len(files),  # Simplified for now
                },
            }
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return {"files": [], "pagination": {"limit": limit, "offset": offset, "total_count": 0}}

    async def get_file_details(self, file_id: str) -> dict[str, Any] | None:
        """Get detailed file information."""
        file_info = await self.get_file(file_id)
        if not file_info:
            return None

        # Extract filename and type from file_path
        file_path = file_info.get("file_path", "")
        filename = file_path.split("/")[-1] if file_path else "unknown"

        # Determine file type from extension
        file_extension = filename.split(".")[-1].lower() if "." in filename else "unknown"
        file_type_map = {"pdf": "pdf", "docx": "docx", "txt": "txt"}
        file_type = file_type_map.get(file_extension, "pdf")  # default to pdf

        # Get file size if file exists
        file_size = 0
        try:
            from pathlib import Path

            full_path = Path(file_path)
            if full_path.exists():
                file_size = full_path.stat().st_size
        except Exception:
            file_size = 0

        # Convert status to ProcessingStatus
        status_str = file_info.get("status", "uploaded")

        # Return UploadedFile compatible structure
        return {
            "file_id": file_id,
            "filename": filename,
            "file_type": file_type,
            "file_size": file_size,
            "upload_timestamp": "2024-01-01T00:00:00",  # placeholder since we don't store this
            "processing_status": status_str,
            "extracted_text": None,
            "error_message": file_info.get("error_message"),
        }

    async def get_processing_status(self, file_id: str) -> ProcessingProgressResponse:
        """Get file processing status."""
        try:
            file_info = await self.get_file(file_id)
            if not file_info:
                return ProcessingProgressResponse(
                    file_id=file_id,
                    status=ProcessingStatus.NOT_FOUND,
                    progress_percentage=0.0,
                    current_step="File not found",
                    error_message="File not found",
                )

            # Get status from file info or default to uploaded
            status_str = file_info.get("status", "uploaded")
            try:
                status = ProcessingStatus(status_str)
            except ValueError:
                status = ProcessingStatus.UPLOADED

            return ProcessingProgressResponse(
                file_id=file_id,
                status=status,
                progress_percentage=file_info.get("progress_percentage", 0.0),
                current_step=file_info.get("current_step", "File uploaded"),
                error_message=file_info.get("error_message"),
            )
        except Exception as e:
            logger.error(f"Failed to get processing status for {file_id}: {e}")
            return ProcessingProgressResponse(
                file_id=file_id,
                status=ProcessingStatus.FAILED,
                progress_percentage=0.0,
                current_step="Error occurred",
                error_message=f"Failed to get status: {str(e)}",
            )
