"""
Multi-Agent LangGraph workflow for comprehensive legal document analysis.
"""

import time
import logging
from typing import Dict, Any
from datetime import datetime, timezone

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.graph_state import DocumentAnalysisState, ProcessingStatus
from app.core.multi_agent_system import LegalAnalysisAgents
from app.services.file_processing import FileProcessingService

logger = logging.getLogger(__name__)


class DocumentAnalysisWorkflow:
    """
    Multi-Agent LangGraph workflow for comprehensive legal document analysis.
    
    Flow: 
    Text Extraction → 
    Document Summarizer Agent → 
    Risk Assessment Agent → 
    Fraud Detection Agent → 
    Legal Advisor Agent → 
    Action Planner Agent
    """
    
    def __init__(self, file_service: FileProcessingService):
        self.file_service = file_service
        self.agents = LegalAnalysisAgents(file_service)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the multi-agent LangGraph workflow."""
        
        # Create the state graph
        workflow = StateGraph(DocumentAnalysisState)
        
        # Add agent nodes
        workflow.add_node("text_extraction", self.agents.text_extraction_node)
        workflow.add_node("document_summarizer", self.agents.document_summarizer_agent)
        workflow.add_node("risk_assessor", self.agents.risk_assessment_agent)
        workflow.add_node("fraud_detector", self.agents.fraud_detection_agent)
        workflow.add_node("legal_advisor", self.agents.legal_advisor_agent)
        workflow.add_node("action_planner", self.agents.action_planner_agent)
        
        # Define the multi-agent flow
        workflow.set_entry_point("text_extraction")
        
        # Sequential agent execution
        workflow.add_edge("text_extraction", "document_summarizer")
        workflow.add_edge("document_summarizer", "risk_assessor")
        workflow.add_edge("risk_assessor", "fraud_detector")
        workflow.add_edge("fraud_detector", "legal_advisor")
        workflow.add_edge("legal_advisor", "action_planner")
        workflow.add_edge("action_planner", END)
        
        # Compile with memory
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    
    async def process_document(
        self, 
        file_id: str, 
        file_content: bytes, 
        filename: str, 
        file_type: str
    ) -> DocumentAnalysisState:
        """
        Process a document through the complete analysis workflow.
        
        Args:
            file_id: Unique identifier for the file
            file_content: Raw file content bytes
            filename: Original filename
            file_type: File type (pdf, docx, txt)
            
        Returns:
            Complete analysis state with results
        """
        start_time = time.time()
        
        # Initialize state
        initial_state: DocumentAnalysisState = {
            "file_id": file_id,
            "file_content": file_content,
            "filename": filename,
            "file_type": file_type,
            "current_step": "Starting analysis",
            "progress_percentage": 0.0,
            
            # Text extraction
            "extracted_text": None,
            "text_extraction_status": ProcessingStatus.PENDING,
            
            # Multi-Agent Analysis Results
            "document_summary": None,
            "document_purpose": None,
            "key_parties": None,
            "important_dates": None,
            
            "legal_risks": None,
            "potential_liabilities": None,
            "overall_risk_score": 0.0,
            "overall_risk_level": None,
            
            "suspicious_clauses": None,
            "hidden_fees": None,
            "fraud_indicators": None,
            "fraud_risk_score": 0.0,
            
            "legal_implications": None,
            "your_rights": None,
            "their_obligations": None,
            "potential_consequences": None,
            
            "immediate_actions": None,
            "before_signing": None,
            "long_term_considerations": None,
            "recommended_timeline": None,
            
            # Legacy fields
            "document_type": None,
            "confidence_score": 0.0,
            "legal_analysis": None,
            "analysis_status": ProcessingStatus.PENDING,
            "risks": [],
            "risk_assessment_status": ProcessingStatus.PENDING,
            "executive_summary": None,
            "key_findings": [],
            
            # Error handling
            "error_message": None,
            "failed_step": None,
            
            # Metadata
            "processing_time": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
        }
        
        logger.info(f"Starting document analysis workflow for file: {file_id}")
        
        try:
            # Run the workflow
            config = {"configurable": {"thread_id": file_id}}
            
            # Process through the graph
            final_state = await self.graph.ainvoke(initial_state, config=config)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            final_state["processing_time"] = processing_time
            
            logger.info(f"Document analysis completed for file: {file_id} in {processing_time:.2f}s")
            
            return final_state
            
        except Exception as e:
            logger.error(f"Document analysis workflow failed for file {file_id}: {str(e)}")
            
            # Return error state
            error_state = initial_state.copy()
            error_state.update({
                "error_message": f"Workflow failed: {str(e)}",
                "failed_step": "workflow",
                "processing_time": time.time() - start_time,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            })
            
            return error_state
    
    async def get_processing_status(self, file_id: str) -> Dict[str, Any]:
        """
        Get current processing status for a file.
        
        Args:
            file_id: File identifier
            
        Returns:
            Current processing status
        """
        try:
            config = {"configurable": {"thread_id": file_id}}
            
            # Get the current state from checkpointer
            state = await self.graph.aget_state(config)
            
            if state and state.values:
                return {
                    "file_id": file_id,
                    "current_step": state.values.get("current_step", "Unknown"),
                    "progress_percentage": state.values.get("progress_percentage", 0.0),
                    "status": "processing" if state.values.get("progress_percentage", 0) < 100 else "completed",
                    "error_message": state.values.get("error_message"),
                }
            else:
                return {
                    "file_id": file_id,
                    "current_step": "Not found",
                    "progress_percentage": 0.0,
                    "status": "not_found",
                    "error_message": "File not found in processing queue",
                }
                
        except Exception as e:
            logger.error(f"Failed to get processing status for file {file_id}: {str(e)}")
            return {
                "file_id": file_id,
                "current_step": "Error",
                "progress_percentage": 0.0,
                "status": "error",
                "error_message": f"Failed to get status: {str(e)}",
            }
