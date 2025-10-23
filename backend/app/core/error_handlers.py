"""
Common error handling utilities for the application.
"""

import logging
import traceback
from typing import Any

from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)


class APIErrorHandler:
    """Centralized error handling for API endpoints."""

    @staticmethod
    def handle_api_exception(
        e: Exception, context: str, file_id: str | None = None, status_code: int = 500
    ) -> HTTPException:
        """
        Handle API exceptions with consistent logging and response format.

        Args:
            e: The exception that occurred
            context: Context description for logging
            file_id: Optional file ID for tracking
            status_code: HTTP status code to return

        Returns:
            HTTPException with appropriate error details
        """
        error_id = f"{context}_{file_id}" if file_id else context

        # Log the error with full context
        logger.error(f"API Error [{error_id}]: {str(e)}")
        logger.error(f"Context: {context}")
        if file_id:
            logger.error(f"File ID: {file_id}")
        logger.error(f"Exception type: {type(e).__name__}")

        # Include traceback in debug mode
        if settings.debug:
            logger.error(f"Traceback: {traceback.format_exc()}")

        # Determine error message based on environment
        if settings.debug or settings.environment == "development":
            detail = f"{context}: {str(e)}"
        else:
            # Generic message for production
            detail = "An error occurred while processing your request. Please try again."

        return HTTPException(
            status_code=status_code,
            detail={
                "error": detail,
                "context": context,
                "error_type": type(e).__name__,
                "file_id": file_id,
            },
        )

    @staticmethod
    def handle_validation_error(
        field_name: str, field_value: Any, constraint: str
    ) -> HTTPException:
        """Handle validation errors with consistent format."""
        error_msg = f"Invalid {field_name}: {constraint}"
        logger.warning(f"Validation error: {error_msg} (value: {field_value})")

        return HTTPException(
            status_code=400,
            detail={
                "error": error_msg,
                "field": field_name,
                "value": field_value,
                "constraint": constraint,
            },
        )

    @staticmethod
    def handle_not_found_error(resource_type: str, resource_id: str) -> HTTPException:
        """Handle resource not found errors."""
        error_msg = f"{resource_type} {resource_id} not found"
        logger.warning(f"Resource not found: {error_msg}")

        return HTTPException(
            status_code=404,
            detail={"error": error_msg, "resource_type": resource_type, "resource_id": resource_id},
        )


class AgentErrorHandler:
    """Error handling for agent operations."""

    @staticmethod
    def handle_agent_error(
        agent_name: str, step_name: str, error: Exception, state: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Handle agent errors and update state consistently.

        Args:
            agent_name: Name of the agent that failed
            step_name: Processing step that failed
            error: The exception that occurred
            state: Current state dictionary

        Returns:
            Updated state with error information
        """
        error_msg = f"{agent_name}: {str(error)}"

        # Log the error with context
        logger.error(f"Agent Error [{agent_name}]: {str(error)}")
        logger.error(f"Step: {step_name}")
        logger.error(f"File ID: {state.get('file_id', 'unknown')}")

        if settings.debug:
            logger.error(f"Traceback: {traceback.format_exc()}")

        # Update state with error information
        state["error_message"] = error_msg
        state["failed_step"] = step_name
        state["current_step"] = f"Failed at {step_name}"

        return state


class ValidationUtils:
    """Common validation utilities."""

    @staticmethod
    def validate_file_id(file_id: str) -> str:
        """Validate file ID format."""
        import uuid

        try:
            uuid.UUID(file_id)
            return file_id
        except ValueError:
            raise APIErrorHandler.handle_validation_error(
                "file_id", file_id, "must be a valid UUID"
            )

    @staticmethod
    def validate_pagination(limit: int, offset: int, max_limit: int = 100) -> tuple[int, int]:
        """Validate pagination parameters."""
        if limit <= 0 or limit > max_limit:
            raise APIErrorHandler.handle_validation_error(
                "limit", limit, f"must be between 1 and {max_limit}"
            )

        if offset < 0:
            raise APIErrorHandler.handle_validation_error("offset", offset, "must be non-negative")

        return limit, offset

    @staticmethod
    def validate_file_size(file_size: int, max_size: int) -> bool:
        """Validate file size."""
        if file_size > max_size:
            raise APIErrorHandler.handle_validation_error(
                "file_size", file_size, f"must not exceed {max_size} bytes"
            )
        return True


# Context managers for error handling
class error_context:
    """Context manager for consistent error handling."""

    def __init__(self, context: str, file_id: str | None = None):
        self.context = context
        self.file_id = file_id

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and exc_type != HTTPException:
            # Log the error but don't suppress it
            logger.error(f"Error in {self.context}: {exc_val}")
            if self.file_id:
                logger.error(f"File ID: {self.file_id}")
            if settings.debug:
                logger.error(f"Traceback: {traceback.format_exc()}")
        return False  # Don't suppress the exception
