from sqlalchemy import Boolean, Column, String, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base import BaseModel, GUID


class Address(BaseModel):
    """Address model for e-commerce platform with multiple addresses per user."""
    
    __tablename__ = "addresses"

    # Foreign key to user
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Address details
    label = Column(String(100), nullable=False)  # e.g., "Home", "Office", "Billing"
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    company = Column(String(200), nullable=True)
    
    # Address lines
    address_line_1 = Column(String(255), nullable=False)
    address_line_2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False, default="US")
    
    # Contact information
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)  # Optional, different from user email
    
    # Address type and status
    address_type = Column(String(20), nullable=False, default="shipping")  # shipping, billing, both
    is_default = Column(Boolean, default=False, nullable=False)  # Default address for this user
    is_active = Column(Boolean, default=True, nullable=False)  # Can be deactivated without deletion
    
    # Special instructions for delivery
    delivery_instructions = Column(Text, nullable=True)
    
    # Image attribute
    image_url = Column(String(500), nullable=True)
    
    # Relationship to user
    user = relationship("User", back_populates="addresses")
    
    # Indexes for better performance
    __table_args__ = (
        Index("idx_address_user_id", "user_id"),
        Index("idx_address_user_default", "user_id", "is_default"),
        Index("idx_address_user_active", "user_id", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<Address(id={self.id}, user_id={self.user_id}, label='{self.label}', is_default={self.is_default})>"
    
    @property
    def full_name(self) -> str:
        """Get the full name for this address."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def full_address(self) -> str:
        """Get the formatted full address."""
        parts = [str(self.address_line_1)]
        if self.address_line_2:
            parts.append(str(self.address_line_2))
        parts.append(f"{self.city}, {self.state} {self.postal_code}")
        parts.append(str(self.country))
        return "\n".join(parts)
    
    @property
    def address_summary(self) -> str:
        """Get a short summary of the address for display."""
        return f"{self.label}: {self.address_line_1}, {self.city}, {self.state}"
