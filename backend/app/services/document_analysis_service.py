"""
Document analysis service that integrates LangGraph workflow with FastAPI.
"""

import logging
from datetime import UTC, datetime
from typing import Any

from app.core.document_workflow import DocumentAnalysisWorkflow
from app.core.graph_state import DocumentAnalysisState, ProcessingStatus
from app.services.file_processing import FileProcessingService

logger = logging.getLogger(__name__)


class DocumentAnalysisService:
    """
    Service for managing document analysis using LangGraph workflow.
    """

    def __init__(self, file_service: FileProcessingService):
        self.file_service = file_service
        self.workflow = DocumentAnalysisWorkflow(file_service)
        # In-memory storage for analysis results (replace with database in production)
        self._analysis_cache: dict[str, DocumentAnalysisState] = {}

    async def analyze_document(
        self, file_id: str, file_content: bytes, filename: str
    ) -> dict[str, Any]:
        """
        Start document analysis and return initial response.

        Args:
            file_id: Unique file identifier
            file_content: Raw file content
            filename: Original filename

        Returns:
            Analysis initiation response
        """
        try:
            # Determine file type
            file_type = self._get_file_type(filename)

            logger.info(f"Starting analysis for file: {file_id} ({filename})")

            # Run the analysis workflow
            result = await self.workflow.process_document(
                file_id=file_id, file_content=file_content, filename=filename, file_type=file_type
            )

            # Cache the result
            self._analysis_cache[file_id] = result

            # Clean up the uploaded file after successful analysis (if enabled)
            if self.file_service.settings.auto_cleanup_after_analysis:
                logger.info(
                    f"Auto-cleanup enabled, removing file {file_id} after successful analysis"
                )
                await self._cleanup_file_after_analysis(file_id)
            else:
                logger.info(f"Auto-cleanup disabled, keeping file {file_id} for manual cleanup")

            # Return formatted response
            return self._format_analysis_response(result)

        except Exception as e:
            logger.error(f"Document analysis failed for {file_id}: {str(e)}")

            # Clean up file on error to prevent storage bloat (if enabled)
            if self.file_service.settings.auto_cleanup_after_analysis:
                try:
                    await self._cleanup_file_after_analysis(file_id)
                except Exception as cleanup_error:
                    logger.error(
                        f"Failed to cleanup file {file_id} after analysis error: {cleanup_error}"
                    )

            return {
                "file_id": file_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat(),
            }

    async def get_analysis_result(self, file_id: str) -> dict[str, Any] | None:
        """
        Get analysis result for a file.

        Args:
            file_id: File identifier

        Returns:
            Analysis result or None if not found
        """
        if file_id in self._analysis_cache:
            result = self._analysis_cache[file_id]
            return self._format_analysis_response(result)

        # Try to get from workflow checkpointer
        status = await self.workflow.get_processing_status(file_id)
        if status.get("status") != "not_found":
            return status

        return None

    async def get_processing_status(self, file_id: str) -> dict[str, Any]:
        """
        Get current processing status.

        Args:
            file_id: File identifier

        Returns:
            Processing status
        """
        return await self.workflow.get_processing_status(file_id)

    def _get_file_type(self, filename: str) -> str:
        """Determine file type from filename."""
        if filename.lower().endswith(".pdf"):
            return "pdf"
        elif filename.lower().endswith((".doc", ".docx")):
            return "docx"
        elif filename.lower().endswith(".txt"):
            return "txt"
        else:
            return "unknown"

    def _format_analysis_response(self, state: DocumentAnalysisState) -> dict[str, Any]:
        """
        Format analysis state into API response.

        Args:
            state: Document analysis state

        Returns:
            Formatted response
        """
        # Basic response structure
        response = {
            "file_id": state["file_id"],
            "filename": state["filename"],
            "status": "completed" if state.get("progress_percentage", 0) >= 100 else "processing",
            "progress_percentage": state.get("progress_percentage", 0),
            "current_step": state.get("current_step"),
            "created_at": state.get("created_at"),
            "completed_at": state.get("completed_at"),
            "processing_time": state.get("processing_time"),
        }

        # Add error information if present
        if state.get("error_message"):
            response.update(
                {
                    "status": "error",
                    "error": state["error_message"],
                    "failed_step": state.get("failed_step"),
                }
            )
            return response

        # Add extracted text if available
        if state.get("extracted_text"):
            response["extracted_text"] = state["extracted_text"]
            response["text_extraction_status"] = state.get(
                "text_extraction_status", ProcessingStatus.PENDING
            ).value

        # === NEW ORGANIZED AGENT RESULTS ===

        # Document Summarizer Agent Results
        if state.get("document_summary"):
            response["document_summary"] = state["document_summary"]
        if state.get("document_purpose"):
            response["document_purpose"] = state["document_purpose"]
        if state.get("key_parties"):
            response["key_parties"] = state["key_parties"]
        if state.get("important_dates"):
            response["important_dates"] = state["important_dates"]

        # Risk Assessment Agent Results
        if state.get("legal_risks"):
            response["legal_risks"] = state["legal_risks"]
        if state.get("potential_liabilities"):
            response["potential_liabilities"] = state["potential_liabilities"]
        if state.get("overall_risk_score") is not None:
            response["overall_risk_score"] = state["overall_risk_score"]
        if state.get("overall_risk_level"):
            response["overall_risk_level"] = state["overall_risk_level"]

        # Fraud Detection Agent Results
        if state.get("suspicious_clauses"):
            response["suspicious_clauses"] = state["suspicious_clauses"]
        if state.get("hidden_fees"):
            response["hidden_fees"] = state["hidden_fees"]
        if state.get("fraud_indicators"):
            response["fraud_indicators"] = state["fraud_indicators"]
        if state.get("fraud_risk_score") is not None:
            response["fraud_risk_score"] = state["fraud_risk_score"]

        # Legal Advisor Agent Results
        if state.get("legal_implications"):
            response["legal_implications"] = state["legal_implications"]
        if state.get("rights_obligations"):
            response["rights_obligations"] = state["rights_obligations"]
            # Also map to legacy fields for backward compatibility
            if state["rights_obligations"].get("your_rights"):
                response["your_rights"] = state["rights_obligations"]["your_rights"]
            if state["rights_obligations"].get("other_party_obligations"):
                response["their_obligations"] = state["rights_obligations"][
                    "other_party_obligations"
                ]
        if state.get("compliance_issues"):
            response["compliance_issues"] = state["compliance_issues"]
        if state.get("legal_advice"):
            response["legal_advice"] = state["legal_advice"]

        # Action Planner Agent Results
        if state.get("immediate_actions"):
            response["immediate_actions"] = state["immediate_actions"]
        if state.get("long_term_actions"):
            response["long_term_actions"] = state["long_term_actions"]
            # Also map to legacy field for backward compatibility
            response["long_term_considerations"] = state["long_term_actions"]
        if state.get("deadlines"):
            response["deadlines"] = state["deadlines"]
        if state.get("recommendations"):
            response["recommendations"] = state["recommendations"]

        # === LEGACY COMPATIBILITY ===

        # Add document classification if available (legacy format)
        if state.get("document_type"):
            response["document_classification"] = {
                "document_type": (
                    state["document_type"].value
                    if hasattr(state["document_type"], "value")
                    else str(state["document_type"])
                ),
                "confidence_score": state.get("confidence_score", 0.0),
            }

        # Add legacy legal analysis if available
        if state.get("legal_analysis"):
            response["legal_analysis"] = state["legal_analysis"]
            response["analysis_status"] = state.get(
                "analysis_status", ProcessingStatus.PENDING
            ).value

        # Add legacy risk assessment if available
        if state.get("risks"):
            response["risk_assessment"] = {
                "overall_risk_score": state.get("overall_risk_score", 0.0),
                "overall_risk_level": (
                    state.get("overall_risk_level").value
                    if state.get("overall_risk_level")
                    and hasattr(state["overall_risk_level"], "value")
                    else state.get("overall_risk_level")
                ),
                "risks": [
                    {
                        "category": (
                            risk["category"].value
                            if hasattr(risk["category"], "value")
                            else str(risk["category"])
                        ),
                        "level": (
                            risk["level"].value
                            if hasattr(risk["level"], "value")
                            else str(risk["level"])
                        ),
                        "title": risk["title"],
                        "description": risk["description"],
                        "recommendation": risk["recommendation"],
                        "confidence": risk["confidence"],
                    }
                    for risk in state["risks"]
                ],
                "status": state.get("risk_assessment_status", ProcessingStatus.PENDING).value,
            }

        # Add summary if available
        if state.get("summary"):
            response["summary"] = state["summary"]
        elif state.get("executive_summary"):
            response["summary"] = {
                "executive_summary": state["executive_summary"],
                "key_findings": state.get("key_findings", []),
            }

        return response

    async def _cleanup_file_after_analysis(self, file_id: str) -> None:
        """
        Clean up uploaded file after analysis is complete.

        This prevents storage bloat by automatically removing files
        once they've been processed and results cached.

        Args:
            file_id: File identifier to clean up
        """
        try:
            # Remove file from storage manager
            success = await self.file_service.storage_manager.remove_file(file_id)

            if success:
                logger.info(f"Successfully cleaned up file {file_id} after analysis completion")
            else:
                logger.warning(
                    f"File {file_id} not found for cleanup (may have been already removed)"
                )

        except Exception as e:
            # Log error but don't fail the analysis - cleanup is not critical
            logger.error(f"Failed to cleanup file {file_id} after analysis: {str(e)}")
            logger.error("Analysis results are still available, only file cleanup failed")
