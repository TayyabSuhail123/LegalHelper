"""File service for file-related business logic."""

import logging
from typing import Optional, List, Dict, Any
from fastapi import UploadFile, HTTPException

from app.repositories.file_repository import FileRepository
from app.core.file_processing import FileProcessingService
from app.models.file_processing import UploadedFile, ProcessingStatus, ProcessingProgress

logger = logging.getLogger(__name__)


class FileService:
    """
    Service layer for file-related business operations.
    
    This service encapsulates business logic for file operations,
    using repositories for data access.
    """
    
    def __init__(self, file_processing_service: FileProcessingService):
        self.file_processing_service = file_processing_service
        self.file_repository = FileRepository()
    
    async def upload_file(self, file: UploadFile) -> UploadedFile:
        """
        Handle file upload with business logic.
        
        Args:
            file: Uploaded file
            
        Returns:
            Processed file information
            
        Raises:
            HTTPException: If upload fails
        """
        try:
            logger.info(f"FileService: Processing upload for {file.filename}")
            
            # Use file processing service to handle the upload
            uploaded_file = await self.file_processing_service.process_file(file)
            
            # Store in repository
            await self.file_repository.create(uploaded_file)
            
            logger.info(f"FileService: File {uploaded_file.file_id} stored successfully")
            return uploaded_file
            
        except Exception as e:
            logger.error(f"FileService: Upload failed for {file.filename}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"File upload failed: {str(e)}"
            )
    
    async def get_file_details(self, file_id: str) -> Optional[UploadedFile]:
        """
        Get file details by ID.
        
        Args:
            file_id: File identifier
            
        Returns:
            File details if found, None otherwise
        """
        return await self.file_repository.get_by_id(file_id)
    
    async def delete_file(self, file_id: str) -> bool:
        """
        Delete a file and clean up storage.
        
        Args:
            file_id: File identifier
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Check if file exists
            file = await self.file_repository.get_by_id(file_id)
            if not file:
                return False
            
            # Clean up physical storage
            await self.file_processing_service.storage_manager.remove_file(file_id)
            
            # Remove from repository
            return await self.file_repository.delete(file_id)
            
        except Exception as e:
            logger.error(f"FileService: Delete failed for {file_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"File deletion failed: {str(e)}"
            )
    
    async def list_files(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        List files with pagination.
        
        Args:
            limit: Maximum number of files to return
            offset: Number of files to skip
            
        Returns:
            Paginated file list with metadata
        """
        try:
            files = await self.file_repository.list_all(limit=limit, offset=offset)
            total_count = await self.file_repository.count()
            
            # Convert to simplified format for API response
            file_list = [
                {
                    "file_id": f.file_id,
                    "filename": f.filename,
                    "file_type": f.file_type.value,
                    "file_size": f.file_size,
                    "upload_timestamp": f.upload_timestamp.isoformat(),
                    "processing_status": f.processing_status.value,
                    "has_extracted_text": bool(f.extracted_text),
                    "has_error": bool(f.error_message)
                }
                for f in files
            ]
            
            return {
                "files": file_list,
                "pagination": {
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_next": offset + limit < total_count,
                    "has_previous": offset > 0
                }
            }
            
        except Exception as e:
            logger.error(f"FileService: List files failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve file list"
            )
    
    async def get_processing_status(self, file_id: str) -> ProcessingProgress:
        """
        Get processing status for a file.
        
        Args:
            file_id: File identifier
            
        Returns:
            Processing progress information
            
        Raises:
            HTTPException: If file not found
        """
        file = await self.file_repository.get_by_id(file_id)
        if not file:
            raise HTTPException(
                status_code=404,
                detail=f"File with ID {file_id} not found"
            )
        
        # Map status to progress percentage
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
            status=file.processing_status,
            progress_percentage=progress_map[file.processing_status],
            current_step=step_map[file.processing_status],
            estimated_time_remaining=None,
            error_message=file.error_message
        )
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Storage usage statistics
        """
        try:
            # Get file repository stats
            file_stats = await self.file_repository.get_files_summary()
            
            # Get physical storage stats
            storage_stats = await self.file_processing_service.storage_manager.get_storage_stats()
            
            return {
                "file_stats": file_stats,
                "storage_stats": storage_stats,
                "cleanup_enabled": self.file_processing_service.settings.auto_cleanup_after_analysis,
                "cleanup_interval_hours": self.file_processing_service.storage_manager.cleanup_interval / 3600
            }
            
        except Exception as e:
            logger.error(f"FileService: Get storage stats failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve storage statistics"
            )
    
    async def update_file_status(self, file_id: str, status: ProcessingStatus, error_message: Optional[str] = None) -> Optional[UploadedFile]:
        """
        Update file processing status.
        
        Args:
            file_id: File identifier
            status: New processing status
            error_message: Error message if status is FAILED
            
        Returns:
            Updated file if found, None otherwise
        """
        return await self.file_repository.update_status(file_id, status, error_message)
    
    async def get_failed_files(self) -> List[UploadedFile]:
        """
        Get all files that failed processing.
        
        Returns:
            List of failed files
        """
        return await self.file_repository.get_failed_files()
    
    async def get_completed_files(self) -> List[UploadedFile]:
        """
        Get all successfully processed files.
        
        Returns:
            List of completed files
        """
        return await self.file_repository.get_completed_files()
