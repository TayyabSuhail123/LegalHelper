"""Dependency injection for FastAPI application."""

from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from app.core.file_processing import FileProcessingService
from app.core.config import settings


@lru_cache()
def get_file_processing_service() -> FileProcessingService:
    """
    Get file processing service instance.
    
    Uses LRU cache to ensure singleton behavior during app lifecycle.
    """
    return FileProcessingService(
        upload_dir=settings.upload_dir,
        max_file_size=settings.max_file_size
    )


# Type aliases for dependency injection
FileProcessingServiceDep = Annotated[FileProcessingService, Depends(get_file_processing_service)]
