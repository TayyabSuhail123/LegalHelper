"""
Legal Advisor Agent - Provides specific legal advice and implications.
"""

import logging
from typing import Any

from app.core.graph_state import DocumentAnalysisState

from .base_agent import BaseAnalysisAgent

logger = logging.getLogger(__name__)


class LegalAdvisorAgent(BaseAnalysisAgent):
    """
    Specialized agent for providing legal advice and implications.

    This agent focuses on:
    - Legal implications of document terms
    - Rights and obligations analysis
    - Compliance considerations
    - Legal precedents and concerns
    """

    def _get_default_prompt(self) -> str:
        """Default prompt if prompt file is not available."""
        return """
        Analyze this legal document and provide specific legal advice and implications.
        
        Document: {document_text}
        
        Provide JSON with: legal_implications, rights_obligations, compliance_issues, legal_advice
        """

    async def analyze(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """
        Analyze document for legal implications and provide advice.

        Args:
            state: Current analysis state

        Returns:
            Updated state with legal analysis results
        """
        return await self._analyze_with_llm(state, "legal analysis", 80.0)

    def _update_state_with_results(
        self, state: DocumentAnalysisState, results: dict[str, Any]
    ) -> DocumentAnalysisState:
        """Update state with legal analysis results."""
        state["legal_implications"] = results.get("legal_implications", [])
        state["rights_obligations"] = results.get("rights_obligations", [])
        state["compliance_issues"] = results.get("compliance_issues", [])
        state["legal_advice"] = results.get("legal_advice", [])
        return state

    def _get_fallback_results(self, document_text: str) -> dict[str, Any]:
        """Provide basic legal analysis when LLM fails."""
        text_lower = document_text.lower()

        legal_implications = []
        rights_obligations = []
        compliance_issues = []
        legal_advice = []

        # Check for key legal terms
        legal_terms = {
            "liability": "Document contains liability provisions that may limit your rights",
            "warranty": "Warranty terms that affect product guarantees and remedies",
            "termination": "Termination clauses that specify when agreement ends",
            "jurisdiction": "Legal jurisdiction and governing law considerations",
            "arbitration": "Dispute resolution through arbitration rather than courts",
            "indemnification": "Indemnification clauses that may require you to cover costs",
            "intellectual property": "Intellectual property rights and restrictions",
            "confidentiality": "Confidentiality obligations that restrict information sharing",
        }

        for term, implication in legal_terms.items():
            if term in text_lower:
                legal_implications.append(
                    {"term": term, "implication": implication, "severity": "medium"}
                )

        # Check for rights and obligations
        obligation_keywords = ["must", "shall", "required", "obligation", "duty", "liable"]
        rights_keywords = ["may", "entitled", "right", "privilege", "authorized"]

        lines = document_text.split(".")
        for line in lines[:20]:  # Check first 20 sentences
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in obligation_keywords):
                if len(line.strip()) > 20:  # Meaningful sentence
                    rights_obligations.append(
                        {
                            "type": "obligation",
                            "description": line.strip()[:200],  # Limit length
                            "importance": "medium",
                        }
                    )
            elif any(keyword in line_lower for keyword in rights_keywords):
                if len(line.strip()) > 20:  # Meaningful sentence
                    rights_obligations.append(
                        {
                            "type": "right",
                            "description": line.strip()[:200],  # Limit length
                            "importance": "medium",
                        }
                    )

        # Check for compliance issues
        compliance_keywords = ["regulation", "compliance", "law", "statute", "code", "requirement"]
        for keyword in compliance_keywords:
            if keyword in text_lower:
                compliance_issues.append(
                    {
                        "area": keyword,
                        "description": f"Document references {keyword} - review for compliance requirements",
                        "priority": "medium",
                    }
                )

        # Provide basic legal advice
        legal_advice = [
            "Review all terms carefully before signing or agreeing",
            "Consider consulting with a qualified attorney for complex agreements",
            "Pay special attention to liability, termination, and dispute resolution clauses",
            "Ensure you understand all rights and obligations before proceeding",
        ]

        # Add specific advice based on detected terms
        if "arbitration" in text_lower:
            legal_advice.append(
                "This document includes arbitration clauses - understand your dispute resolution options"
            )

        if "liability" in text_lower:
            legal_advice.append(
                "Review liability limitations carefully - they may restrict your remedies"
            )

        if "termination" in text_lower:
            legal_advice.append("Check termination procedures and notice requirements")

        return {
            "legal_implications": legal_implications[:10],  # Limit to 10 items
            "rights_obligations": rights_obligations[:15],  # Limit to 15 items
            "compliance_issues": compliance_issues[:10],  # Limit to 10 items
            "legal_advice": legal_advice[:10],  # Limit to 10 items
        }
