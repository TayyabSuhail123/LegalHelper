"""
Legal Advisor Agent - Provides specific legal advice and implications.
"""

import json
import logging
from typing import Dict, Any, List

from .base_agent import BaseAgent
from app.core.graph_state import DocumentAnalysisState, ProcessingStatus

logger = logging.getLogger(__name__)


class LegalAdvisorAgent(BaseAgent):
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
            Updated state with legal advice
        """
        logger.info(f"LegalAdvisorAgent: Starting analysis for file {state['file_id']}")
        
        try:
            state["current_step"] = "Analyzing legal implications"
            state["progress_percentage"] = 70.0
            
            if not self._validate_document_text(state):
                return self._update_state_with_error(
                    state, 
                    "No document text available for legal analysis", 
                    "legal_advisor"
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
                    state["legal_implications"] = result.get("legal_implications", [])
                    state["rights_obligations"] = result.get("rights_obligations", {})
                    state["compliance_issues"] = result.get("compliance_issues", [])
                    state["legal_advice"] = result.get("legal_advice", [])
                    
                    logger.info(f"LegalAdvisorAgent: AI analysis completed for file {state['file_id']}")
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"LegalAdvisorAgent: Failed to parse AI response, using fallback: {e}")
                    self._fallback_analysis(state, document_text)
            else:
                logger.warning("LegalAdvisorAgent: No AI response, using fallback analysis")
                self._fallback_analysis(state, document_text)
            
            state["progress_percentage"] = 80.0
            logger.info(f"LegalAdvisorAgent: Analysis completed for file {state['file_id']}")
            
        except Exception as e:
            return self._update_state_with_error(
                state, 
                f"Legal analysis failed: {str(e)}", 
                "legal_advisor"
            )
        
        return state
    
    def _fallback_analysis(self, state: DocumentAnalysisState, document_text: str) -> None:
        """
        Fallback legal analysis when AI is not available.
        
        Args:
            state: Current analysis state
            document_text: Text to analyze
        """
        text = document_text.lower()
        legal_implications = []
        rights_obligations = {"your_rights": [], "your_obligations": [], "other_party_rights": [], "other_party_obligations": []}
        compliance_issues = []
        legal_advice = []
        
        # Common legal terms and their implications
        legal_patterns = {
            "liquidated damages": {
                "implication": "You may be required to pay predetermined damages for breach",
                "advice": "Ensure damage amounts are reasonable and enforceable"
            },
            "indemnification": {
                "implication": "You may be responsible for defending/paying claims against the other party",
                "advice": "Review indemnification scope carefully - it can be very costly"
            },
            "force majeure": {
                "implication": "Contract performance may be excused during extraordinary circumstances",
                "advice": "Understand what events are covered and notification requirements"
            },
            "governing law": {
                "implication": "Disputes will be resolved under specific state/country laws",
                "advice": "Consider if the governing law is favorable to your situation"
            },
            "arbitration": {
                "implication": "Disputes must be resolved through arbitration, not court",
                "advice": "You may waive your right to jury trial and class action suits"
            },
            "non-disclosure": {
                "implication": "You are legally bound to keep certain information confidential",
                "advice": "Understand what information is confidential and time limits"
            },
            "non-compete": {
                "implication": "You may be restricted from competing with the other party",
                "advice": "Ensure restrictions are reasonable in scope, time, and geography"
            }
        }
        
        for pattern, info in legal_patterns.items():
            if pattern in text:
                legal_implications.append(info["implication"])
                legal_advice.append(f"{pattern.title()}: {info['advice']}")
        
        # Check for termination clauses
        termination_terms = ["terminate", "termination", "end this agreement", "cancel"]
        if any(term in text for term in termination_terms):
            legal_implications.append("Contract contains termination provisions")
            legal_advice.append("Review termination procedures and notice requirements carefully")
        
        # Check for payment obligations
        payment_terms = ["payment", "pay", "fee", "cost", "charge", "invoice"]
        if any(term in text for term in payment_terms):
            rights_obligations["your_obligations"].append("Payment obligations specified in document")
            legal_advice.append("Ensure you understand all payment terms and due dates")
        
        # Check for warranty disclaimers
        warranty_terms = ["warranty", "guarantee", "as is", "without warranty"]
        if any(term in text for term in warranty_terms):
            legal_implications.append("Document contains warranty provisions or disclaimers")
            legal_advice.append("Understand what warranties are provided or disclaimed")
        
        # Check for limitation of liability
        liability_terms = ["limitation of liability", "limit liability", "not liable", "exclude liability"]
        if any(term in text for term in liability_terms):
            legal_implications.append("Liability may be limited or excluded")
            legal_advice.append("Consider whether liability limitations are acceptable for your situation")
        
        # Check for intellectual property clauses
        ip_terms = ["intellectual property", "copyright", "trademark", "patent", "trade secret"]
        if any(term in text for term in ip_terms):
            legal_implications.append("Intellectual property rights are addressed")
            legal_advice.append("Understand who owns what intellectual property and usage rights")
        
        # Check for compliance requirements
        compliance_terms = ["comply", "compliance", "regulation", "law", "legal requirement"]
        if any(term in text for term in compliance_terms):
            compliance_issues.append("Document references compliance obligations")
            legal_advice.append("Ensure you can meet all compliance requirements mentioned")
        
        # Check for duration and renewal
        duration_terms = ["term", "duration", "expire", "renew", "renewal"]
        if any(term in text for term in duration_terms):
            legal_implications.append("Contract has specific duration and renewal terms")
            legal_advice.append("Note contract duration and any automatic renewal provisions")
        
        # General rights based on document type
        if "employment" in text or "employee" in text:
            rights_obligations["your_rights"].append("Employment rights as defined by law")
            legal_advice.append("Review employment terms against local labor laws")
        
        if "lease" in text or "rent" in text:
            rights_obligations["your_rights"].append("Tenant rights under applicable landlord-tenant law")
            legal_advice.append("Understand your rights and obligations as a tenant")
        
        if "purchase" in text or "sale" in text:
            rights_obligations["your_rights"].append("Consumer protection rights may apply")
            legal_advice.append("Review return policies and warranty protections")
        
        # Default analysis if no specific terms found
        if not legal_implications:
            legal_implications.append("Document creates legal obligations that should be carefully reviewed")
            legal_advice.append("Consider having this document reviewed by a qualified attorney")
        
        # Add general legal advice
        legal_advice.extend([
            "Keep a signed copy of this document for your records",
            "If you don't understand any terms, seek legal counsel before signing",
            "Consider the long-term implications of all obligations you're undertaking"
        ])
        
        # Update state
        state["legal_implications"] = legal_implications
        state["rights_obligations"] = rights_obligations
        state["compliance_issues"] = compliance_issues
        state["legal_advice"] = legal_advice
        
        logger.info(f"LegalAdvisorAgent: Fallback analysis completed with {len(legal_implications)} implications")
