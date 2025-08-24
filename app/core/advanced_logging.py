"""
Advanced logging configuration with multiple storage backends.

This module provides comprehensive logging solutions including:
- File-based logging with rotation
- Elasticsearch integration
- Database logging for critical events
- Structured logging with context
- Performance monitoring
- Error tracking with Sentry
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union
import json
from pathlib import Path
import structlog
from loguru import logger as loguru_logger
from pythonjsonlogger import jsonlogger
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from elasticsearch import Elasticsearch
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# Database model for storing critical logs
LogBase = declarative_base()

class LogEntry(LogBase):
    """Database model for storing critical log entries."""
    __tablename__ = "log_entries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    level = Column(String(20), index=True)
    logger_name = Column(String(100), index=True)
    message = Column(Text)
    module = Column(String(100))
    function = Column(String(100))
    line_number = Column(Integer)
    extra_data = Column(Text)  # JSON string for additional context
    user_id = Column(String(100), index=True, nullable=True)
    request_id = Column(String(100), index=True, nullable=True)
    ip_address = Column(String(50), nullable=True)


class ElasticsearchHandler(logging.Handler):
    """Custom handler to send logs to Elasticsearch."""
    
    def __init__(self, elasticsearch_url: Optional[str] = None):
        super().__init__()
        self.es_client = None
        if elasticsearch_url:
            try:
                self.es_client = Elasticsearch([elasticsearch_url])
                # Test connection
                if self.es_client.ping():
                    print(f"✅ Connected to Elasticsearch at {elasticsearch_url}")
                else:
                    print(f"❌ Cannot connect to Elasticsearch at {elasticsearch_url}")
                    self.es_client = None
            except Exception as e:
                print(f"❌ Elasticsearch connection error: {e}")
                self.es_client = None
    
    def emit(self, record):
        """Send log record to Elasticsearch."""
        if not self.es_client:
            return
        
        try:
            log_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "process_id": os.getpid(),
                "thread_name": record.threadName,
            }
            
            # Add exception info if present
            if record.exc_info:
                log_data["exception"] = self.format(record)
            
            # Add extra fields
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
                log_data.update(extra_fields)
            
            # Index the log entry
            index_name = f"fastapi-logs-{datetime.now().strftime('%Y-%m')}"
            self.es_client.index(
                index=index_name,
                document=log_data
            )
            
        except Exception as e:
            # Don't let logging errors break the application
            print(f"Error sending log to Elasticsearch: {e}")


class DatabaseHandler(logging.Handler):
    """Custom handler to store critical logs in database."""
    
    def __init__(self, database_url: str):
        super().__init__()
        self.engine = create_engine(database_url)
        LogBase.metadata.create_all(self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.SessionLocal = SessionLocal
    
    def emit(self, record):
        """Store critical log record in database."""
        # Only store WARNING and above in database
        if record.levelno < logging.WARNING:
            return
        
        try:
            db = self.SessionLocal()
            
            # Extract extra fields
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
            
            log_entry = LogEntry(
                timestamp=datetime.now(timezone.utc),
                level=record.levelname,
                logger_name=record.name,
                message=record.getMessage(),
                module=record.module,
                function=record.funcName,
                line_number=record.lineno,
                extra_data=json.dumps(extra_fields, default=str) if extra_fields else None,
                user_id=extra_fields.get('user_id'),
                request_id=extra_fields.get('request_id'),
                ip_address=extra_fields.get('ip_address')
            )
            
            db.add(log_entry)
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"Error storing log in database: {e}")


class AdvancedLogger:
    """Advanced logger with multiple backends and structured logging."""
    
    def __init__(self, name: str = "fastapi-app"):
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_handlers()
        self._setup_structlog()
        self._setup_sentry()
    
    def _setup_handlers(self):
        """Set up all logging handlers."""
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # 1. Console Handler with JSON formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Use JSON formatter for structured logging
        json_formatter = jsonlogger.JsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s %(module)s %(funcName)s %(lineno)d",
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(json_formatter)
        
        # 2. Rotating File Handler
        file_handler = logging.handlers.RotatingFileHandler(
            logs_dir / "app.log",
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=10
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(json_formatter)
        
        # 3. Error File Handler (errors only)
        error_handler = logging.handlers.RotatingFileHandler(
            logs_dir / "errors.log",
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(json_formatter)
        
        # 4. Elasticsearch Handler
        es_url = os.getenv("ELASTICSEARCH_URL")
        if es_url:
            es_handler = ElasticsearchHandler(es_url)
            es_handler.setLevel(logging.INFO)
            self.logger.addHandler(es_handler)
        
        # 5. Database Handler for critical logs
        try:
            db_handler = DatabaseHandler(settings.get_database_url())
            db_handler.setLevel(logging.WARNING)
            self.logger.addHandler(db_handler)
        except Exception as e:
            print(f"Could not setup database logging: {e}")
        
        # Add all handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        
        # Prevent propagation to avoid duplicate logs
        self.logger.propagate = False
    
    def _setup_structlog(self):
        """Configure structlog for structured logging."""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    def _setup_sentry(self):
        """Configure Sentry for error tracking."""
        sentry_dsn = os.getenv("SENTRY_DSN")
        if sentry_dsn:
            sentry_logging = LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            )
            
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[sentry_logging],
                traces_sample_rate=0.1,
                environment=os.getenv("ENVIRONMENT", "development")
            )
            print("✅ Sentry error tracking initialized")
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Get a logger instance."""
        logger_name = f"{self.name}.{name}" if name else self.name
        return logging.getLogger(logger_name)
    
    def get_structlog(self, name: Optional[str] = None):
        """Get a structlog instance."""
        logger_name = f"{self.name}.{name}" if name else self.name
        return structlog.get_logger(logger_name)


class BusinessLogger:
    """Specialized logger for business events and analytics."""
    
    def __init__(self, logger_name: str = "business"):
        self.logger = logging.getLogger(f"fastapi-app.{logger_name}")
        self.structlog = structlog.get_logger(f"fastapi-app.{logger_name}")
    
    def user_action(self, action: str, user_id: str, **context):
        """Log user actions for analytics."""
        self.logger.info(
            f"User action: {action}",
            extra={
                "event_type": "user_action",
                "action": action,
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **context
            }
        )
    
    def api_performance(self, endpoint: str, method: str, duration: float, status_code: int, **context):
        """Log API performance metrics."""
        self.logger.info(
            f"API call: {method} {endpoint}",
            extra={
                "event_type": "api_performance",
                "endpoint": endpoint,
                "method": method,
                "duration_ms": duration * 1000,
                "status_code": status_code,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **context
            }
        )
    
    def business_event(self, event_name: str, **context):
        """Log business events for analysis."""
        self.logger.info(
            f"Business event: {event_name}",
            extra={
                "event_type": "business_event",
                "event_name": event_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **context
            }
        )
    
    def security_event(self, event_type: str, severity: str = "medium", **context):
        """Log security-related events."""
        log_level = logging.WARNING if severity in ["medium", "high"] else logging.INFO
        
        self.logger.log(
            log_level,
            f"Security event: {event_type}",
            extra={
                "event_type": "security_event",
                "security_event_type": event_type,
                "severity": severity,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **context
            }
        )


# Initialize advanced logging
advanced_logger = AdvancedLogger()
business_logger = BusinessLogger()

# Export logger instances
app_logger = advanced_logger.get_logger()
struct_logger = advanced_logger.get_structlog()

# Loguru setup for even more advanced features
loguru_logger.add(
    "logs/app_loguru.log",
    rotation="100 MB",
    retention="30 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message} | {extra}",
    serialize=True  # JSON format
)
