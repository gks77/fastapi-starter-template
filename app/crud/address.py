from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.address import Address
from app.schemas.address import AddressCreate, AddressUpdate


class CRUDAddress:
    """CRUD operations for Address model."""
    
    def get(self, db: Session, address_id: UUID) -> Optional[Address]:
        """Get address by ID."""
        return db.query(Address).filter(
            and_(
                Address.id == address_id,
                Address.is_deleted == False
            )
        ).first()
    
    def get_user_addresses(
        self, 
        db: Session, 
        user_id: UUID, 
        active_only: bool = True,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Address]:
        """Get all addresses for a specific user."""
        query = db.query(Address).filter(
            and_(
                Address.user_id == user_id,
                Address.is_deleted == False
            )
        )
        
        if active_only:
            query = query.filter(Address.is_active == True)
        
        # Order by default first, then by creation date
        query = query.order_by(Address.is_default.desc(), Address.created_date.desc())
        
        return query.offset(skip).limit(limit).all()
    
    def get_user_address(
        self, 
        db: Session, 
        user_id: UUID, 
        address_id: UUID
    ) -> Optional[Address]:
        """Get a specific address for a user."""
        return db.query(Address).filter(
            and_(
                Address.id == address_id,
                Address.user_id == user_id,
                Address.is_deleted == False
            )
        ).first()
    
    def get_default_address(
        self, 
        db: Session, 
        user_id: UUID
    ) -> Optional[Address]:
        """Get the default address for a user."""
        return db.query(Address).filter(
            and_(
                Address.user_id == user_id,
                Address.is_default == True,
                Address.is_active == True,
                Address.is_deleted == False
            )
        ).first()
    
    def create(
        self, 
        db: Session, 
        user_id: UUID, 
        obj_in: AddressCreate
    ) -> Address:
        """Create a new address for a user."""
        # If this is the user's first address or explicitly set as default,
        # make it the default address
        existing_addresses = self.get_user_addresses(db, user_id, active_only=True)
        
        if not existing_addresses or obj_in.is_default:
            # If setting as default, unset other default addresses
            if obj_in.is_default:
                self._unset_default_addresses(db, user_id)
            # If this is the first address, make it default
            elif not existing_addresses:
                obj_in.is_default = True
        
        # Create the address
        address_data = obj_in.model_dump()
        db_obj = Address(
            user_id=user_id,
            **address_data
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, 
        db: Session, 
        user_id: UUID, 
        address_id: UUID, 
        obj_in: AddressUpdate
    ) -> Optional[Address]:
        """Update a user's address."""
        db_obj = self.get_user_address(db, user_id, address_id)
        if not db_obj:
            return None
        
        # If setting as default, unset other default addresses
        if obj_in.is_default:
            self._unset_default_addresses(db, user_id, exclude_id=address_id)
        
        # Update the address
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def set_default_address(
        self, 
        db: Session, 
        user_id: UUID, 
        address_id: UUID
    ) -> Optional[Address]:
        """Set an address as the default for a user."""
        address = self.get_user_address(db, user_id, address_id)
        if not address or not address.is_active:
            return None
        
        # Unset current default
        self._unset_default_addresses(db, user_id)
        
        # Set new default
        address.is_default = True
        db.add(address)
        db.commit()
        db.refresh(address)
        return address
    
    def remove(
        self, 
        db: Session, 
        user_id: UUID, 
        address_id: UUID,
        soft_delete: bool = True
    ) -> Optional[Address]:
        """Delete a user's address (soft delete by default)."""
        address = self.get_user_address(db, user_id, address_id)
        if not address:
            return None
        
        was_default = address.is_default
        
        if soft_delete:
            # Soft delete - mark as deleted and inactive
            address.is_deleted = True
            address.is_active = False
            address.is_default = False
            db.add(address)
        else:
            # Hard delete
            db.delete(address)
        
        db.commit()
        
        # If this was the default address, set another active address as default
        if was_default:
            remaining_addresses = self.get_user_addresses(db, user_id, active_only=True)
            if remaining_addresses:
                remaining_addresses[0].is_default = True
                db.add(remaining_addresses[0])
                db.commit()
        
        return address
    
    def get_addresses_by_type(
        self, 
        db: Session, 
        user_id: UUID, 
        address_type: str,
        active_only: bool = True
    ) -> List[Address]:
        """Get addresses by type (shipping, billing, both)."""
        query = db.query(Address).filter(
            and_(
                Address.user_id == user_id,
                Address.address_type.in_([address_type, 'both']),
                Address.is_deleted == False
            )
        )
        
        if active_only:
            query = query.filter(Address.is_active == True)
        
        return query.order_by(Address.is_default.desc()).all()
    
    def _unset_default_addresses(
        self, 
        db: Session, 
        user_id: UUID, 
        exclude_id: Optional[UUID] = None
    ) -> None:
        """Helper method to unset all default addresses for a user."""
        query = db.query(Address).filter(
            and_(
                Address.user_id == user_id,
                Address.is_default == True,
                Address.is_deleted == False
            )
        )
        
        if exclude_id:
            query = query.filter(Address.id != exclude_id)
        
        for address in query.all():
            address.is_default = False
            db.add(address)
        
        db.commit()


# Create the CRUD instance
address = CRUDAddress()
