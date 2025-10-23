"""
Multi-agent system for legal document analysis.
"""

from .action_planner import ActionPlannerAgent
from .base_agent import BaseAnalysisAgent
from .document_summarizer import DocumentSummarizerAgent
from .fraud_detector import FraudDetectorAgent
from .legal_advisor import LegalAdvisorAgent
from .risk_assessor import RiskAssessorAgent

__all__ = [
    "BaseAnalysisAgent",
    "DocumentSummarizerAgent",
    "RiskAssessorAgent",
    "FraudDetectorAgent",
    "LegalAdvisorAgent",
    "ActionPlannerAgent",
]
