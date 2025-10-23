"""Business models for file processing and document analysis."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


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


class DocumentFile(BaseModel):
    """Business model for uploaded document files."""

    file_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    file_type: FileType
    file_size: int
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_status: ProcessingStatus = ProcessingStatus.UPLOADED

    # Internal storage details
    storage_path: str | None = None
    extracted_text: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Error tracking
    error_message: str | None = None
    retry_count: int = 0

    def mark_processing(self) -> None:
        """Mark file as being processed."""
        self.processing_status = ProcessingStatus.PROCESSING

    def mark_completed(self, extracted_text: str) -> None:
        """Mark file processing as completed."""
        self.processing_status = ProcessingStatus.COMPLETED
        self.extracted_text = extracted_text
        self.error_message = None

    def mark_failed(self, error: str) -> None:
        """Mark file processing as failed."""
        self.processing_status = ProcessingStatus.FAILED
        self.error_message = error
        self.retry_count += 1


class DocumentAnalysis(BaseModel):
    """Business model for document analysis results."""

    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_id: str
    document_file: DocumentFile | None = None

    # Risk assessment
    overall_risk_score: float = Field(ge=0, le=10, description="Risk score from 0-10")
    overall_risk_level: RiskLevel

    # Analysis content
    document_summary: str | None = None
    document_purpose: str | None = None
    key_parties: list[str] = Field(default_factory=list)
    important_dates: list[str] = Field(default_factory=list)

    # Risk categories
    legal_risks: list[dict[str, Any]] = Field(default_factory=list)
    potential_liabilities: list[str] = Field(default_factory=list)
    financial_risks: list[dict[str, Any]] = Field(default_factory=list)
    operational_risks: list[dict[str, Any]] = Field(default_factory=list)

    # Detailed findings
    suspicious_clauses: list[dict[str, Any]] = Field(default_factory=list)
    hidden_fees: list[str] = Field(default_factory=list)
    fraud_indicators: list[str] = Field(default_factory=list)

    # Legal advice
    legal_implications: list[str] = Field(default_factory=list)
    your_rights: list[str] = Field(default_factory=list)
    their_obligations: list[str] = Field(default_factory=list)
    potential_consequences: list[str] = Field(default_factory=list)

    # Action items
    immediate_actions: list[str] = Field(default_factory=list)
    before_signing: list[str] = Field(default_factory=list)
    long_term_considerations: list[str] = Field(default_factory=list)
    recommended_timeline: str | None = None

    # Metadata
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time: float | None = None
    confidence_score: float = 0.0

    def calculate_overall_risk(self) -> None:
        """Calculate overall risk score based on individual risk categories."""
        # Simple risk calculation - can be made more sophisticated
        risk_weights = {
            "legal_risks": 0.3,
            "financial_risks": 0.3,
            "operational_risks": 0.2,
            "fraud_indicators": 0.2,
        }

        total_score = 0.0
        total_score += len(self.legal_risks) * risk_weights["legal_risks"] * 2
        total_score += len(self.financial_risks) * risk_weights["financial_risks"] * 2
        total_score += len(self.operational_risks) * risk_weights["operational_risks"] * 2
        total_score += len(self.fraud_indicators) * risk_weights["fraud_indicators"] * 3

        self.overall_risk_score = min(total_score, 10.0)

        # Determine risk level
        if self.overall_risk_score >= 8:
            self.overall_risk_level = RiskLevel.CRITICAL
        elif self.overall_risk_score >= 6:
            self.overall_risk_level = RiskLevel.HIGH
        elif self.overall_risk_score >= 3:
            self.overall_risk_level = RiskLevel.MEDIUM
        else:
            self.overall_risk_level = RiskLevel.LOW
