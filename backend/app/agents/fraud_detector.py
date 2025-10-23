"""
Fraud Detector Agent - Identifies suspicious clauses and potential fraud indicators.
"""

import logging
from typing import Any

from app.core.graph_state import DocumentAnalysisState

from .base_agent import BaseAnalysisAgent

logger = logging.getLogger(__name__)


class FraudDetectorAgent(BaseAnalysisAgent):
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
        return await self._analyze_with_llm(state, "fraud detection", 60.0)

    def _update_state_with_results(
        self, state: DocumentAnalysisState, results: dict[str, Any]
    ) -> DocumentAnalysisState:
        """Update state with fraud detection results."""
        state["suspicious_clauses"] = results.get("suspicious_clauses", [])
        state["hidden_fees"] = results.get("hidden_fees", [])
        state["fraud_indicators"] = results.get("fraud_indicators", [])
        state["fraud_risk_score"] = min(results.get("fraud_risk_score", 0.0), 10.0)
        return state

    def _get_fallback_results(self, document_text: str) -> dict[str, Any]:
        """Provide basic fraud detection when LLM fails."""
        text_lower = document_text.lower()

        # Basic fraud indicators
        fraud_keywords = [
            "guaranteed",
            "risk-free",
            "no hidden fees",
            "free trial",
            "cancel anytime",
            "limited time",
            "act now",
            "exclusive offer",
        ]

        suspicious_clauses = []
        hidden_fees = []
        fraud_indicators = []

        # Check for suspicious language
        for keyword in fraud_keywords:
            if keyword in text_lower:
                fraud_indicators.append(
                    f"Document contains potentially deceptive language: '{keyword}'"
                )

        # Check for fee-related terms that might indicate hidden costs
        fee_terms = ["fee", "charge", "cost", "payment", "billing"]
        lines = document_text.split("\n")

        for line in lines:
            line_lower = line.lower()
            if any(term in line_lower for term in fee_terms):
                if any(
                    suspicious in line_lower for suspicious in ["additional", "extra", "penalty"]
                ):
                    hidden_fees.append(line.strip()[:200])  # Limit length

        # Check for suspicious clauses
        suspicious_patterns = ["auto-renew", "automatically", "binding", "irrevocable"]
        for pattern in suspicious_patterns:
            if pattern in text_lower:
                suspicious_clauses.append(
                    {
                        "type": "automatic_renewal" if "auto" in pattern else "binding_clause",
                        "description": f"Document contains {pattern} clause",
                        "risk_level": "medium",
                    }
                )

        # Calculate fraud risk score
        fraud_score = (
            len(fraud_indicators) * 0.5 + len(hidden_fees) * 1.0 + len(suspicious_clauses) * 1.5
        )
        fraud_score = min(fraud_score, 10.0)

        return {
            "suspicious_clauses": suspicious_clauses,
            "hidden_fees": hidden_fees[:5],  # Limit to 5 items
            "fraud_indicators": fraud_indicators[:10],  # Limit to 10 items
            "fraud_risk_score": fraud_score,
        }
