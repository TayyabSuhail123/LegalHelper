"""Pydantic models for API responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    message: str
    timestamp: datetime
    version: str
    environment: str


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str
    message: str
    timestamp: datetime


class SuccessResponse(BaseModel):
    """Standard success response model."""

    success: bool
    message: str
    data: dict[str, Any] = {}
    timestamp: datetime
