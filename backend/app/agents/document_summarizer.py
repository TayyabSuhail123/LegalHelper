"""
Document Summarizer Agent - Provides clear summaries of legal documents.
"""

import logging
from typing import Dict, Any

from .base_agent import BaseAnalysisAgent
from app.core.graph_state import DocumentAnalysisState, ProcessingStatus

logger = logging.getLogger(__name__)


class DocumentSummarizerAgent(BaseAnalysisAgent):
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
        return await self._analyze_with_llm(state, "document summarization", 20.0)
    
    def _update_state_with_results(self, state: DocumentAnalysisState, results: Dict[str, Any]) -> DocumentAnalysisState:
        """Update state with document summarizer results."""
        # Update state with AI results
        state["document_summary"] = results.get("document_summary", "")
        state["document_purpose"] = results.get("document_purpose", "")
        state["key_parties"] = results.get("key_parties", [])
        state["important_dates"] = results.get("important_dates", [])
        
        # Extract document type for classification (for compatibility)
        doc_summary = results.get("document_summary", "").lower()
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
        
        return state
    
    def _get_fallback_results(self, document_text: str) -> Dict[str, Any]:
        """Provide basic rule-based analysis when LLM fails."""
        # Basic text analysis without AI
        text_lower = document_text.lower()
        
        # Simple document type detection
        if any(word in text_lower for word in ["contract", "agreement", "terms"]):
            doc_type = "contract"
            purpose = "Legal agreement between parties"
        elif any(word in text_lower for word in ["lease", "rental", "rent"]):
            doc_type = "lease"
            purpose = "Property rental agreement"
        elif any(word in text_lower for word in ["employment", "job", "work", "employee"]):
            doc_type = "employment"
            purpose = "Employment-related document"
        elif any(word in text_lower for word in ["nda", "confidential", "non-disclosure", "confidentiality"]):
            doc_type = "nda"
            purpose = "Non-disclosure agreement"
        else:
            doc_type = "legal_document"
            purpose = "Legal document requiring review"
        
        # Extract potential parties (very basic)
        parties = []
        party_indicators = ["party", "company", "corporation", "llc", "inc", "ltd"]
        lines = document_text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if any(indicator in line.lower() for indicator in party_indicators):
                parties.append(line.strip()[:100])  # Limit length
        
        # Basic date extraction (simplified)
        import re
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
        dates = re.findall(date_pattern, document_text)
        
        return {
            "document_summary": f"This appears to be a {doc_type.replace('_', ' ')} document.",
            "document_purpose": purpose,
            "key_parties": parties[:3],  # Limit to 3 parties
            "important_dates": dates[:5]  # Limit to 5 dates
        }
