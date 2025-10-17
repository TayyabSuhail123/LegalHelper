"""Core module initialization."""

from .config import settings
from .dependencies import FileProcessingServiceDep, get_file_processing_service

__all__ = ["settings", "FileProcessingServiceDep", "get_file_processing_service"]
