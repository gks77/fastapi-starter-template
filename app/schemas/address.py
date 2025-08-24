from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID
from app.schemas.base import BaseSchema


class AddressBase(BaseModel):
    """Base address schema with common fields."""
    
    label: str = Field(..., min_length=1, max_length=100, description="Address label like 'Home', 'Office', 'Billing'")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name for this address")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name for this address")
    company: Optional[str] = Field(None, max_length=200, description="Company name (optional)")
    
    address_line_1: str = Field(..., min_length=1, max_length=255, description="Primary address line")
    address_line_2: Optional[str] = Field(None, max_length=255, description="Secondary address line (apartment, suite, etc.)")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    state: str = Field(..., min_length=1, max_length=100, description="State or province")
    postal_code: str = Field(..., min_length=1, max_length=20, description="Postal or ZIP code")
    country: str = Field(default="US", min_length=2, max_length=100, description="Country code or name")
    
    phone: Optional[str] = Field(None, max_length=20, description="Phone number for this address")
    email: Optional[str] = Field(None, max_length=255, description="Email for this address (optional)")
    
    address_type: str = Field(default="shipping", description="Address type: shipping, billing, or both")
    is_default: bool = Field(default=False, description="Whether this is the default address")
    delivery_instructions: Optional[str] = Field(None, description="Special delivery instructions")
    
    @field_validator('address_type')
    @classmethod
    def validate_address_type(cls, v: str) -> str:
        allowed_types = ['shipping', 'billing', 'both']
        if v not in allowed_types:
            raise ValueError(f'address_type must be one of: {", ".join(allowed_types)}')
        return v
    
    @field_validator('postal_code')
    @classmethod
    def validate_postal_code(cls, v: str) -> str:
        # Basic validation - remove spaces and ensure it's not empty
        cleaned = v.strip().replace(' ', '')
        if not cleaned:
            raise ValueError('postal_code cannot be empty')
        return cleaned
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v:
            # Remove common phone formatting
            cleaned = ''.join(filter(str.isdigit, v))
            if len(cleaned) < 10:
                raise ValueError('phone must contain at least 10 digits')
        return v


class AddressCreate(AddressBase):
    """Schema for creating a new address."""
    pass


class AddressUpdate(BaseModel):
    """Schema for updating an existing address."""
    
    label: Optional[str] = Field(None, min_length=1, max_length=100)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    company: Optional[str] = Field(None, max_length=200)
    
    address_line_1: Optional[str] = Field(None, min_length=1, max_length=255)
    address_line_2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, min_length=1, max_length=20)
    country: Optional[str] = Field(None, min_length=2, max_length=100)
    
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    
    address_type: Optional[str] = Field(None)
    is_default: Optional[bool] = Field(None)
    is_active: Optional[bool] = Field(None)
    delivery_instructions: Optional[str] = Field(None)
    
    @field_validator('address_type')
    @classmethod
    def validate_address_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed_types = ['shipping', 'billing', 'both']
            if v not in allowed_types:
                raise ValueError(f'address_type must be one of: {", ".join(allowed_types)}')
        return v


class AddressPublic(BaseSchema):
    """Public address schema for API responses."""
    
    id: UUID
    user_id: UUID
    label: str
    first_name: str
    last_name: str
    company: Optional[str]
    
    address_line_1: str
    address_line_2: Optional[str]
    city: str
    state: str
    postal_code: str
    country: str
    
    phone: Optional[str]
    email: Optional[str]
    
    address_type: str
    is_default: bool
    is_active: bool
    delivery_instructions: Optional[str]
    
    created_date: datetime
    updated_date: datetime
    
    # Computed fields
    full_name: str
    address_summary: str
    
    class Config:
        from_attributes = True


class AddressSummary(BaseModel):
    """Simplified address schema for lists and summaries."""
    
    id: UUID
    label: str
    address_summary: str
    is_default: bool
    is_active: bool
    address_type: str
    
    class Config:
        from_attributes = True


class SetDefaultAddressRequest(BaseModel):
    """Schema for setting a default address."""
    
    address_id: UUID = Field(..., description="ID of the address to set as default")


class AddressResponse(BaseModel):
    """Response schema for address operations."""
    
    success: bool
    message: str
    address: Optional[AddressPublic] = None
