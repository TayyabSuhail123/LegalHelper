"""Health check API endpoints."""

from fastapi import APIRouter
from datetime import datetime

from app.core import settings
from app.models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthResponse: Current application health status
    """
    return HealthResponse(
        status="healthy",
        message="ContractCopilot backend is running successfully",
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        environment=settings.environment
    )


@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check endpoint.
    
    Returns:
        dict: Detailed system health information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "application": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "debug_mode": settings.debug
        },
        "system": {
            "python_version": "3.11+",
            "fastapi_version": "0.104.1"
        },
        "endpoints": {
            "health": "/health",
            "detailed_health": "/health/detailed",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }
