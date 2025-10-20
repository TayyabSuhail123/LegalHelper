"""Dependency injection for FastAPI application."""

from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from app.core.file_processing import FileProcessingService
from app.core.config import settings
from app.services.file_service import FileService
from app.services.analysis_service import AnalysisService


@lru_cache()
def get_file_processing_service() -> FileProcessingService:
    """
    Get file processing service instance.
    
    Uses LRU cache to ensure singleton behavior during app lifecycle.
    """
    return FileProcessingService(
        upload_dir=settings.upload_dir,
        max_file_size=settings.max_file_size,
        settings=settings
    )


def get_file_service(
    file_processing_service: FileProcessingService = Depends(get_file_processing_service)
) -> FileService:
    """
    Get file service instance with repository pattern.
    
    Args:
        file_processing_service: Core file processing service
        
    Returns:
        File service with business logic
    """
    return FileService(file_processing_service)


def get_analysis_service(
    file_service: FileService = Depends(get_file_service)
) -> AnalysisService:
    """
    Get analysis service instance with repository pattern.
    
    Args:
        file_service: File service dependency
        
    Returns:
        Analysis service with business logic
    """
    return AnalysisService(file_service)


# Type aliases for dependency injection
FileProcessingServiceDep = Annotated[FileProcessingService, Depends(get_file_processing_service)]
FileServiceDep = Annotated[FileService, Depends(get_file_service)]
AnalysisServiceDep = Annotated[AnalysisService, Depends(get_analysis_service)]
