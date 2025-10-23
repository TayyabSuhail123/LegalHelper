"""
Risk Assessor Agent - Identifies legal risks and potential liabilities.
"""

import logging
from typing import Dict, Any, List

from .base_agent import BaseAnalysisAgent
from app.core.graph_state import DocumentAnalysisState, ProcessingStatus

logger = logging.getLogger(__name__)


class RiskAssessorAgent(BaseAnalysisAgent):
    """
    Specialized agent for identifying legal risks and liabilities.
    
    This agent focuses on:
    - Financial risks and penalties
    - Legal liability exposure
    - Unfavorable terms and conditions
    - Compliance and regulatory risks
    """
    
    def _get_default_prompt(self) -> str:
        """Default prompt if prompt file is not available."""
        return """
        Analyze this legal document for potential risks and liabilities.
        
        Document: {document_text}
        
        Provide JSON with: legal_risks, potential_liabilities, overall_risk_score, overall_risk_level
        """
    
    async def analyze(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """
        Analyze document for legal risks and liabilities.
        
        Args:
            state: Current analysis state
            
        Returns:
            Updated state with risk assessment
        """
        return await self._analyze_with_llm(state, "risk assessment", 50.0)
    
    def _update_state_with_results(self, state: DocumentAnalysisState, results: Dict[str, Any]) -> DocumentAnalysisState:
        """Update state with risk assessment results."""
        state["legal_risks"] = results.get("legal_risks", [])
        state["potential_liabilities"] = results.get("potential_liabilities", [])
        state["overall_risk_score"] = min(results.get("overall_risk_score", 5.0), 10.0)
        state["overall_risk_level"] = results.get("overall_risk_level", "MEDIUM")
        return state
    
    def _get_fallback_results(self, document_text: str) -> Dict[str, Any]:
        """Provide basic risk analysis when LLM fails."""
        text_lower = document_text.lower()
        
        # Basic risk indicators
        high_risk_keywords = [
            "penalty", "fine", "liquidated damages", "termination without cause",
            "indemnification", "liability", "unlimited liability", "personal guarantee"
        ]
        
        medium_risk_keywords = [
            "breach", "default", "suspension", "confidentiality", "non-compete",
            "exclusive", "irrevocable", "waiver", "limitation of liability"
        ]
        
        # Count risk indicators
        high_risk_count = sum(1 for keyword in high_risk_keywords if keyword in text_lower)
        medium_risk_count = sum(1 for keyword in medium_risk_keywords if keyword in text_lower)
        
        # Calculate risk score and level
        risk_score = min(high_risk_count * 2 + medium_risk_count * 1, 10)
        
        if risk_score >= 8:
            risk_level = "HIGH"
        elif risk_score >= 5:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Generate basic risk list
        legal_risks = []
        if "penalty" in text_lower or "fine" in text_lower:
            legal_risks.append({
                "category": "FINANCIAL",
                "level": "HIGH",
                "description": "Document contains penalty or fine provisions"
            })
        
        if "liability" in text_lower:
            legal_risks.append({
                "category": "LIABILITY", 
                "level": "MEDIUM",
                "description": "Document contains liability provisions"
            })
            
        if "termination" in text_lower:
            legal_risks.append({
                "category": "OPERATIONAL",
                "level": "MEDIUM", 
                "description": "Document contains termination clauses"
            })
        
        # Basic liability assessment
        potential_liabilities = []
        if "indemnif" in text_lower:
            potential_liabilities.append("Indemnification obligations")
        if "breach" in text_lower:
            potential_liabilities.append("Potential breach consequences")
        if "damage" in text_lower:
            potential_liabilities.append("Damage-related liabilities")
        
        return {
            "legal_risks": legal_risks,
            "potential_liabilities": potential_liabilities,
            "overall_risk_score": risk_score,
            "overall_risk_level": risk_level
        }
