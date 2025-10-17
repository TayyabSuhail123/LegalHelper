"""
Fraud Detector Agent - Identifies suspicious clauses and potential fraud indicators.
"""

import json
import logging
from typing import Dict, Any, List

from .base_agent import BaseAgent
from app.core.graph_state import DocumentAnalysisState, ProcessingStatus

logger = logging.getLogger(__name__)


class FraudDetectorAgent(BaseAgent):
    """
    Specialized agent for detecting fraud indicators and suspicious clauses.
    
    This agent focuses on:
    - Hidden fees and charges
    - Deceptive language and terms
    - Clauses that seem too good to be true
    - Suspicious payment or renewal terms
    """
    
    def _get_default_prompt(self) -> str:
        """Default prompt if prompt file is not available."""
        return """
        Analyze this legal document for fraud indicators and suspicious clauses.
        
        Document: {document_text}
        
        Provide JSON with: suspicious_clauses, hidden_fees, fraud_indicators, fraud_risk_score
        """
    
    async def analyze(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """
        Analyze document for fraud indicators and suspicious elements.
        
        Args:
            state: Current analysis state
            
        Returns:
            Updated state with fraud detection results
        """
        logger.info(f"FraudDetectorAgent: Starting analysis for file {state['file_id']}")
        
        try:
            state["current_step"] = "Detecting fraud indicators"
            state["progress_percentage"] = 60.0
            
            if not self._validate_document_text(state):
                return self._update_state_with_error(
                    state, 
                    "No document text available for fraud detection", 
                    "fraud_detector"
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
                    state["suspicious_clauses"] = result.get("suspicious_clauses", [])
                    state["hidden_fees"] = result.get("hidden_fees", [])
                    state["fraud_indicators"] = result.get("fraud_indicators", [])
                    state["fraud_risk_score"] = min(result.get("fraud_risk_score", 2.0), 10.0)
                    
                    logger.info(f"FraudDetectorAgent: AI analysis completed for file {state['file_id']}")
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"FraudDetectorAgent: Failed to parse AI response, using fallback: {e}")
                    self._fallback_analysis(state, document_text)
            else:
                logger.warning("FraudDetectorAgent: No AI response, using fallback analysis")
                self._fallback_analysis(state, document_text)
            
            state["progress_percentage"] = 70.0
            logger.info(f"FraudDetectorAgent: Analysis completed for file {state['file_id']}")
            
        except Exception as e:
            return self._update_state_with_error(
                state, 
                f"Fraud detection failed: {str(e)}", 
                "fraud_detector"
            )
        
        return state
    
    def _fallback_analysis(self, state: DocumentAnalysisState, document_text: str) -> None:
        """
        Fallback fraud analysis when AI is not available.
        
        Args:
            state: Current analysis state
            document_text: Text to analyze
        """
        text = document_text.lower()
        suspicious_clauses = []
        hidden_fees = []
        fraud_indicators = []
        fraud_score = 0.0
        
        # Check for suspicious terms and patterns
        suspicious_patterns = {
            "free trial": {
                "concern": "Often leads to automatic billing",
                "severity": "MEDIUM",
                "score": 3.0
            },
            "limited time": {
                "concern": "Pressure tactic to rush decisions",
                "severity": "LOW",
                "score": 2.0
            },
            "act now": {
                "concern": "High-pressure sales tactic",
                "severity": "MEDIUM",
                "score": 3.5
            },
            "guaranteed": {
                "concern": "Unrealistic promises may be misleading",
                "severity": "MEDIUM",
                "score": 2.5
            },
            "risk free": {
                "concern": "Claims that seem too good to be true",
                "severity": "MEDIUM",
                "score": 3.0
            },
            "no obligation": {
                "concern": "May hide automatic renewals or charges",
                "severity": "MEDIUM",
                "score": 2.5
            }
        }
        
        for pattern, info in suspicious_patterns.items():
            if pattern in text:
                clause = {
                    "clause": f"Contains '{pattern}' language",
                    "concern": info["concern"],
                    "severity": info["severity"]
                }
                suspicious_clauses.append(clause)
                fraud_score += info["score"]
        
        # Check for hidden fee indicators
        fee_indicators = [
            "processing fee", "handling fee", "administrative fee",
            "convenience fee", "service charge", "additional charges",
            "plus applicable", "fees may apply", "charges may vary"
        ]
        
        for fee_term in fee_indicators:
            if fee_term in text:
                hidden_fees.append(f"Potential {fee_term} mentioned in document")
                fraud_score += 1.5
        
        # Check for automatic renewal red flags
        auto_renewal_flags = [
            "automatic renewal", "auto-renew", "automatically renew",
            "unless cancelled", "continuous service", "evergreen clause"
        ]
        
        for flag in auto_renewal_flags:
            if flag in text:
                fraud_indicators.append(f"Automatic renewal detected: {flag}")
                fraud_score += 2.0
        
        # Check for payment red flags
        payment_flags = [
            "irreversible", "non-refundable", "immediate payment",
            "upfront payment", "advance payment", "payment in full"
        ]
        
        for flag in payment_flags:
            if flag in text:
                fraud_indicators.append(f"Payment concern: {flag}")
                fraud_score += 1.0
        
        # Check for overly complex language
        if len(document_text) > 5000:  # Long document
            complex_terms = ["heretofore", "whereas", "notwithstanding", "pursuant to"]
            complex_count = sum(1 for term in complex_terms if term in text)
            if complex_count > 5:
                fraud_indicators.append("Document contains excessive legal jargon that may obscure important terms")
                fraud_score += 1.5
        
        # Default analysis if nothing suspicious found
        if not suspicious_clauses and not hidden_fees and not fraud_indicators:
            fraud_indicators.append("No obvious fraud indicators detected in initial analysis")
            fraud_score = 1.0
        
        # Update state
        state["suspicious_clauses"] = suspicious_clauses
        state["hidden_fees"] = hidden_fees
        state["fraud_indicators"] = fraud_indicators
        state["fraud_risk_score"] = min(fraud_score, 10.0)
        
        logger.info(f"FraudDetectorAgent: Fallback analysis completed - Fraud Score: {fraud_score:.1f}")
