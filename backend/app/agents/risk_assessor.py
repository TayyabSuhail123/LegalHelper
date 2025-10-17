"""
Risk Assessor Agent - Identifies legal risks and potential liabilities.
"""

import json
import logging
from typing import Dict, Any, List

from .base_agent import BaseAgent
from app.core.graph_state import DocumentAnalysisState, ProcessingStatus

logger = logging.getLogger(__name__)


class RiskAssessorAgent(BaseAgent):
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
        logger.info(f"RiskAssessorAgent: Starting analysis for file {state['file_id']}")
        
        try:
            state["current_step"] = "Assessing legal risks"
            state["progress_percentage"] = 50.0
            
            if not self._validate_document_text(state):
                return self._update_state_with_error(
                    state, 
                    "No document text available for risk assessment", 
                    "risk_assessor"
                )
            
            document_text = state["extracted_text"]
            
            # Load prompt and call LLM
            prompt = self._load_prompt()
            llm_response = await self._call_llm(prompt, document_text)
            
            if llm_response:
                try:
                    # Parse JSON response
                    result = json.loads(llm_response)
                    
                    # Update state with AI results
                    state["legal_risks"] = result.get("legal_risks", [])
                    state["potential_liabilities"] = result.get("potential_liabilities", [])
                    state["overall_risk_score"] = min(result.get("overall_risk_score", 5.0), 10.0)
                    state["overall_risk_level"] = result.get("overall_risk_level", "MEDIUM")
                    
                    logger.info(f"RiskAssessorAgent: AI analysis completed for file {state['file_id']}")
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"RiskAssessorAgent: Failed to parse AI response, using fallback: {e}")
                    self._fallback_analysis(state, document_text)
            else:
                logger.warning("RiskAssessorAgent: No AI response, using fallback analysis")
                self._fallback_analysis(state, document_text)
            
            state["progress_percentage"] = 70.0
            logger.info(f"RiskAssessorAgent: Analysis completed for file {state['file_id']}")
            
        except Exception as e:
            return self._update_state_with_error(
                state, 
                f"Risk assessment failed: {str(e)}", 
                "risk_assessor"
            )
        
        return state
    
    def _fallback_analysis(self, state: DocumentAnalysisState, document_text: str) -> None:
        """
        Fallback risk analysis when AI is not available.
        
        Args:
            state: Current analysis state
            document_text: Text to analyze
        """
        text = document_text.lower()
        risks = []
        total_risk_score = 0.0
        
        # High-risk terms and their risk scores
        high_risk_terms = {
            "unlimited liability": {"category": "legal", "severity": "CRITICAL", "score": 8.0},
            "automatic renewal": {"category": "operational", "severity": "HIGH", "score": 6.0},
            "penalty": {"category": "financial", "severity": "HIGH", "score": 7.0},
            "liquidated damages": {"category": "financial", "severity": "HIGH", "score": 6.5},
            "no limitation": {"category": "legal", "severity": "CRITICAL", "score": 9.0},
            "immediate termination": {"category": "operational", "severity": "MEDIUM", "score": 5.0},
            "indemnify": {"category": "legal", "severity": "HIGH", "score": 7.5},
            "hold harmless": {"category": "legal", "severity": "HIGH", "score": 7.0},
            "waive": {"category": "legal", "severity": "MEDIUM", "score": 4.5},
        }
        
        # Check for high-risk terms
        for term, risk_info in high_risk_terms.items():
            if term in text:
                risk = {
                    "category": risk_info["category"],
                    "severity": risk_info["severity"],
                    "description": f"Document contains '{term}' clause which may create {risk_info['severity'].lower()} risk",
                    "recommendation": f"Carefully review the '{term}' clause with legal counsel"
                }
                risks.append(risk)
                total_risk_score += risk_info["score"]
        
        # Check for specific risky patterns
        risky_patterns = [
            ("payment", "financial", "MEDIUM", 3.0, "payment obligations"),
            ("fee", "financial", "MEDIUM", 2.5, "additional fees"),
            ("breach", "legal", "HIGH", 5.5, "breach consequences"),
            ("default", "legal", "HIGH", 5.0, "default provisions"),
            ("force majeure", "operational", "LOW", 2.0, "force majeure clauses"),
        ]
        
        for pattern, category, severity, score, description in risky_patterns:
            if pattern in text and not any(r["description"].startswith(f"Document contains '{pattern}'") for r in risks):
                risk = {
                    "category": category,
                    "severity": severity, 
                    "description": f"Document contains {description} that should be reviewed",
                    "recommendation": f"Review {description} carefully"
                }
                risks.append(risk)
                total_risk_score += score
        
        # Add default risk if none found
        if not risks:
            risk = {
                "category": "general",
                "severity": "LOW",
                "description": "Standard legal document - no obvious high-risk terms detected",
                "recommendation": "Standard legal review recommended before signing"
            }
            risks.append(risk)
            total_risk_score = 2.0
        
        # Determine overall risk level
        if total_risk_score >= 15:
            overall_risk_level = "CRITICAL"
        elif total_risk_score >= 10:
            overall_risk_level = "HIGH"
        elif total_risk_score >= 5:
            overall_risk_level = "MEDIUM"
        else:
            overall_risk_level = "LOW"
        
        # Update state
        state["legal_risks"] = risks
        state["potential_liabilities"] = [
            "Legal obligations as specified in the document",
            "Financial responsibilities outlined in terms",
            "Compliance requirements mentioned"
        ]
        state["overall_risk_score"] = min(total_risk_score, 10.0)
        state["overall_risk_level"] = overall_risk_level
        
        logger.info(f"RiskAssessorAgent: Fallback analysis completed - Risk Level: {overall_risk_level}")
