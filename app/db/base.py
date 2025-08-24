import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy.engine import Dialect
import json


class GUID(TypeDecorator[uuid.UUID]):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36), storing as stringified hex values.
    """
    impl = VARCHAR
    cache_ok = True
    def load_dialect_impl(self, dialect: Dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(VARCHAR(36))
            return dialect.type_descriptor(VARCHAR(36))

    def process_bind_param(self, value: Optional[uuid.UUID], dialect) -> Optional[str]:
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value: Optional[str], dialect) -> Optional[uuid.UUID]:
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value


class JSONType(TypeDecorator[Dict[str, Any]]):
    """JSON type that stores data as TEXT and converts to/from Python dict."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Optional[Dict[str, Any]], dialect) -> Optional[str]:
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


# Create the base class
Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields for all database models."""
    
    __abstract__ = True
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_date = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    other_details = Column(JSONType, default=dict, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
