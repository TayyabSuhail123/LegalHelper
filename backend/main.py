"""ContractCopilot FastAPI Backend Application."""

import logging
import traceback
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core import settings
from app.api import health_router
from app.api.files import router as files_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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

    # Add global exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler to catch and log all unhandled exceptions."""
        logger.error(f"Global exception handler caught: {type(exc).__name__}")
        logger.error(f"Exception details: {str(exc)}")
        logger.error(f"Request URL: {request.url}")
        logger.error(f"Request method: {request.method}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error_type": type(exc).__name__,
                "error_message": str(exc) if settings.debug else "Internal server error"
            }
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """HTTP exception handler to log HTTP exceptions."""
        logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
        logger.warning(f"Request URL: {request.url}")
        logger.warning(f"Request method: {request.method}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Validation exception handler to log validation errors."""
        logger.warning(f"Validation error: {exc.errors()}")
        logger.warning(f"Request URL: {request.url}")
        logger.warning(f"Request method: {request.method}")
        
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()}
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
    app.include_router(files_router, prefix=f"{settings.api_v1_prefix}/files", tags=["files"])

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
