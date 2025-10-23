"""API schemas for file processing endpoints."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.file_processing import FileType, ProcessingStatus, RiskLevel


class FileUploadRequest(BaseModel):
    """Request schema for file upload (if needed for additional metadata)."""

    description: str | None = None
    tags: list[str] = Field(default_factory=list)


class FileUploadResponse(BaseModel):
    """API response schema for file upload."""

    success: bool
    message: str
    file_id: str
    processing_status: ProcessingStatus
    estimated_processing_time: int | None = Field(None, description="Estimated time in seconds")


class FileDetailsResponse(BaseModel):
    """API response schema for file details."""

    file_id: str
    filename: str
    file_type: FileType
    file_size: int
    upload_timestamp: datetime
    processing_status: ProcessingStatus
    error_message: str | None = None


class ProcessingProgressResponse(BaseModel):
    """API response schema for processing progress."""

    file_id: str
    status: ProcessingStatus
    progress_percentage: float = Field(ge=0, le=100)
    current_step: str
    estimated_time_remaining: int | None = Field(None, description="Estimated time in seconds")
    error_message: str | None = None


class RiskSummary(BaseModel):
    """Summary of risk assessment for API response."""

    overall_score: float = Field(ge=0, le=10)
    overall_level: RiskLevel
    total_risks_found: int
    critical_issues: int
    recommendations_count: int


class DocumentSummaryResponse(BaseModel):
    """API response schema for document summary."""

    document_summary: str
    document_purpose: str | None = None
    key_parties: list[str] = Field(default_factory=list)
    important_dates: list[str] = Field(default_factory=list)


class AnalysisResultResponse(BaseModel):
    """API response schema for complete analysis results."""

    file_id: str
    analysis_id: str
    status: str
    timestamp: datetime

    # Summary information
    document_summary: DocumentSummaryResponse
    risk_summary: RiskSummary

    # Detailed findings (public-safe versions)
    legal_risks: list[dict[str, Any]] = Field(default_factory=list)
    potential_liabilities: list[str] = Field(default_factory=list)
    suspicious_clauses: list[dict[str, Any]] = Field(default_factory=list)

    # Recommendations
    immediate_actions: list[str] = Field(default_factory=list)
    before_signing: list[str] = Field(default_factory=list)
    long_term_considerations: list[str] = Field(default_factory=list)

    # Metadata
    confidence_score: float = Field(ge=0, le=1)
    processing_time: float | None = Field(None, description="Processing time in seconds")


class FileListResponse(BaseModel):
    """API response schema for file listing."""

    files: list[FileDetailsResponse]
    total_count: int
    page: int
    page_size: int
    has_more: bool


class AnalysisInitiationResponse(BaseModel):
    """API response schema for analysis initiation."""

    success: bool
    message: str
    file_id: str
    analysis_id: str
    status: str
    estimated_completion_time: int | None = Field(None, description="Estimated time in seconds")


class DeleteFileResponse(BaseModel):
    """API response schema for file deletion."""

    success: bool
    message: str
    file_id: str


class ErrorResponse(BaseModel):
    """Standard API error response schema."""

    error: str
    details: str | None = None
    error_code: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str | None = None


class HealthResponse(BaseModel):
    """API response schema for health checks."""

    status: str
    message: str
    timestamp: datetime
    version: str
    environment: str
    uptime_seconds: float | None = None


class SupportedFormatsResponse(BaseModel):
    """API response schema for supported file formats."""

    supported_formats: list[str]
    max_file_size_mb: float
    description: str


# Request schemas
class PaginationRequest(BaseModel):
    """Request schema for pagination parameters."""

    limit: int = Field(50, ge=1, le=100, description="Number of items per page")
    offset: int = Field(0, ge=0, description="Number of items to skip")


class FileFilterRequest(BaseModel):
    """Request schema for file filtering."""

    file_type: FileType | None = None
    status: ProcessingStatus | None = None
    uploaded_after: datetime | None = None
    uploaded_before: datetime | None = None


class StorageStatsResponse(BaseModel):
    """Storage statistics response schema."""

    storage_stats: dict[str, Any]
    cleanup_enabled: bool
    cleanup_interval_hours: float


class CleanupResponse(BaseModel):
    """Cleanup operation response schema."""

    success: bool
    message: str
    files_removed: int
    space_freed_mb: float
    stats_before: dict[str, Any]
    stats_after: dict[str, Any]
