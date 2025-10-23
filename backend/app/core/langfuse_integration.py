"""
LangFuse integration for tracing AI agents and workflows.
Implements hierarchical tracing: workflow trace contains agent spans.
"""

import logging
import os
from typing import Any

try:
    from langfuse import get_client, observe

    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    observe = None
    get_client = None

logger = logging.getLogger(__name__)


def get_langfuse_client():
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

        client = get_client()
        logger.info("LangFuse client retrieved successfully")
        return client

    except Exception as e:
        logger.error(f"Failed to get LangFuse client: {e}")
        return None


def trace_workflow(workflow_name: str):
    """Decorator to trace an entire workflow as the root span."""

    def decorator(func):
        if not LANGFUSE_AVAILABLE or not observe:
            # Return undecorated function if LangFuse is not available
            return func

        # Use the @observe decorator with workflow name
        decorated_func = observe(name=workflow_name)(func)
        return decorated_func

    return decorator


def trace_agent(agent_name: str):
    """Decorator to trace individual agent execution as child spans."""

    def decorator(func):
        if not LANGFUSE_AVAILABLE or not observe:
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
        langfuse = get_client()
        if langfuse:
            langfuse.event(name=event_name, input=data)
            logger.info(f"Logged workflow event: {event_name}")
    except Exception as e:
        logger.error(f"Failed to log workflow event {event_name}: {e}")


def flush_langfuse():
    """Flush any pending LangFuse events."""
    client = get_langfuse_client()
    if client:
        try:
            client.flush()
            logger.info("LangFuse events flushed")
        except Exception as e:
            logger.error(f"Failed to flush LangFuse events: {e}")
