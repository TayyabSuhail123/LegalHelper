"""Base repository interface and common implementations."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any
from uuid import UUID

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Base repository interface for data access operations.
    
    This abstract class defines the common interface that all repositories
    should implement, following the Repository pattern.
    """
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """
        Create a new entity.
        
        Args:
            entity: Entity to create
            
        Returns:
            Created entity with any generated fields (e.g., ID)
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            entity_id: Unique identifier
            
        Returns:
            Entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def update(self, entity_id: str, entity: T) -> Optional[T]:
        """
        Update an existing entity.
        
        Args:
            entity_id: Unique identifier
            entity: Updated entity data
            
        Returns:
            Updated entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """
        Delete an entity.
        
        Args:
            entity_id: Unique identifier
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """
        List all entities with pagination.
        
        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip
            
        Returns:
            List of entities
        """
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """
        Count total number of entities.
        
        Returns:
            Total count
        """
        pass


class InMemoryRepository(BaseRepository[T]):
    """
    In-memory implementation of repository pattern.
    
    This provides a concrete implementation using dictionaries for storage,
    suitable for development and testing.
    """
    
    def __init__(self):
        self._storage: Dict[str, T] = {}
    
    async def create(self, entity: T) -> T:
        """Create a new entity in memory."""
        entity_id = getattr(entity, 'file_id', None) or getattr(entity, 'id', None)
        if not entity_id:
            raise ValueError("Entity must have 'file_id' or 'id' attribute")
        
        self._storage[entity_id] = entity
        return entity
    
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get entity by ID from memory."""
        return self._storage.get(entity_id)
    
    async def update(self, entity_id: str, entity: T) -> Optional[T]:
        """Update entity in memory."""
        if entity_id not in self._storage:
            return None
        
        self._storage[entity_id] = entity
        return entity
    
    async def delete(self, entity_id: str) -> bool:
        """Delete entity from memory."""
        if entity_id in self._storage:
            del self._storage[entity_id]
            return True
        return False
    
    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """List entities with pagination."""
        entities = list(self._storage.values())
        
        # Apply offset
        if offset > 0:
            entities = entities[offset:]
        
        # Apply limit
        if limit is not None:
            entities = entities[:limit]
        
        return entities
    
    async def count(self) -> int:
        """Count total entities."""
        return len(self._storage)
    
    async def exists(self, entity_id: str) -> bool:
        """Check if entity exists."""
        return entity_id in self._storage
    
    async def clear(self) -> None:
        """Clear all entities (useful for testing)."""
        self._storage.clear()
