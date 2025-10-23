"""
LangGraph state definitions for document analysis workflow.
"""

from enum import Enum
from typing import Any, TypedDict


class DocumentType(str, Enum):
    """Types of legal documents we can analyze."""

    CONTRACT = "contract"
    AGREEMENT = "agreement"
    TERMS_OF_SERVICE = "terms_of_service"
    PRIVACY_POLICY = "privacy_policy"
    NDA = "nda"
    EMPLOYMENT = "employment"
    LEASE = "lease"
    UNKNOWN = "unknown"


class RiskCategory(str, Enum):
    """Categories of legal risks."""

    FINANCIAL = "financial"
    LEGAL = "legal"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    TERMINATION = "termination"
    LIABILITY = "liability"


class RiskLevel(str, Enum):
    """Risk severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProcessingStatus(str, Enum):
    """Processing status for each step."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Risk(TypedDict):
    """Individual risk item."""

    category: RiskCategory
    level: RiskLevel
    title: str
    description: str
    recommendation: str
    confidence: float


class DocumentAnalysisState(TypedDict):
    """
    State object that flows through the LangGraph workflow.
    Each node can read from and write to this state.
    """

    # Input data
    file_id: str
    file_content: bytes
    filename: str
    file_type: str

    # Processing status tracking
    current_step: str
    progress_percentage: float

    # Text extraction results
    extracted_text: str | None
    text_extraction_status: ProcessingStatus

    # Multi-Agent Analysis Results
    # Document Summarizer Agent
    document_summary: str | None
    document_purpose: str | None
    key_parties: list[str] | None
    important_dates: list[str] | None

    # Risk Assessment Agent
    legal_risks: list[dict[str, Any]] | None
    potential_liabilities: list[str] | None
    overall_risk_score: float  # 0.0 to 10.0
    overall_risk_level: RiskLevel | None

    # Fraud Detection Agent
    suspicious_clauses: list[dict[str, Any]] | None
    hidden_fees: list[str] | None
    fraud_indicators: list[str] | None
    fraud_risk_score: float  # 0.0 to 10.0

    # Legal Advisor Agent
    legal_implications: list[str] | None
    rights_obligations: list[dict[str, Any]] | None  # Added missing field
    compliance_issues: list[dict[str, Any]] | None   # Added missing field
    legal_advice: list[str] | None                   # Added missing field
    your_rights: list[str] | None
    their_obligations: list[str] | None
    potential_consequences: list[str] | None

    # Action Planner Agent
    immediate_actions: list[dict[str, Any]] | None   # Changed from list[str] to match agent
    long_term_actions: list[dict[str, Any]] | None   # Added missing field
    deadlines: list[dict[str, Any]] | None           # Added missing field
    recommendations: list[str] | None                # Added missing field
    before_signing: list[str] | None
    long_term_considerations: list[str] | None
    recommended_timeline: str | None

    # Document Summary fields
    summary: str | None                              # Added missing field

    # Legacy fields (for backward compatibility)
    document_type: DocumentType | None
    confidence_score: float
    legal_analysis: dict[str, Any] | None
    analysis_status: ProcessingStatus
    risks: list[Risk]
    risk_assessment_status: ProcessingStatus
    executive_summary: str | None
    key_findings: list[str]

    # Error handling
    error_message: str | None
    failed_step: str | None

    # Metadata
    processing_time: float | None
    created_at: str
    completed_at: str | None
