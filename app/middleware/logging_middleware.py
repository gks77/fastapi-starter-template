"""
Logging middleware for FastAPI applications.

This middleware automatically logs all HTTP requests and responses with
detailed information for monitoring and analysis.
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import json

from app.core.advanced_logging import business_logger, app_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Extract request details
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        method = request.method
        url = str(request.url)
        
        # Log request start
        app_logger.info(
            f"Request started: {method} {url}",
            extra={
                "event_type": "request_start",
                "request_id": request_id,
                "method": method,
                "url": url,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "headers": dict(request.headers)
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log successful response
            app_logger.info(
                f"Request completed: {method} {url}",
                extra={
                    "event_type": "request_completed",
                    "request_id": request_id,
                    "method": method,
                    "url": url,
                    "status_code": response.status_code,
                    "duration_seconds": duration,
                    "client_ip": client_ip
                }
            )
            
            # Log performance metrics
            business_logger.api_performance(
                endpoint=request.url.path,
                method=method,
                duration=duration,
                status_code=response.status_code,
                request_id=request_id,
                client_ip=client_ip
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate duration for failed requests
            duration = time.time() - start_time
            
            # Log error
            app_logger.error(
                f"Request failed: {method} {url}",
                extra={
                    "event_type": "request_failed",
                    "request_id": request_id,
                    "method": method,
                    "url": url,
                    "duration_seconds": duration,
                    "client_ip": client_ip,
                    "error": str(e)
                },
                exc_info=True
            )
            
            # Re-raise the exception
            raise


class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for security-related logging."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.suspicious_patterns = [
            "sql", "union", "select", "drop", "delete", "insert",
            "<script>", "javascript:", "onload=", "onerror=",
            "../", "etc/passwd", "cmd.exe", "powershell"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check for security threats and log suspicious activity."""
        
        # Check for suspicious patterns in URL and query parameters
        url_lower = str(request.url).lower()
        is_suspicious = any(pattern in url_lower for pattern in self.suspicious_patterns)
        
        if is_suspicious:
            business_logger.security_event(
                "suspicious_request_pattern",
                severity="medium",
                url=str(request.url),
                client_ip=request.client.host if request.client else "unknown",
                user_agent=request.headers.get("user-agent", "unknown"),
                patterns_found=[p for p in self.suspicious_patterns if p in url_lower]
            )
        
        # Check for unusual request sizes
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB
            business_logger.security_event(
                "large_request_body",
                severity="low",
                content_length=content_length,
                url=str(request.url),
                client_ip=request.client.host if request.client else "unknown"
            )
        
        # Process request normally
        response = await call_next(request)
        
        # Log failed authentication attempts
        if response.status_code == 401:
            business_logger.security_event(
                "authentication_failure",
                severity="medium",
                url=str(request.url),
                client_ip=request.client.host if request.client else "unknown",
                user_agent=request.headers.get("user-agent", "unknown")
            )
        
        return response
