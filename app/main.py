from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError, HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.api.api import api_router
from app.core.config import settings
from app.core.exception_handlers import (
    validation_exception_handler,
    pydantic_validation_exception_handler,
    http_exception_handler,
    integrity_error_handler,
    general_exception_handler
)
from app.core.advanced_logging import advanced_logger, business_logger
from app.middleware.logging_middleware import LoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    from app.db.init_db import init_db
    from app.core.advanced_logging import advanced_logger
    
    # Initialize database
    init_db()
    
    # Log application startup
    logger = advanced_logger.get_logger()
    logger.info("FastAPI application starting up", extra={"event": "startup"})
    
    yield
    
    # Shutdown - add any cleanup here if needed
    logger.info("FastAPI application shutting down", extra={"event": "shutdown"})


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Create FastAPI app with lifespan
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Create uploads directory if it doesn't exist
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)

    # Mount static files for serving uploaded images
    app.mount("/static", StaticFiles(directory="uploads"), name="static")

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add logging middleware
    app.add_middleware(LoggingMiddleware)

    # Include API router
    app.include_router(api_router)

    # Add exception handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    @app.get("/")
    async def root():
        """Root endpoint - API health check."""
        return {
            "message": f"Welcome to {settings.PROJECT_NAME}",
            "version": settings.VERSION,
            "docs": "/docs",
            "redoc": "/redoc"
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION
        }
    
    return app


# Create the app instance
app = create_app()
