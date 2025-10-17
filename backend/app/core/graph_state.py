"""
LangGraph state definitions for document analysis workflow.
"""

from typing import TypedDict, Optional, Dict, Any, List
from enum import Enum


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
    extracted_text: Optional[str]
    text_extraction_status: ProcessingStatus
    
    # Multi-Agent Analysis Results
    # Document Summarizer Agent
    document_summary: Optional[str]
    document_purpose: Optional[str]
    key_parties: Optional[List[str]]
    important_dates: Optional[List[str]]
    
    # Risk Assessment Agent
    legal_risks: Optional[List[Dict[str, Any]]]
    potential_liabilities: Optional[List[str]]
    overall_risk_score: float  # 0.0 to 10.0
    overall_risk_level: Optional[RiskLevel]
    
    # Fraud Detection Agent
    suspicious_clauses: Optional[List[Dict[str, Any]]]
    hidden_fees: Optional[List[str]]
    fraud_indicators: Optional[List[str]]
    fraud_risk_score: float  # 0.0 to 10.0
    
    # Legal Advisor Agent
    legal_implications: Optional[List[str]]
    your_rights: Optional[List[str]]
    their_obligations: Optional[List[str]]
    potential_consequences: Optional[List[str]]
    
    # Action Planner Agent
    immediate_actions: Optional[List[str]]
    before_signing: Optional[List[str]]
    long_term_considerations: Optional[List[str]]
    recommended_timeline: Optional[str]
    
    # Legacy fields (for backward compatibility)
    document_type: Optional[DocumentType]
    confidence_score: float
    legal_analysis: Optional[Dict[str, Any]]
    analysis_status: ProcessingStatus
    risks: List[Risk]
    risk_assessment_status: ProcessingStatus
    executive_summary: Optional[str]
    key_findings: List[str]
    
    # Error handling
    error_message: Optional[str]
    failed_step: Optional[str]
    
    # Metadata
    processing_time: Optional[float]
    created_at: str
    completed_at: Optional[str]
