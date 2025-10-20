"""Analysis repository for document analysis results."""

from typing import Optional, List, Dict, Any
from datetime import datetime

from .base_repository import InMemoryRepository
from app.core.graph_state import DocumentAnalysisState, ProcessingStatus


class AnalysisRepository(InMemoryRepository[DocumentAnalysisState]):
    """
    Repository for managing document analysis results.
    
    Stores and retrieves analysis states and results.
    """
    
    async def create(self, entity: DocumentAnalysisState) -> DocumentAnalysisState:
        """Create analysis result with file_id as key."""
        file_id = entity.get('file_id')
        if not file_id:
            raise ValueError("Analysis state must have 'file_id'")
        
        self._storage[file_id] = entity
        return entity
    
    async def get_by_status(self, status: ProcessingStatus) -> List[DocumentAnalysisState]:
        """
        Get analyses by processing status.
        
        Args:
            status: Processing status to filter by
            
        Returns:
            List of analyses with the specified status
        """
        return [
            analysis for analysis in self._storage.values()
            if analysis.get('text_extraction_status') == status or
               analysis.get('document_summarization_status') == status or
               analysis.get('risk_assessment_status') == status
        ]
    
    async def get_completed_analyses(self) -> List[DocumentAnalysisState]:
        """
        Get all completed analyses.
        
        Returns:
            List of completed analyses
        """
        return [
            analysis for analysis in self._storage.values()
            if analysis.get('progress_percentage', 0) >= 100.0
        ]
    
    async def get_failed_analyses(self) -> List[DocumentAnalysisState]:
        """
        Get all failed analyses.
        
        Returns:
            List of failed analyses
        """
        return [
            analysis for analysis in self._storage.values()
            if analysis.get('error_message') is not None
        ]
    
    async def get_in_progress_analyses(self) -> List[DocumentAnalysisState]:
        """
        Get all analyses currently in progress.
        
        Returns:
            List of in-progress analyses
        """
        return [
            analysis for analysis in self._storage.values()
            if 0 < analysis.get('progress_percentage', 0) < 100.0 and
               analysis.get('error_message') is None
        ]
    
    async def update_progress(self, file_id: str, progress: float, current_step: str) -> Optional[DocumentAnalysisState]:
        """
        Update analysis progress.
        
        Args:
            file_id: File identifier
            progress: Progress percentage (0-100)
            current_step: Description of current processing step
            
        Returns:
            Updated analysis state if found, None otherwise
        """
        analysis = await self.get_by_id(file_id)
        if not analysis:
            return None
        
        analysis['progress_percentage'] = progress
        analysis['current_step'] = current_step
        
        return await self.update(file_id, analysis)
    
    async def mark_failed(self, file_id: str, error_message: str, failed_step: str) -> Optional[DocumentAnalysisState]:
        """
        Mark analysis as failed.
        
        Args:
            file_id: File identifier
            error_message: Error description
            failed_step: Step where failure occurred
            
        Returns:
            Updated analysis state if found, None otherwise
        """
        analysis = await self.get_by_id(file_id)
        if not analysis:
            return None
        
        analysis['error_message'] = error_message
        analysis['failed_step'] = failed_step
        analysis['progress_percentage'] = 0.0
        
        return await self.update(file_id, analysis)
    
    async def get_analysis_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics about analyses.
        
        Returns:
            Dictionary with analysis statistics
        """
        all_analyses = await self.list_all()
        
        total_count = len(all_analyses)
        completed = await self.get_completed_analyses()
        failed = await self.get_failed_analyses()
        in_progress = await self.get_in_progress_analyses()
        
        # Calculate average processing time for completed analyses
        avg_processing_time = None
        if completed:
            total_time = 0
            count_with_time = 0
            for analysis in completed:
                start_time = analysis.get('start_time')
                end_time = analysis.get('end_time')
                if start_time and end_time:
                    total_time += (end_time - start_time)
                    count_with_time += 1
            
            if count_with_time > 0:
                avg_processing_time = total_time / count_with_time
        
        return {
            "total_analyses": total_count,
            "completed": len(completed),
            "failed": len(failed),
            "in_progress": len(in_progress),
            "success_rate": len(completed) / total_count if total_count > 0 else 0,
            "average_processing_time_seconds": avg_processing_time,
            "has_failures": len(failed) > 0
        }
    
    async def cleanup_old_analyses(self, max_age_hours: int = 24) -> int:
        """
        Clean up old completed analyses.
        
        Args:
            max_age_hours: Maximum age in hours for analyses to keep
            
        Returns:
            Number of analyses cleaned up
        """
        current_time = datetime.utcnow()
        cutoff_time = current_time.timestamp() - (max_age_hours * 3600)
        
        analyses_to_remove = []
        for file_id, analysis in self._storage.items():
            # Only clean up completed analyses
            if analysis.get('progress_percentage', 0) >= 100.0:
                end_time = analysis.get('end_time')
                if end_time and end_time < cutoff_time:
                    analyses_to_remove.append(file_id)
        
        for file_id in analyses_to_remove:
            await self.delete(file_id)
        
        return len(analyses_to_remove)
