"""
LangFuse integration for tracing AI agents and workflows.
Implements hierarchical tracing: workflow trace contains agent spans.
"""

import logging
import os
from typing import Any, Callable, Optional, TypeVar

# Initialize variables for type checking
observe: Optional[Callable[..., Any]] = None
get_client: Optional[Callable[..., Any]] = None

try:
    from langfuse import get_client, observe

    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    observe = None
    get_client = None

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


def get_langfuse_client() -> Any:
    """Get the LangFuse client."""
    if not LANGFUSE_AVAILABLE:
        logger.warning("LangFuse is not available. Tracing will be disabled.")
        return None

    try:
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

        if not public_key or not secret_key:
            logger.warning("LangFuse credentials not found. Tracing will be disabled.")
            return None

        if get_client is None:
            logger.warning("LangFuse get_client function not available.")
            return None

        client = get_client()
        logger.info("LangFuse client retrieved successfully")
        return client

    except Exception as e:
        logger.error(f"Failed to get LangFuse client: {e}")
        return None


def trace_workflow(workflow_name: str) -> Callable[[F], F]:
    """Decorator to trace an entire workflow as the root span."""

    def decorator(func: F) -> F:
        if not LANGFUSE_AVAILABLE or observe is None:
            # Return undecorated function if LangFuse is not available
            return func

        # Use the @observe decorator with workflow name
        decorated_func = observe(name=workflow_name)(func)
        return decorated_func

    return decorator


def trace_agent(agent_name: str) -> Callable[[F], F]:
    """Decorator to trace individual agent execution as child spans."""

    def decorator(func: F) -> F:
        if not LANGFUSE_AVAILABLE or observe is None:
            # Return undecorated function if LangFuse is not available
            return func

        # Use the @observe decorator with agent name
        decorated_func = observe(name=agent_name)(func)
        return decorated_func

    return decorator


def log_workflow_event(event_name: str, data: dict[str, Any]) -> None:
    """Log a workflow event as an event in the current trace context."""
    if not LANGFUSE_AVAILABLE:
        return

    try:
        # Use langfuse.event() to create an event within the current trace
        langfuse_client = get_langfuse_client()
        if langfuse_client and hasattr(langfuse_client, 'event'):
            langfuse_client.event(name=event_name, input=data)
            logger.info(f"Logged workflow event: {event_name}")
        else:
            logger.debug(f"LangFuse event logging not available for: {event_name}")
    except Exception as e:
        logger.error(f"Failed to log workflow event {event_name}: {e}")


def flush_langfuse() -> None:
    """Flush any pending LangFuse events."""
    client = get_langfuse_client()
    if client:
        try:
            client.flush()
            logger.info("LangFuse events flushed")
        except Exception as e:
            logger.error(f"Failed to flush LangFuse events: {e}")
