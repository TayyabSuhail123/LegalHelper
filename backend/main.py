"""ContractCopilot FastAPI Backend Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core import settings
from app.api import health_router


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """

    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-Powered Legal Document Risk Scanner",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health_router, prefix=settings.api_v1_prefix, tags=["health"])

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return JSONResponse(
            content={
                "message": f"Welcome to {settings.app_name}",
                "version": settings.app_version,
                "docs": "/docs",
                "health": f"{settings.api_v1_prefix}/health",
            }
        )

    return app


# Create app instance
app = create_app()
