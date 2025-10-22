"""
LangGraph nodes for multi-agent document analysis workflow.
"""

import time
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone


from langchain_openai import ChatOpenAI

from app.core.graph_state import (
    DocumentAnalysisState, 
    ProcessingStatus, 
    DocumentType, 
    RiskLevel,
    RiskCategory,
    Risk
)
from app.services.file_processing import FileProcessingService
from app.models.file_processing import FileType
from app.core.config import settings

logger = logging.getLogger(__name__)


class DocumentAnalysisAgents:
    """Multi-agent system for specialized document analysis."""
    
    def __init__(self, file_service: FileProcessingService):
        self.file_service = file_service
        self._llm = None
    
    def _get_llm(self):
        """Get or create LLM instance."""
        if self._llm is None and settings.openai_api_key:
            try:
                self._llm = ChatOpenAI(
                    api_key=settings.openai_api_key,
                    model=settings.openai_model,
                    max_tokens=2500,  # Increased for detailed analysis
                    temperature=0.1
                )
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self._llm = None
        return self._llm
    
    async def text_extraction_node(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """
        Extract text from the uploaded document.
        """
        logger.info(f"Starting text extraction for file: {state['file_id']}")
        
        try:
            state["current_step"] = "Extracting text from document"
            state["progress_percentage"] = 20.0
            state["text_extraction_status"] = ProcessingStatus.IN_PROGRESS
            
            # Map file types
            file_type_map = {
                "pdf": FileType.PDF,
                "docx": FileType.DOCX,
                "txt": FileType.TXT
            }
            
            file_type = file_type_map.get(state["file_type"], FileType.TXT)
            
            # Save content temporarily and extract text
            temp_path = await self.file_service.storage_manager.store_temp_file(
                state["file_content"], 
                state["filename"], 
                state["file_id"]
            )
            
            # Extract text using existing service
            extracted_text = await self.file_service.extract_text(str(temp_path), file_type)
            
            state["extracted_text"] = extracted_text
            state["text_extraction_status"] = ProcessingStatus.COMPLETED
            state["progress_percentage"] = 40.0
            
            logger.info(f"Text extraction completed for file: {state['file_id']}")
            
        except Exception as e:
            logger.error(f"Text extraction failed for file {state['file_id']}: {str(e)}")
            state["text_extraction_status"] = ProcessingStatus.FAILED
            state["error_message"] = f"Text extraction failed: {str(e)}"
            state["failed_step"] = "text_extraction"
            
        return state
    
    async def document_classification_node(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """
        Classify the document type based on extracted text.
        For now, we'll use simple keyword matching. Later, we'll use AI.
        """
        logger.info(f"Starting document classification for file: {state['file_id']}")
        
        try:
            state["current_step"] = "Classifying document type"
            state["progress_percentage"] = 50.0
            
            if not state.get("extracted_text"):
                raise ValueError("No extracted text available for classification")
            
            text = state["extracted_text"]
            llm = self._get_llm()
            
            if llm:
                # AI-powered classification
                prompt = f"""
                Analyze this legal document and classify it into one of these categories:
                - CONTRACT: General contracts and agreements
                - EMPLOYMENT: Employment contracts and agreements
                - LEASE: Lease and rental agreements
                - NDA: Non-disclosure agreements
                - TERMS_OF_SERVICE: Terms of service documents
                - PRIVACY_POLICY: Privacy policy documents
                - UNKNOWN: If the document doesn't fit any category
                
                Document text (first 1000 characters):
                {text[:1000]}
                
                Respond with only the category name and confidence score (0.0-1.0) in format:
                CATEGORY_NAME,confidence_score
                """
                
                try:
                    response = await llm.ainvoke([{"role": "user", "content": prompt}])
                    result = response.content.strip().split(',')
                    
                    if len(result) == 2:
                        category_name = result[0].strip()
                        confidence = float(result[1].strip())
                        
                        # Map to enum
                        document_type = getattr(DocumentType, category_name, DocumentType.UNKNOWN)
                        
                        state["document_type"] = document_type
                        state["confidence_score"] = confidence
                        
                        logger.info(f"AI classified document as {document_type} with confidence {confidence}")
                    else:
                        raise ValueError("Invalid AI response format")
                        
                except Exception as e:
                    logger.warning(f"AI classification failed, falling back to keyword-based: {e}")
                    # Fall back to keyword-based classification
                    document_type, confidence = self._keyword_classification(text)
                    state["document_type"] = document_type
                    state["confidence_score"] = confidence
            else:
                # Keyword-based classification fallback
                document_type, confidence = self._keyword_classification(text)
                state["document_type"] = document_type
                state["confidence_score"] = confidence
            
            state["progress_percentage"] = 60.0
            
        except Exception as e:
            logger.error(f"Document classification failed for file {state['file_id']}: {str(e)}")
            state["error_message"] = f"Document classification failed: {str(e)}"
            state["failed_step"] = "document_classification"
            
        return state
    
    def _keyword_classification(self, text: str) -> tuple[DocumentType, float]:
        """Fallback keyword-based classification."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["contract", "agreement", "parties", "whereas"]):
            if "employment" in text_lower or "employee" in text_lower:
                return DocumentType.EMPLOYMENT, 0.8
            elif "lease" in text_lower or "rental" in text_lower or "tenant" in text_lower:
                return DocumentType.LEASE, 0.8
            elif "nda" in text_lower or "non-disclosure" in text_lower or "confidential" in text_lower:
                return DocumentType.NDA, 0.8
            else:
                return DocumentType.CONTRACT, 0.7
        elif any(word in text_lower for word in ["terms of service", "terms of use", "user agreement"]):
            return DocumentType.TERMS_OF_SERVICE, 0.9
        elif any(word in text_lower for word in ["privacy policy", "data collection", "personal information"]):
            return DocumentType.PRIVACY_POLICY, 0.9
        else:
            return DocumentType.UNKNOWN, 0.3
            
        return state
    
    async def legal_analysis_node(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """
        Perform AI-powered legal analysis.
        For Phase 1, this will be a simple rule-based analysis.
        """
        logger.info(f"Starting legal analysis for file: {state['file_id']}")
        
        try:
            state["current_step"] = "Analyzing legal content"
            state["progress_percentage"] = 70.0
            state["analysis_status"] = ProcessingStatus.IN_PROGRESS
            
            if not state.get("extracted_text"):
                raise ValueError("No extracted text available for analysis")
            
            text = state["extracted_text"].lower()
            
            # Simple analysis (will be replaced with LLM)
            analysis = {
                "clauses_found": [],
                "payment_terms": None,
                "termination_clause": None,
                "liability_clause": None,
                "governing_law": None,
                "renewal_terms": None
            }
            
            # Look for key clauses
            if "payment" in text:
                analysis["payment_terms"] = "Payment terms found in document"
                analysis["clauses_found"].append("payment")
            
            if "termination" in text or "terminate" in text:
                analysis["termination_clause"] = "Termination clause found"
                analysis["clauses_found"].append("termination")
            
            if "liability" in text or "liable" in text:
                analysis["liability_clause"] = "Liability clause found"
                analysis["clauses_found"].append("liability")
            
            if "governing law" in text or "jurisdiction" in text:
                analysis["governing_law"] = "Governing law clause found"
                analysis["clauses_found"].append("governing_law")
            
            if "renewal" in text or "renew" in text:
                analysis["renewal_terms"] = "Renewal terms found"
                analysis["clauses_found"].append("renewal")
            
            state["legal_analysis"] = analysis
            state["analysis_status"] = ProcessingStatus.COMPLETED
            state["progress_percentage"] = 80.0
            
            logger.info(f"Legal analysis completed for file: {state['file_id']}")
            
        except Exception as e:
            logger.error(f"Legal analysis failed for file {state['file_id']}: {str(e)}")
            state["analysis_status"] = ProcessingStatus.FAILED
            state["error_message"] = f"Legal analysis failed: {str(e)}"
            state["failed_step"] = "legal_analysis"
            
        return state
    
    async def risk_assessment_node(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """
        Assess risks based on the legal analysis.
        """
        logger.info(f"Starting risk assessment for file: {state['file_id']}")
        
        try:
            state["current_step"] = "Assessing legal risks"
            state["progress_percentage"] = 90.0
            state["risk_assessment_status"] = ProcessingStatus.IN_PROGRESS
            
            text = state.get("extracted_text", "").lower()
            risks = []
            total_risk_score = 0.0
            
            # Check for high-risk terms
            high_risk_terms = [
                ("unlimited liability", RiskCategory.LIABILITY, RiskLevel.CRITICAL, 8.0),
                ("automatic renewal", RiskCategory.OPERATIONAL, RiskLevel.HIGH, 6.0),
                ("penalty", RiskCategory.FINANCIAL, RiskLevel.HIGH, 7.0),
                ("liquidated damages", RiskCategory.FINANCIAL, RiskLevel.HIGH, 6.5),
                ("no limitation of liability", RiskCategory.LIABILITY, RiskLevel.CRITICAL, 9.0),
                ("broad confidentiality", RiskCategory.LEGAL, RiskLevel.MEDIUM, 4.0),
                ("immediate termination", RiskCategory.OPERATIONAL, RiskLevel.MEDIUM, 5.0),
            ]
            
            for term, category, level, score in high_risk_terms:
                if term in text:
                    risk = Risk(
                        category=category,
                        level=level,
                        title=f"{term.title()} Clause Found",
                        description=f"Document contains {term} which may pose {level.value} risk",
                        recommendation=f"Review {term} clause carefully with legal counsel",
                        confidence=0.8
                    )
                    risks.append(risk)
                    total_risk_score += score
            
            # Add basic risks if no specific terms found
            if not risks:
                risk = Risk(
                    category=RiskCategory.LEGAL,
                    level=RiskLevel.LOW,
                    title="Standard Legal Document",
                    description="No obvious high-risk terms detected",
                    recommendation="Standard legal review recommended",
                    confidence=0.6
                )
                risks.append(risk)
                total_risk_score = 2.0
            
            # Calculate overall risk level
            if total_risk_score >= 15:
                overall_risk_level = RiskLevel.CRITICAL
            elif total_risk_score >= 10:
                overall_risk_level = RiskLevel.HIGH
            elif total_risk_score >= 5:
                overall_risk_level = RiskLevel.MEDIUM
            else:
                overall_risk_level = RiskLevel.LOW
            
            state["risks"] = risks
            state["overall_risk_score"] = min(total_risk_score, 10.0)  # Cap at 10.0
            state["overall_risk_level"] = overall_risk_level
            state["risk_assessment_status"] = ProcessingStatus.COMPLETED
            state["progress_percentage"] = 95.0
            
            logger.info(f"Risk assessment completed for file: {state['file_id']} - Overall risk: {overall_risk_level}")
            
        except Exception as e:
            logger.error(f"Risk assessment failed for file {state['file_id']}: {str(e)}")
            state["risk_assessment_status"] = ProcessingStatus.FAILED
            state["error_message"] = f"Risk assessment failed: {str(e)}"
            state["failed_step"] = "risk_assessment"
            
        return state
    
    async def summary_generation_node(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """
        Generate executive summary and key findings.
        """
        logger.info(f"Generating summary for file: {state['file_id']}")
        
        try:
            state["current_step"] = "Generating summary"
            state["progress_percentage"] = 98.0
            
            # Generate key findings
            key_findings = []
            
            if state.get("document_type"):
                key_findings.append(f"Document type: {state['document_type'].value.replace('_', ' ').title()}")
            
            if state.get("legal_analysis", {}).get("clauses_found"):
                clauses = state["legal_analysis"]["clauses_found"]
                key_findings.append(f"Key clauses identified: {', '.join(clauses)}")
            
            if state.get("risks"):
                high_risk_count = len([r for r in state["risks"] if r["level"] in [RiskLevel.HIGH, RiskLevel.CRITICAL]])
                if high_risk_count > 0:
                    key_findings.append(f"High-risk items detected: {high_risk_count}")
                else:
                    key_findings.append("No critical risk items detected")
            
            # Generate executive summary
            doc_type = state.get("document_type", DocumentType.UNKNOWN).value.replace("_", " ").title()
            risk_level = state.get("overall_risk_level", RiskLevel.LOW).value.title()
            risk_score = state.get("overall_risk_score", 0.0)
            
            summary = f"Analysis of {doc_type} completed. "
            summary += f"Overall risk assessment: {risk_level} ({risk_score:.1f}/10.0). "
            
            if state.get("risks"):
                risk_count = len(state["risks"])
                summary += f"Identified {risk_count} risk factor(s) requiring attention. "
            
            summary += "Recommend legal review before execution."
            
            state["executive_summary"] = summary
            state["key_findings"] = key_findings
            state["progress_percentage"] = 100.0
            state["current_step"] = "Analysis completed"
            state["completed_at"] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"Summary generation completed for file: {state['file_id']}")
            
        except Exception as e:
            logger.error(f"Summary generation failed for file {state['file_id']}: {str(e)}")
            state["error_message"] = f"Summary generation failed: {str(e)}"
            state["failed_step"] = "summary_generation"
            
        return state
