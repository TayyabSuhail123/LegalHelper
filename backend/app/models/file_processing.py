"""File upload and processing models."""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class FileType(str, Enum):
    """Supported file types for contract upload."""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class ProcessingStatus(str, Enum):
    """File processing status."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_FOUND = "not_found"


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UploadedFile(BaseModel):
    """Uploaded file information."""
    file_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    file_type: FileType
    file_size: int
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_status: ProcessingStatus = ProcessingStatus.UPLOADED
    extracted_text: Optional[str] = None
    error_message: Optional[str] = None


class ContractAnalysis(BaseModel):
    """Contract analysis results."""
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_id: str
    overall_risk_score: float = Field(ge=0, le=10, description="Risk score from 0-10")
    overall_risk_level: RiskLevel
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Risk categories
    financial_risks: List[Dict[str, Any]] = Field(default_factory=list)
    legal_risks: List[Dict[str, Any]] = Field(default_factory=list)
    operational_risks: List[Dict[str, Any]] = Field(default_factory=list)
    termination_risks: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Analysis details
    key_findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    missing_clauses: List[str] = Field(default_factory=list)
    problematic_clauses: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Executive summary
    executive_summary: Optional[str] = None


class FileUploadResponse(BaseModel):
    """Response for file upload."""
    success: bool
    message: str
    file_id: Optional[str] = None
    processing_status: ProcessingStatus
    estimated_processing_time: Optional[int] = None  # in seconds


class AnalysisResponse(BaseModel):
    """Response for analysis request."""
    success: bool
    message: str
    analysis: Optional[ContractAnalysis] = None


class ProcessingProgress(BaseModel):
    """Processing progress information."""
    file_id: str
    status: ProcessingStatus
    progress_percentage: float = Field(ge=0, le=100)
    current_step: str
    estimated_time_remaining: Optional[int] = None  # in seconds
    error_message: Optional[str] = None
