"""File storage and cleanup management."""

import os
import shutil
import asyncio
import tempfile
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FileStorageManager:
    """
    Manages temporary file storage with automatic cleanup.
    
    Files are stored temporarily during processing and cleaned up automatically.
    This is suitable for document processing where we don't need long-term storage.
    """
    
    def __init__(self, base_dir: str = "./uploads", cleanup_interval: int = 3600):
        """
        Initialize file storage manager.
        
        Args:
            base_dir: Base directory for file storage
            cleanup_interval: How often to run cleanup (seconds)
        """
        self.base_dir = Path(base_dir)
        self.cleanup_interval = cleanup_interval
        self._file_registry: Dict[str, Dict] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Create directory if it doesn't exist
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Note: Cleanup task will be started when first async method is called
    
    def _start_cleanup_task(self):
        """Start the background cleanup task if there's an event loop."""
        try:
            if self._cleanup_task is None or self._cleanup_task.done():
                self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        except RuntimeError:
            # No event loop running, cleanup task will start when first async method is called
            pass
    
    async def _cleanup_loop(self):
        """Background task to clean up old files."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self.cleanup_old_files()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def store_temp_file(self, file_content: bytes, filename: str, file_id: str) -> Path:
        """
        Store file temporarily for processing.
        
        Args:
            file_content: File content bytes
            filename: Original filename
            file_id: Unique file identifier
            
        Returns:
            Path to stored file
        """
        # Start cleanup task if not already running
        self._start_cleanup_task()
        
        # Create subdirectory for this file
        file_dir = self.base_dir / file_id
        file_dir.mkdir(exist_ok=True)
        
        # Store file
        file_path = file_dir / filename
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Register file for cleanup
        self._file_registry[file_id] = {
            'path': file_path,
            'directory': file_dir,
            'created_at': datetime.utcnow(),
            'filename': filename
        }
        
        logger.info(f"Stored temporary file: {file_path}")
        return file_path
    
    async def get_file_path(self, file_id: str) -> Optional[Path]:
        """Get file path by file ID."""
        if file_id in self._file_registry:
            return self._file_registry[file_id]['path']
        return None
    
    async def get_file_content(self, file_id: str) -> Optional[bytes]:
        """
        Get file content by file ID.
        
        Args:
            file_id: File identifier
            
        Returns:
            File content as bytes, or None if file not found
        """
        file_path = await self.get_file_path(file_id)
        if file_path and file_path.exists():
            try:
                with open(file_path, 'rb') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Failed to read file {file_id}: {e}")
                return None
        return None
    
    async def remove_file(self, file_id: str) -> bool:
        """
        Remove a specific file and its directory.
        
        Args:
            file_id: File identifier
            
        Returns:
            True if file was removed, False if not found
        """
        if file_id not in self._file_registry:
            return False
        
        try:
            file_info = self._file_registry[file_id]
            
            # Remove directory (which contains the file)
            if file_info['directory'].exists():
                shutil.rmtree(file_info['directory'])
            
            # Remove from registry
            del self._file_registry[file_id]
            
            logger.info(f"Removed file: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing file {file_id}: {e}")
            return False
    
    async def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up files older than specified age.
        
        Args:
            max_age_hours: Maximum age of files in hours
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        files_to_remove = []
        
        for file_id, file_info in self._file_registry.items():
            if file_info['created_at'] < cutoff_time:
                files_to_remove.append(file_id)
        
        for file_id in files_to_remove:
            await self.remove_file(file_id)
        
        if files_to_remove:
            logger.info(f"Cleaned up {len(files_to_remove)} old files")
    
    async def get_storage_stats(self) -> Dict:
        """Get storage statistics."""
        total_files = len(self._file_registry)
        total_size = 0
        
        for file_info in self._file_registry.values():
            try:
                if file_info['path'].exists():
                    total_size += file_info['path'].stat().st_size
            except Exception:
                continue
        
        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'base_directory': str(self.base_dir)
        }
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
