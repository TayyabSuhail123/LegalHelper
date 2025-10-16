"""Pydantic models for API responses."""

from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime


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
    data: Dict[str, Any] = {}
    timestamp: datetime
