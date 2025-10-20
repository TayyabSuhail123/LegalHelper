"""Analysis service for document analysis business logic."""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.file_repository import FileRepository
from app.core.document_analysis_service import DocumentAnalysisService as CoreAnalysisService
from app.core.graph_state import DocumentAnalysisState, ProcessingStatus

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Service layer for document analysis business operations.
    
    This service encapsulates business logic for analysis operations,
    using repositories for data access.
    """
    
    def __init__(self, file_service):
        self.file_service = file_service
        self.analysis_repository = AnalysisRepository()
        self.file_repository = FileRepository()
        self.core_analysis_service = CoreAnalysisService(file_service.file_processing_service)
    
    async def start_analysis(self, file_id: str) -> Dict[str, Any]:
        """
        Start document analysis for a file.
        
        Args:
            file_id: File identifier
            
        Returns:
            Analysis initiation response
            
        Raises:
            ValueError: If file not found or invalid
        """
        try:
            logger.info(f"AnalysisService: Starting analysis for file {file_id}")
            
            # Check if file exists in repository
            file = await self.file_repository.get_by_id(file_id)
            if not file:
                raise ValueError(f"File with ID {file_id} not found")
            
            # Get file content for analysis
            file_content = await self.file_service.file_processing_service.storage_manager.get_file_content(file_id)
            if not file_content:
                raise ValueError("File content not found")
            
            # Start analysis using core service
            result = await self.core_analysis_service.analyze_document(
                file_id=file_id,
                file_content=file_content,
                filename=file.filename
            )
            
            # Store initial analysis state in repository
            if 'file_id' in result:
                analysis_state = {
                    'file_id': file_id,
                    'start_time': datetime.utcnow().timestamp(),
                    'progress_percentage': 0.0,
                    'current_step': 'Analysis started',
                    'status': 'processing'
                }
                await self.analysis_repository.create(analysis_state)
            
            logger.info(f"AnalysisService: Analysis started for file {file_id}")
            return result
            
        except Exception as e:
            logger.error(f"AnalysisService: Start analysis failed for {file_id}: {str(e)}")
            raise
    
    async def get_result(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get analysis result for a file.
        
        Args:
            file_id: File identifier
            
        Returns:
            Analysis result if available, None otherwise
        """
        try:
            # First check our repository
            analysis_state = await self.analysis_repository.get_by_id(file_id)
            
            # If not found, check core service
            if not analysis_state:
                result = await self.core_analysis_service.get_analysis_result(file_id)
                return result
            
            # If we have state, get latest result from core service
            result = await self.core_analysis_service.get_analysis_result(file_id)
            
            # Update our repository with latest state if needed
            if result and analysis_state:
                analysis_state['end_time'] = datetime.utcnow().timestamp()
                analysis_state['progress_percentage'] = 100.0
                analysis_state['current_step'] = 'Analysis completed'
                await self.analysis_repository.update(file_id, analysis_state)
            
            return result
            
        except Exception as e:
            logger.error(f"AnalysisService: Get result failed for {file_id}: {str(e)}")
            return None
    
    async def get_processing_status(self, file_id: str) -> Dict[str, Any]:
        """
        Get detailed processing status for an analysis.
        
        Args:
            file_id: File identifier
            
        Returns:
            Processing status information
        """
        try:
            # Check our repository first
            analysis_state = await self.analysis_repository.get_by_id(file_id)
            
            # Get status from core service
            core_status = await self.core_analysis_service.get_processing_status(file_id)
            
            # Combine information
            if analysis_state and core_status:
                return {
                    **core_status,
                    'start_time': analysis_state.get('start_time'),
                    'repository_tracked': True
                }
            elif core_status:
                return {
                    **core_status,
                    'repository_tracked': False
                }
            else:
                return {
                    'file_id': file_id,
                    'status': 'not_found',
                    'error_message': 'Analysis not found',
                    'repository_tracked': False
                }
                
        except Exception as e:
            logger.error(f"AnalysisService: Get processing status failed for {file_id}: {str(e)}")
            return {
                'file_id': file_id,
                'status': 'error',
                'error_message': str(e),
                'repository_tracked': False
            }
    
    async def list_analyses(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        List all analyses with pagination.
        
        Args:
            limit: Maximum number of analyses to return
            offset: Number of analyses to skip
            
        Returns:
            Paginated analysis list
        """
        try:
            analyses = await self.analysis_repository.list_all(limit=limit, offset=offset)
            total_count = await self.analysis_repository.count()
            
            return {
                "analyses": analyses,
                "pagination": {
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_next": offset + limit < total_count,
                    "has_previous": offset > 0
                }
            }
            
        except Exception as e:
            logger.error(f"AnalysisService: List analyses failed: {str(e)}")
            raise
    
    async def get_completed_analyses(self) -> List[DocumentAnalysisState]:
        """
        Get all completed analyses.
        
        Returns:
            List of completed analyses
        """
        return await self.analysis_repository.get_completed_analyses()
    
    async def get_failed_analyses(self) -> List[DocumentAnalysisState]:
        """
        Get all failed analyses.
        
        Returns:
            List of failed analyses
        """
        return await self.analysis_repository.get_failed_analyses()
    
    async def get_analysis_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics about analyses.
        
        Returns:
            Analysis statistics
        """
        try:
            repository_stats = await self.analysis_repository.get_analysis_summary()
            
            # Add additional business logic here if needed
            return {
                **repository_stats,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AnalysisService: Get analysis summary failed: {str(e)}")
            raise
    
    async def cleanup_old_analyses(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """
        Clean up old analyses.
        
        Args:
            max_age_hours: Maximum age in hours for analyses to keep
            
        Returns:
            Cleanup operation result
        """
        try:
            logger.info(f"AnalysisService: Starting cleanup of analyses older than {max_age_hours} hours")
            
            cleaned_count = await self.analysis_repository.cleanup_old_analyses(max_age_hours)
            
            logger.info(f"AnalysisService: Cleaned up {cleaned_count} old analyses")
            
            return {
                "success": True,
                "cleaned_analyses": cleaned_count,
                "max_age_hours": max_age_hours,
                "cleanup_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AnalysisService: Cleanup failed: {str(e)}")
            raise
    
    async def mark_analysis_failed(self, file_id: str, error_message: str, failed_step: str) -> Optional[DocumentAnalysisState]:
        """
        Mark an analysis as failed.
        
        Args:
            file_id: File identifier
            error_message: Error description
            failed_step: Step where failure occurred
            
        Returns:
            Updated analysis state if found, None otherwise
        """
        return await self.analysis_repository.mark_failed(file_id, error_message, failed_step)
    
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
        return await self.analysis_repository.update_progress(file_id, progress, current_step)
