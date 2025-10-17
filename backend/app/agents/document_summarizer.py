"""
Document Summarizer Agent - Provides clear summaries of legal documents.
"""

import json
import logging
from typing import Dict, Any

from .base_agent import BaseAgent
from app.core.graph_state import DocumentAnalysisState, ProcessingStatus

logger = logging.getLogger(__name__)


class DocumentSummarizerAgent(BaseAgent):
    """
    Specialized agent for creating clear, accessible summaries of legal documents.
    
    This agent focuses on:
    - Document purpose and main points
    - Key parties involved
    - Important dates and deadlines
    - Plain English explanations
    """
    
    def _get_default_prompt(self) -> str:
        """Default prompt if prompt file is not available."""
        return """
        Analyze this legal document and provide a clear summary.
        
        Document: {document_text}
        
        Provide JSON with: document_summary, document_purpose, key_parties, important_dates
        """
    
    async def analyze(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """
        Analyze document and create comprehensive summary.
        
        Args:
            state: Current analysis state
            
        Returns:
            Updated state with summary information
        """
        logger.info(f"DocumentSummarizerAgent: Starting analysis for file {state['file_id']}")
        
        try:
            state["current_step"] = "Creating document summary"
            state["progress_percentage"] = 20.0
            
            if not self._validate_document_text(state):
                return self._update_state_with_error(
                    state, 
                    "No document text available for summarization", 
                    "document_summarizer"
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
                    state["document_summary"] = result.get("document_summary", "")
                    state["document_purpose"] = result.get("document_purpose", "")
                    state["key_parties"] = result.get("key_parties", [])
                    state["important_dates"] = result.get("important_dates", [])
                    
                    # Extract document type for classification (for compatibility)
                    doc_summary = result.get("document_summary", "").lower()
                    if any(word in doc_summary for word in ["contract", "agreement", "terms"]):
                        state["document_type"] = "contract"
                    elif any(word in doc_summary for word in ["lease", "rental"]):
                        state["document_type"] = "lease"
                    elif any(word in doc_summary for word in ["employment", "job", "work"]):
                        state["document_type"] = "employment"
                    elif any(word in doc_summary for word in ["nda", "confidential", "non-disclosure"]):
                        state["document_type"] = "nda"
                    else:
                        state["document_type"] = "legal_document"
                    
                    state["confidence_score"] = 0.85  # AI analysis confidence
                    
                    logger.info(f"DocumentSummarizerAgent: AI analysis completed for file {state['file_id']}")
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"DocumentSummarizerAgent: Failed to parse AI response, using fallback: {e}")
                    self._fallback_analysis(state, document_text)
            else:
                logger.warning("DocumentSummarizerAgent: No AI response, using fallback analysis")
                self._fallback_analysis(state, document_text)
            
            state["progress_percentage"] = 40.0
            logger.info(f"DocumentSummarizerAgent: Analysis completed for file {state['file_id']}")
            
        except Exception as e:
            return self._update_state_with_error(
                state, 
                f"Analysis failed: {str(e)}", 
                "document_summarizer"
            )
        
        return state
    
    def _fallback_analysis(self, state: DocumentAnalysisState, document_text: str) -> None:
        """
        Fallback analysis when AI is not available.
        
        Args:
            state: Current analysis state
            document_text: Text to analyze
        """
        text = document_text.lower()
        
        # Basic document type detection
        if any(word in text for word in ["contract", "agreement", "terms"]):
            doc_type = "legal agreement"
            doc_type_key = "contract"
        elif "lease" in text:
            doc_type = "lease agreement"
            doc_type_key = "lease"
        elif "employment" in text:
            doc_type = "employment document"
            doc_type_key = "employment"
        elif "privacy" in text:
            doc_type = "privacy policy"
            doc_type_key = "privacy_policy"
        else:
            doc_type = "legal document"
            doc_type_key = "legal_document"
        
        # Extract basic information
        state["document_summary"] = f"This appears to be a {doc_type}. The document contains legal terms and conditions that should be reviewed carefully."
        state["document_purpose"] = f"The main purpose appears to be establishing a {doc_type} between parties."
        state["document_type"] = doc_type_key
        state["confidence_score"] = 0.60  # Lower confidence for fallback analysis
        
        # Simple party detection
        parties = []
        if "company" in text or "corporation" in text:
            parties.append("Company/Corporation")
        if "user" in text or "customer" in text or "client" in text:
            parties.append("User/Customer")
        if "employee" in text:
            parties.append("Employee")
        if "tenant" in text:
            parties.append("Tenant")
        if "landlord" in text:
            parties.append("Landlord")
        
        state["key_parties"] = parties if parties else ["Multiple parties as specified in document"]
        
        # Simple date detection
        import re
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{4}-\d{2}-\d{2}',
            r'[A-Za-z]+ \d{1,2}, \d{4}'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, document_text)
            dates.extend(matches[:3])  # Limit to first 3 dates
        
        state["important_dates"] = dates if dates else ["Dates specified within document"]
        
        logger.info("DocumentSummarizerAgent: Fallback analysis completed")
