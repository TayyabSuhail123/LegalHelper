"""
Multi-agent system for legal document analysis.
"""

from .base_agent import BaseAgent
from .document_summarizer import DocumentSummarizerAgent
from .risk_assessor import RiskAssessorAgent
from .fraud_detector import FraudDetectorAgent
from .legal_advisor import LegalAdvisorAgent
from .action_planner import ActionPlannerAgent

__all__ = [
    'BaseAgent',
    'DocumentSummarizerAgent',
    'RiskAssessorAgent', 
    'FraudDetectorAgent',
    'LegalAdvisorAgent',
    'ActionPlannerAgent'
]
