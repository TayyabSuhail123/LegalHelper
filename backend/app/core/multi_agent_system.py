"""
Multi-Agent System for Specialized Legal Document Analysis.
Uses organized agent architecture with individual agent files and prompts.
"""

import logging
from typing import Dict, Any, List

from app.core.graph_state import DocumentAnalysisState, ProcessingStatus
from app.core.file_processing import FileProcessingService
from app.agents.document_summarizer import DocumentSummarizerAgent
from app.agents.risk_assessor import RiskAssessorAgent
from app.agents.fraud_detector import FraudDetectorAgent
from app.agents.legal_advisor import LegalAdvisorAgent
from app.agents.action_planner import ActionPlannerAgent

logger = logging.getLogger(__name__)


class LegalAnalysisAgents:
    """Organized multi-agent system using specialized agent classes."""
    
    def __init__(self, file_service: FileProcessingService):
        self.file_service = file_service
        
        # Initialize specialized agents
        self.document_summarizer = DocumentSummarizerAgent()
        self.risk_assessor = RiskAssessorAgent()
        self.fraud_detector = FraudDetectorAgent()
        self.legal_advisor = LegalAdvisorAgent()
        self.action_planner = ActionPlannerAgent()

    async def text_extraction_node(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """Extract text from the uploaded document."""
        logger.info(f"Starting text extraction for file: {state['file_id']}")
        
        try:
            state["current_step"] = "Extracting text from document"
            state["progress_percentage"] = 20.0
            state["text_extraction_status"] = ProcessingStatus.IN_PROGRESS
            
            # Save content temporarily and extract text
            temp_path = await self.file_service.storage_manager.store_temp_file(
                state["file_content"], 
                state["filename"], 
                state["file_id"]
            )
            
            # Get file type for processing
            from app.models.file_processing import FileType
            
            file_type_map = {
                "pdf": FileType.PDF,
                "docx": FileType.DOCX,
                "txt": FileType.TXT
            }
            file_type = file_type_map.get(state["file_type"], FileType.TXT)
            
            # Extract text using existing service
            extracted_text = await self.file_service.extract_text(str(temp_path), file_type)
            
            state["extracted_text"] = extracted_text
            state["text_extraction_status"] = ProcessingStatus.COMPLETED
            state["progress_percentage"] = 30.0
            
            logger.info(f"Text extraction completed for file: {state['file_id']}")
            
        except Exception as e:
            logger.error(f"Text extraction failed for file {state['file_id']}: {str(e)}")
            state["text_extraction_status"] = ProcessingStatus.FAILED
            state["error_message"] = f"Text extraction failed: {str(e)}"
            state["failed_step"] = "text_extraction"
            
        return state

    async def document_summarizer_agent(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """
        🏷️ Agent 1: Document Summarizer
        Uses the organized DocumentSummarizerAgent class.
        """
        logger.info(f"🏷️ Document Summarizer Agent starting for file: {state['file_id']}")
        
        try:
            state = await self.document_summarizer.analyze(state)
            logger.info(f"✅ Document Summarizer Agent completed for file: {state['file_id']}")
        except Exception as e:
            logger.error(f"❌ Document Summarizer Agent failed for file {state['file_id']}: {str(e)}")
            state["error_message"] = f"Document summarization failed: {str(e)}"
            state["failed_step"] = "document_summarizer"
            
        return state

    async def risk_assessment_agent(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """
        ⚠️ Agent 2: Risk Assessment Agent
        Uses the organized RiskAssessorAgent class.
        """
        logger.info(f"⚠️ Risk Assessment Agent starting for file: {state['file_id']}")
        
        try:
            state = await self.risk_assessor.analyze(state)
            logger.info(f"✅ Risk Assessment Agent completed for file: {state['file_id']}")
        except Exception as e:
            logger.error(f"❌ Risk Assessment Agent failed for file {state['file_id']}: {str(e)}")
            state["error_message"] = f"Risk assessment failed: {str(e)}"
            state["failed_step"] = "risk_assessment"
            
        return state

    async def fraud_detection_agent(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """
        🛡️ Agent 3: Fraud Detection Agent
        Uses the organized FraudDetectorAgent class.
        """
        logger.info(f"🛡️ Fraud Detection Agent starting for file: {state['file_id']}")
        
        try:
            state = await self.fraud_detector.analyze(state)
            logger.info(f"✅ Fraud Detection Agent completed for file: {state['file_id']}")
        except Exception as e:
            logger.error(f"❌ Fraud Detection Agent failed for file {state['file_id']}: {str(e)}")
            state["error_message"] = f"Fraud detection failed: {str(e)}"
            state["failed_step"] = "fraud_detection"
            
        return state

    async def legal_advisor_agent(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """
        ⚖️ Agent 4: Legal Advisor Agent
        Uses the organized LegalAdvisorAgent class.
        """
        logger.info(f"⚖️ Legal Advisor Agent starting for file: {state['file_id']}")
        
        try:
            state = await self.legal_advisor.analyze(state)
            logger.info(f"✅ Legal Advisor Agent completed for file: {state['file_id']}")
        except Exception as e:
            logger.error(f"❌ Legal Advisor Agent failed for file {state['file_id']}: {str(e)}")
            state["error_message"] = f"Legal analysis failed: {str(e)}"
            state["failed_step"] = "legal_analysis"
            
        return state

    async def action_planner_agent(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """
        📝 Agent 5: Action Planner Agent
        Uses the organized ActionPlannerAgent class and creates final summary.
        """
        logger.info(f"📝 Action Planner Agent starting for file: {state['file_id']}")
        
        try:
            # Run action planner analysis
            state = await self.action_planner.analyze(state)
            
            # Create final summary combining all results
            self._create_final_summary(state)
            
            # Mark workflow as completed
            state["current_step"] = "Analysis completed"
            state["progress_percentage"] = 100.0
            
            from datetime import datetime, timezone
            state["completed_at"] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"✅ Action Planner Agent completed for file: {state['file_id']}")
            
        except Exception as e:
            logger.error(f"❌ Action Planner Agent failed for file {state['file_id']}: {str(e)}")
            state["error_message"] = f"Action planning failed: {str(e)}"
            state["failed_step"] = "action_planning"
            
            # Create fallback summary even if action planner fails
            self._create_fallback_summary(state)
            
        return state

    def _create_final_summary(self, state: DocumentAnalysisState) -> None:
        """Create comprehensive final summary from all agent results."""
        try:
            # Get data from state
            doc_type = state.get("document_type", "Unknown document")
            risk_level = state.get("risk_level", "medium")
            risk_score = state.get("overall_risk_score", 5.0)
            fraud_score = state.get("fraud_risk_score", 2.0)
            
            # Get immediate actions count
            immediate_actions = state.get("immediate_actions", [])
            action_count = len(immediate_actions)
            
            # Create executive summary
            executive_summary = f"Analysis of {doc_type} completed. "
            executive_summary += f"Risk level: {risk_level} ({risk_score}/10). "
            
            if fraud_score > 5.0:
                executive_summary += f"Fraud concerns detected (score: {fraud_score}/10). "
            
            executive_summary += f"{action_count} immediate actions identified."
            
            # Create key findings
            key_findings = [
                f"Document Type: {doc_type}",
                f"Risk Level: {risk_level} ({risk_score}/10)",
                f"Fraud Risk Score: {fraud_score}/10",
                f"Immediate Actions: {action_count} items"
            ]
            
            # Add specific findings if available
            if state.get("suspicious_clauses"):
                key_findings.append(f"Suspicious clauses: {len(state['suspicious_clauses'])} found")
            
            if state.get("legal_implications"):
                key_findings.append(f"Legal implications: {len(state['legal_implications'])} identified")
            
            state["summary"] = {
                "executive_summary": executive_summary,
                "key_findings": key_findings
            }
            
        except Exception as e:
            logger.warning(f"Failed to create final summary: {e}")
            self._create_fallback_summary(state)

    def _create_fallback_summary(self, state: DocumentAnalysisState) -> None:
        """Create a basic fallback summary."""
        doc_type = state.get("document_type", "legal document")
        risk_level = state.get("risk_level", "medium")
        
        state["summary"] = {
            "executive_summary": f"Analysis completed for {doc_type}. Risk level: {risk_level}. Professional review recommended for important decisions.",
            "key_findings": [
                f"Document identified as: {doc_type}",
                f"Overall risk level: {risk_level}",
                "Professional legal review recommended",
                "Read document carefully before signing"
            ]
        }
