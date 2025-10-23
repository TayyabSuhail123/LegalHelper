"""
Action Planner Agent - Creates specific action plans and next steps.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from app.core.graph_state import DocumentAnalysisState

from .base_agent import BaseAnalysisAgent

logger = logging.getLogger(__name__)


class ActionPlannerAgent(BaseAnalysisAgent):
    """
    Specialized agent for creating actionable next steps and recommendations.

    This agent focuses on:
    - Immediate actions required
    - Long-term planning considerations
    - Deadlines and time-sensitive items
    - Specific recommendations
    """

    def _get_default_prompt(self) -> str:
        """Default prompt if prompt file is not available."""
        return """
        Based on this legal document analysis, create a specific action plan and next steps.
        
        Document: {document_text}
        
        Provide JSON with: immediate_actions, long_term_actions, deadlines, recommendations
        """

    async def analyze(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """
        Create action plan based on document analysis.

        Args:
            state: Current analysis state

        Returns:
            Updated state with action plan
        """
        return await self._analyze_with_llm(state, "action planning", 90.0)

    def _update_state_with_results(
        self, state: DocumentAnalysisState, results: dict[str, Any]
    ) -> DocumentAnalysisState:
        """Update state with action planning results."""
        state["immediate_actions"] = results.get("immediate_actions", [])
        state["long_term_actions"] = results.get("long_term_actions", [])
        state["deadlines"] = results.get("deadlines", [])
        state["recommendations"] = results.get("recommendations", [])
        return state

    def _get_fallback_results(self, document_text: str) -> dict[str, Any]:
        """Provide basic action planning when LLM fails."""
        text_lower = document_text.lower()

        immediate_actions = []
        long_term_actions = []
        deadlines = []
        recommendations = []

        # Time-sensitive indicators
        time_indicators = {
            "within": "Review document for time-sensitive requirements",
            "deadline": "Identify all deadlines and mark them in your calendar",
            "expire": "Note expiration dates and set reminders",
            "terminate": "Understand termination procedures and notice requirements",
            "notice": "Review all notice requirements and delivery methods",
            "signature": "Ensure all parties have signed the document",
            "effective date": "Confirm the effective date and any conditions precedent",
        }

        for indicator, action in time_indicators.items():
            if indicator in text_lower:
                immediate_actions.append(
                    {"action": action, "priority": "high", "category": "time_sensitive"}
                )

        # Payment-related actions
        payment_terms = ["payment", "pay", "fee", "invoice", "billing"]
        if any(term in text_lower for term in payment_terms):
            immediate_actions.append(
                {
                    "action": "Set up payment tracking and ensure compliance with payment terms",
                    "priority": "high",
                    "category": "financial",
                }
            )
            recommendations.append("Consider setting up automated reminders for payment due dates")

        # Legal review actions
        complex_terms = ["indemnification", "liability", "arbitration", "governing law"]
        if any(term in text_lower for term in complex_terms):
            immediate_actions.append(
                {
                    "action": "Have document reviewed by qualified legal counsel",
                    "priority": "high",
                    "category": "legal",
                }
            )

        # Insurance and risk management
        insurance_terms = ["insurance", "liability", "damage", "loss"]
        if any(term in text_lower for term in insurance_terms):
            long_term_actions.append(
                {
                    "action": "Review insurance coverage to ensure adequate protection",
                    "priority": "medium",
                    "category": "risk_management",
                    "timeframe": "within_30_days",
                }
            )

        # Compliance actions
        compliance_terms = ["comply", "regulation", "law", "requirement"]
        if any(term in text_lower for term in compliance_terms):
            immediate_actions.append(
                {
                    "action": "Create compliance checklist and monitoring procedures",
                    "priority": "high",
                    "category": "compliance",
                }
            )

        # Record keeping
        immediate_actions.append(
            {
                "action": "File document in secure location with backup copies",
                "priority": "medium",
                "category": "record_keeping",
            }
        )

        # Default deadlines based on common document types
        current_date = datetime.now()

        if "contract" in text_lower or "agreement" in text_lower:
            deadlines.append(
                {
                    "item": "Contract review period",
                    "date": (current_date + timedelta(days=7)).strftime("%Y-%m-%d"),
                    "description": "Complete thorough review of all contract terms",
                    "priority": "high",
                }
            )

        # General recommendations
        recommendations.extend(
            [
                "Keep all original documents in a secure location",
                "Create calendar reminders for important dates and deadlines",
                "Maintain detailed records of all communications related to this document",
                "Review document annually or as circumstances change",
                "Ensure all parties have current contact information",
            ]
        )

        # Long-term planning
        long_term_actions.extend(
            [
                {
                    "action": "Schedule periodic review of document terms and compliance",
                    "priority": "medium",
                    "category": "maintenance",
                    "timeframe": "quarterly",
                },
                {
                    "action": "Assess impact of document on business operations and strategy",
                    "priority": "medium",
                    "category": "strategic",
                    "timeframe": "within_60_days",
                },
            ]
        )

        return {
            "immediate_actions": immediate_actions[:10],  # Limit to 10 items
            "long_term_actions": long_term_actions[:8],  # Limit to 8 items
            "deadlines": deadlines[:5],  # Limit to 5 items
            "recommendations": recommendations[:12],  # Limit to 12 items
        }
