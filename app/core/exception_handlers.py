"""Custom exception handlers for the FastAPI application."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error on {request.url}: {exc.errors()}")
    
    # Safely handle body to avoid FormData serialization issues
    body_content = None
    if hasattr(exc, 'body') and exc.body is not None:
        # Convert FormData to dict or handle bytes/string
        if hasattr(exc.body, '_fields'):  # FormData object
            body_content = dict(exc.body)
        elif isinstance(exc.body, (str, bytes)):
            body_content = exc.body if isinstance(exc.body, str) else exc.body.decode('utf-8', errors='ignore')
        else:
            body_content = str(exc.body)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation Error",
            "errors": exc.errors(),
            "body": body_content
        }
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(f"Pydantic validation error on {request.url}: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation Error",
            "errors": exc.errors()
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with enhanced logging."""
    logger.warning(f"HTTP {exc.status_code} on {request.url}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        },
        headers=exc.headers
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors."""
    logger.error(f"Database integrity error on {request.url}: {str(exc.orig)}")
    
    # Extract meaningful error message
    error_message = "Database constraint violation"
    if "UNIQUE constraint failed" in str(exc.orig):
        error_message = "Resource already exists"
    elif "FOREIGN KEY constraint failed" in str(exc.orig):
        error_message = "Referenced resource does not exist"
    elif "NOT NULL constraint failed" in str(exc.orig):
        error_message = "Required field is missing"
    
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": error_message,
            "type": "integrity_error"
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error on {request.url}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "type": "server_error"
        }
    )
