import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common fields for all Pydantic models."""
    
    id: uuid.UUID = Field(..., description="Unique identifier")
    created_date: datetime = Field(..., description="Creation timestamp")
    updated_date: datetime = Field(..., description="Last update timestamp")
    other_details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional JSON data")
    is_deleted: bool = Field(default=False, description="Soft delete flag")
    
    model_config = ConfigDict(from_attributes=True)


class BaseCreateSchema(BaseModel):
    """Base schema for creating new records."""
    
    other_details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional JSON data")
    
    model_config = ConfigDict(from_attributes=True)


class BaseUpdateSchema(BaseModel):
    """Base schema for updating existing records."""
    
    other_details: Optional[Dict[str, Any]] = Field(None, description="Additional JSON data")
    is_deleted: Optional[bool] = Field(None, description="Soft delete flag")
    
    model_config = ConfigDict(from_attributes=True)
