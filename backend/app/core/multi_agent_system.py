"""
Multi-Agent System for Specialized Legal Document Analysis.
Uses organized agent architecture with individual agent files and prompts.
"""

import logging
from typing import Any

from app.agents.action_planner import ActionPlannerAgent
from app.agents.document_summarizer import DocumentSummarizerAgent
from app.agents.fraud_detector import FraudDetectorAgent
from app.agents.legal_advisor import LegalAdvisorAgent
from app.agents.risk_assessor import RiskAssessorAgent
from app.core.graph_state import DocumentAnalysisState, ProcessingStatus
from app.core.langfuse_integration import trace_agent
from app.services.file_processing import FileProcessingService, FileType

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

    async def extract_text_content(self, state: dict[str, Any]) -> None:
        """Extract text content from the file for analysis."""
        try:
            logger.info("MultiAgentSystem: Starting text extraction")

            # Check if text is already extracted
            if state.get("extracted_text"):
                logger.info(
                    f"MultiAgentSystem: Text already extracted. Length: {len(state['extracted_text'])}"
                )
                state["text_extraction_status"] = ProcessingStatus.COMPLETED
                return

            # Create temporary file from bytes
            import os
            import tempfile

            with tempfile.NamedTemporaryFile(
                delete=False, suffix=f".{state['file_type']}"
            ) as temp_file:
                temp_file.write(state["file_content"])
                temp_path = temp_file.name

            try:
                # Determine file type for extraction
                file_extension = state["file_type"].lower()
                if file_extension == "pdf":
                    file_type = FileType.PDF
                elif file_extension in ["docx", "doc"]:
                    file_type = FileType.DOCX
                else:
                    file_type = FileType.TXT

                logger.info(f"MultiAgentSystem: Extracting text from {file_type} file")

                # Extract text using file service
                extracted_text = await self.file_service.extract_text(str(temp_path), file_type)

                # Store in state
                state["extracted_text"] = extracted_text
                state["text_extraction_status"] = ProcessingStatus.COMPLETED

                logger.info(
                    f"MultiAgentSystem: Text extraction completed. Length: {len(extracted_text) if extracted_text else 0}"
                )

            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except Exception as e:
            logger.error(f"MultiAgentSystem: Error extracting text: {str(e)}")
            state["text_extraction_status"] = ProcessingStatus.FAILED
            raise

    # Workflow compatibility methods
    @trace_agent("text_extraction")
    async def text_extraction_node(self, state: dict[str, Any]) -> dict[str, Any]:
        """Text extraction node for workflow compatibility."""
        await self.extract_text_content(state)
        return state

    @trace_agent("document_summarizer")
    async def document_summarizer_agent(self, state: dict[str, Any]) -> dict[str, Any]:
        """Document summarizer agent node."""
        try:
            logger.info("Starting document summarizer agent")
            state["current_step"] = "Analyzing document content"
            state["progress_percentage"] = 40.0

            if not state.get("extracted_text"):
                logger.error("No extracted text available for document summarizer")
                return state

            # Run document summarizer
            await self.document_summarizer.analyze(state)
            state["progress_percentage"] = 50.0

            logger.info("Document summarizer agent completed")

        except Exception as e:
            logger.error(f"Document summarizer agent failed: {str(e)}")
            state["error_message"] = f"Document summarizer failed: {str(e)}"

        return state

    @trace_agent("risk_assessment")
    async def risk_assessment_agent(self, state: dict[str, Any]) -> dict[str, Any]:
        """Risk assessment agent node."""
        try:
            logger.info("Starting risk assessment agent")
            state["current_step"] = "Assessing legal risks"
            state["progress_percentage"] = 60.0

            if not state.get("extracted_text"):
                logger.error("No extracted text available for risk assessment")
                return state

            # Run risk assessor
            await self.risk_assessor.analyze(state)
            state["progress_percentage"] = 70.0

            logger.info("Risk assessment agent completed")

        except Exception as e:
            logger.error(f"Risk assessment agent failed: {str(e)}")
            state["error_message"] = f"Risk assessment failed: {str(e)}"

        return state

    @trace_agent("fraud_detection")
    async def fraud_detection_agent(self, state: dict[str, Any]) -> dict[str, Any]:
        """Fraud detection agent node."""
        try:
            logger.info("Starting fraud detection agent")
            state["current_step"] = "Detecting potential fraud"
            state["progress_percentage"] = 80.0

            if not state.get("extracted_text"):
                logger.error("No extracted text available for fraud detection")
                return state

            # Run fraud detector
            await self.fraud_detector.analyze(state)
            state["progress_percentage"] = 85.0

            logger.info("Fraud detection agent completed")

        except Exception as e:
            logger.error(f"Fraud detection agent failed: {str(e)}")
            state["error_message"] = f"Fraud detection failed: {str(e)}"

        return state

    @trace_agent("legal_advisor")
    async def legal_advisor_agent(self, state: dict[str, Any]) -> dict[str, Any]:
        """Legal advisor agent node."""
        try:
            logger.info("Starting legal advisor agent")
            state["current_step"] = "Providing legal analysis"
            state["progress_percentage"] = 90.0

            if not state.get("extracted_text"):
                logger.error("No extracted text available for legal advisor")
                return state

            # Run legal advisor
            await self.legal_advisor.analyze(state)
            state["progress_percentage"] = 95.0

            logger.info("Legal advisor agent completed")

        except Exception as e:
            logger.error(f"Legal advisor agent failed: {str(e)}")
            state["error_message"] = f"Legal advisor failed: {str(e)}"

        return state

    @trace_agent("action_planner")
    async def action_planner_agent(self, state: dict[str, Any]) -> dict[str, Any]:
        """Action planner agent node."""
        try:
            logger.info("Starting action planner agent")
            state["current_step"] = "Creating action plan"
            state["progress_percentage"] = 95.0

            if not state.get("extracted_text"):
                logger.error("No extracted text available for action planner")
                return state

            # Run action planner
            await self.action_planner.analyze(state)
            state["current_step"] = "Analysis completed"
            state["progress_percentage"] = 100.0

            logger.info("Action planner agent completed")

        except Exception as e:
            logger.error(f"Action planner agent failed: {str(e)}")
            state["error_message"] = f"Action planner failed: {str(e)}"

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
                f"Immediate Actions: {action_count} items",
            ]

            # Add specific findings if available
            if state.get("suspicious_clauses"):
                key_findings.append(f"Suspicious clauses: {len(state['suspicious_clauses'])} found")

            if state.get("legal_implications"):
                key_findings.append(
                    f"Legal implications: {len(state['legal_implications'])} identified"
                )

            state["summary"] = {
                "executive_summary": executive_summary,
                "key_findings": key_findings,
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
                "Read document carefully before signing",
            ],
        }
