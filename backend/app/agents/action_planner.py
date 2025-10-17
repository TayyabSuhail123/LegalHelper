"""
Action Planner Agent - Creates specific action plans and next steps.
"""

import json
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from .base_agent import BaseAgent
from app.core.graph_state import DocumentAnalysisState, ProcessingStatus

logger = logging.getLogger(__name__)


class ActionPlannerAgent(BaseAgent):
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
        logger.info(f"ActionPlannerAgent: Starting analysis for file {state['file_id']}")
        
        try:
            state["current_step"] = "Creating action plan"
            state["progress_percentage"] = 80.0
            
            if not self._validate_document_text(state):
                return self._update_state_with_error(
                    state, 
                    "No document text available for action planning", 
                    "action_planner"
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
                    state["immediate_actions"] = result.get("immediate_actions", [])
                    state["long_term_actions"] = result.get("long_term_actions", [])
                    state["deadlines"] = result.get("deadlines", [])
                    state["recommendations"] = result.get("recommendations", [])
                    
                    logger.info(f"ActionPlannerAgent: AI analysis completed for file {state['file_id']}")
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"ActionPlannerAgent: Failed to parse AI response, using fallback: {e}")
                    self._fallback_analysis(state, document_text)
            else:
                logger.warning("ActionPlannerAgent: No AI response, using fallback analysis")
                self._fallback_analysis(state, document_text)
            
            state["progress_percentage"] = 90.0
            logger.info(f"ActionPlannerAgent: Analysis completed for file {state['file_id']}")
            
        except Exception as e:
            return self._update_state_with_error(
                state, 
                f"Action planning failed: {str(e)}", 
                "action_planner"
            )
        
        return state
    
    def _fallback_analysis(self, state: DocumentAnalysisState, document_text: str) -> None:
        """
        Fallback action planning when AI is not available.
        
        Args:
            state: Current analysis state
            document_text: Text to analyze
        """
        text = document_text.lower()
        immediate_actions = []
        long_term_actions = []
        deadlines = []
        recommendations = []
        
        # Check for signature requirements
        signature_terms = ["sign", "signature", "execute", "executed by"]
        if any(term in text for term in signature_terms):
            immediate_actions.append({
                "action": "Review document thoroughly before signing",
                "priority": "HIGH",
                "description": "Ensure you understand all terms and conditions"
            })
            immediate_actions.append({
                "action": "Verify all parties' signatures are required",
                "priority": "HIGH",
                "description": "Confirm who needs to sign and in what order"
            })
        
        # Check for payment terms
        payment_terms = ["payment", "pay", "due", "invoice", "fee", "cost"]
        if any(term in text for term in payment_terms):
            immediate_actions.append({
                "action": "Set up payment tracking system",
                "priority": "MEDIUM",
                "description": "Track payment due dates to avoid late fees"
            })
            long_term_actions.append({
                "action": "Budget for ongoing payment obligations",
                "priority": "MEDIUM",
                "description": "Ensure sufficient funds for all required payments"
            })
        
        # Check for insurance requirements
        insurance_terms = ["insurance", "insured", "coverage", "policy"]
        if any(term in text for term in insurance_terms):
            immediate_actions.append({
                "action": "Verify insurance coverage requirements",
                "priority": "HIGH",
                "description": "Ensure you have adequate insurance as specified"
            })
            long_term_actions.append({
                "action": "Review insurance policies annually",
                "priority": "LOW",
                "description": "Keep insurance coverage current and adequate"
            })
        
        # Check for compliance requirements
        compliance_terms = ["comply", "compliance", "regulation", "standard"]
        if any(term in text for term in compliance_terms):
            immediate_actions.append({
                "action": "Research applicable compliance requirements",
                "priority": "HIGH",
                "description": "Understand all regulatory obligations"
            })
            long_term_actions.append({
                "action": "Implement compliance monitoring system",
                "priority": "MEDIUM",
                "description": "Regularly check compliance status"
            })
        
        # Check for renewal/termination clauses
        renewal_terms = ["renew", "renewal", "terminate", "termination", "expire"]
        if any(term in text for term in renewal_terms):
            immediate_actions.append({
                "action": "Calendar important contract dates",
                "priority": "HIGH",
                "description": "Set reminders for renewal and termination deadlines"
            })
            long_term_actions.append({
                "action": "Review contract performance before renewal",
                "priority": "MEDIUM",
                "description": "Evaluate if contract terms should be renegotiated"
            })
        
        # Check for confidentiality/non-disclosure
        confidentiality_terms = ["confidential", "non-disclosure", "nda", "proprietary"]
        if any(term in text for term in confidentiality_terms):
            immediate_actions.append({
                "action": "Implement information security measures",
                "priority": "HIGH",
                "description": "Protect confidential information as required"
            })
            immediate_actions.append({
                "action": "Train team on confidentiality requirements",
                "priority": "MEDIUM",
                "description": "Ensure all relevant parties understand obligations"
            })
        
        # Check for intellectual property
        ip_terms = ["intellectual property", "copyright", "trademark", "patent"]
        if any(term in text for term in ip_terms):
            immediate_actions.append({
                "action": "Document existing intellectual property",
                "priority": "MEDIUM",
                "description": "Create inventory of relevant IP assets"
            })
            long_term_actions.append({
                "action": "Monitor IP usage and infringement",
                "priority": "LOW",
                "description": "Regularly check for unauthorized use"
            })
        
        # Create deadlines based on common patterns
        current_date = datetime.now()
        
        # Look for date patterns
        if "30 days" in text or "thirty days" in text:
            deadlines.append({
                "deadline": (current_date + timedelta(days=30)).strftime("%Y-%m-%d"),
                "description": "30-day deadline mentioned in document",
                "priority": "MEDIUM"
            })
        
        if "60 days" in text or "sixty days" in text:
            deadlines.append({
                "deadline": (current_date + timedelta(days=60)).strftime("%Y-%m-%d"),
                "description": "60-day deadline mentioned in document",
                "priority": "MEDIUM"
            })
        
        if "annual" in text or "yearly" in text:
            deadlines.append({
                "deadline": (current_date + timedelta(days=365)).strftime("%Y-%m-%d"),
                "description": "Annual review or renewal deadline",
                "priority": "LOW"
            })
        
        # General recommendations based on document type
        if "employment" in text or "employee" in text:
            recommendations.extend([
                "Keep detailed records of work performance and communications",
                "Understand your employee rights under local labor laws",
                "Save a copy of the employee handbook if referenced"
            ])
        
        if "lease" in text or "rental" in text:
            recommendations.extend([
                "Document property condition with photos before move-in",
                "Understand local tenant rights and landlord obligations",
                "Keep receipts for security deposits and rental payments"
            ])
        
        if "purchase" in text or "sale" in text:
            recommendations.extend([
                "Keep all purchase documentation and warranties",
                "Understand return and refund policies",
                "Research consumer protection laws in your jurisdiction"
            ])
        
        if "service" in text:
            recommendations.extend([
                "Monitor service quality and delivery timelines",
                "Keep records of all service communications",
                "Understand escalation procedures for service issues"
            ])
        
        # Default actions if nothing specific found
        if not immediate_actions:
            immediate_actions.append({
                "action": "Have document reviewed by qualified attorney",
                "priority": "HIGH",
                "description": "Professional legal review recommended"
            })
        
        if not long_term_actions:
            long_term_actions.append({
                "action": "Schedule periodic review of contract performance",
                "priority": "LOW",
                "description": "Regular evaluation ensures ongoing compliance"
            })
        
        # Add general recommendations
        recommendations.extend([
            "Keep original signed documents in a secure location",
            "Maintain organized records of all related communications",
            "Consider setting up automated reminders for important dates",
            "Review document terms if circumstances change significantly"
        ])
        
        # Update state
        state["immediate_actions"] = immediate_actions
        state["long_term_actions"] = long_term_actions
        state["deadlines"] = deadlines
        state["recommendations"] = recommendations
        
        logger.info(f"ActionPlannerAgent: Fallback analysis completed with {len(immediate_actions)} immediate actions")
