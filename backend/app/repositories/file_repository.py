"""File repository for uploaded file data access."""

from typing import Optional, List, Dict, Any
from datetime import datetime

from .base_repository import InMemoryRepository
from app.models.file_processing import UploadedFile, ProcessingStatus, FileType


class FileRepository(InMemoryRepository[UploadedFile]):
    """
    Repository for managing uploaded file data.
    
    Extends the base in-memory repository with file-specific operations.
    """
    
    async def get_by_filename(self, filename: str) -> Optional[UploadedFile]:
        """
        Get file by filename.
        
        Args:
            filename: Name of the file
            
        Returns:
            File if found, None otherwise
        """
        for file in self._storage.values():
            if file.filename == filename:
                return file
        return None
    
    async def get_by_status(self, status: ProcessingStatus) -> List[UploadedFile]:
        """
        Get files by processing status.
        
        Args:
            status: Processing status to filter by
            
        Returns:
            List of files with the specified status
        """
        return [
            file for file in self._storage.values() 
            if file.processing_status == status
        ]
    
    async def get_by_file_type(self, file_type: FileType) -> List[UploadedFile]:
        """
        Get files by type.
        
        Args:
            file_type: File type to filter by
            
        Returns:
            List of files with the specified type
        """
        return [
            file for file in self._storage.values() 
            if file.file_type == file_type
        ]
    
    async def get_files_uploaded_after(self, timestamp: datetime) -> List[UploadedFile]:
        """
        Get files uploaded after a specific timestamp.
        
        Args:
            timestamp: Timestamp to filter by
            
        Returns:
            List of files uploaded after the timestamp
        """
        return [
            file for file in self._storage.values() 
            if file.upload_timestamp > timestamp
        ]
    
    async def get_failed_files(self) -> List[UploadedFile]:
        """
        Get all files that failed processing.
        
        Returns:
            List of failed files
        """
        return await self.get_by_status(ProcessingStatus.FAILED)
    
    async def get_completed_files(self) -> List[UploadedFile]:
        """
        Get all successfully processed files.
        
        Returns:
            List of completed files
        """
        return await self.get_by_status(ProcessingStatus.COMPLETED)
    
    async def update_status(self, file_id: str, status: ProcessingStatus, error_message: Optional[str] = None) -> Optional[UploadedFile]:
        """
        Update file processing status.
        
        Args:
            file_id: File identifier
            status: New processing status
            error_message: Error message if status is FAILED
            
        Returns:
            Updated file if found, None otherwise
        """
        file = await self.get_by_id(file_id)
        if not file:
            return None
        
        file.processing_status = status
        if error_message:
            file.error_message = error_message
        
        return await self.update(file_id, file)
    
    async def get_files_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics about files.
        
        Returns:
            Dictionary with file statistics
        """
        all_files = await self.list_all()
        
        total_count = len(all_files)
        total_size = sum(file.file_size for file in all_files)
        
        status_counts = {}
        type_counts = {}
        
        for file in all_files:
            # Count by status
            status = file.processing_status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by type
            file_type = file.file_type.value
            type_counts[file_type] = type_counts.get(file_type, 0) + 1
        
        return {
            "total_files": total_count,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "status_breakdown": status_counts,
            "type_breakdown": type_counts,
            "has_failed_files": ProcessingStatus.FAILED.value in status_counts,
            "completed_files": status_counts.get(ProcessingStatus.COMPLETED.value, 0)
        }
