"""
Structured logging configuration for the application.

This module provides enterprise-grade logging with structured output,
proper log levels, and context preservation.
"""

import logging
import sys
from typing import Any, Dict, Optional, Union
from datetime import datetime, timezone
import json
from app.core.config import settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as structured JSON."""
        log_data: Dict[str, Union[str, int, Any]] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields from the log record
        extra_fields = {
            k: v for k, v in record.__dict__.items()
            if k not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created',
                'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'message', 'exc_info', 'exc_text',
                'stack_info'
            }
        }
        
        if extra_fields:
            log_data["extra"] = extra_fields
        
        return json.dumps(log_data, default=str)


class ProductLogger:
    """Specialized logger for product operations with context."""
    
    def __init__(self, name: str = "product"):
        self.logger = logging.getLogger(f"{settings.PROJECT_NAME}.{name}")
    
    def _log(
        self, 
        level: int, 
        message: str, 
        **context: Any
    ) -> None:
        """Log with structured context."""
        self.logger.log(level, message, extra=context)
    
    def info(self, message: str, **context: Any) -> None:
        """Log info level message with context."""
        self._log(logging.INFO, message, **context)
    
    def warning(self, message: str, **context: Any) -> None:
        """Log warning level message with context."""
        self._log(logging.WARNING, message, **context)
    
    def error(self, message: str, **context: Any) -> None:
        """Log error level message with context."""
        self._log(logging.ERROR, message, **context)
    
    def debug(self, message: str, **context: Any) -> None:
        """Log debug level message with context."""
        self._log(logging.DEBUG, message, **context)
    
    def product_created(
        self, 
        product_id: str, 
        product_name: str, 
        sku: str,
        user_id: Optional[str] = None
    ) -> None:
        """Log product creation event."""
        self.info(
            "Product created successfully",
            event_type="product_created",
            product_id=product_id,
            product_name=product_name,
            sku=sku,
            user_id=user_id
        )
    
    def product_updated(
        self, 
        product_id: str, 
        changes: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> None:
        """Log product update event."""
        self.info(
            "Product updated successfully",
            event_type="product_updated",
            product_id=product_id,
            changes=changes,
            user_id=user_id
        )
    
    def product_deleted(
        self, 
        product_id: str, 
        user_id: Optional[str] = None
    ) -> None:
        """Log product deletion event."""
        self.info(
            "Product deleted successfully",
            event_type="product_deleted",
            product_id=product_id,
            user_id=user_id
        )
    
    def inventory_updated(
        self, 
        product_id: str, 
        old_quantity: int, 
        new_quantity: int,
        reason: str,
        user_id: Optional[str] = None
    ) -> None:
        """Log inventory update event."""
        self.info(
            "Product inventory updated",
            event_type="inventory_updated",
            product_id=product_id,
            old_quantity=old_quantity,
            new_quantity=new_quantity,
            quantity_change=new_quantity - old_quantity,
            reason=reason,
            user_id=user_id
        )
    
    def low_stock_alert(
        self, 
        product_id: str, 
        product_name: str,
        current_quantity: int, 
        threshold: int
    ) -> None:
        """Log low stock alert."""
        self.warning(
            "Low stock alert triggered",
            event_type="low_stock_alert",
            product_id=product_id,
            product_name=product_name,
            current_quantity=current_quantity,
            threshold=threshold
        )


# Configure root logger
def setup_logging() -> None:
    """Set up structured logging for the application."""
    
    # Create logger
    logger = logging.getLogger(settings.PROJECT_NAME)
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Use structured formatter
    formatter = StructuredFormatter()
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent duplicate log messages
    logger.propagate = False


# Initialize logging
setup_logging()

# Create default logger instances
logger = logging.getLogger(settings.PROJECT_NAME)
product_logger = ProductLogger()
