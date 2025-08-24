from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.crud.address import address
from app.models.user import User
from app.schemas.address import (
    AddressCreate, 
    AddressUpdate, 
    AddressPublic, 
    AddressSummary,
    SetDefaultAddressRequest,
    AddressResponse
)

router = APIRouter()


@router.get("/", response_model=List[AddressPublic])
def get_user_addresses(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    active_only: bool = True,
    address_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[AddressPublic]:
    """
    Get all addresses for the current user.
    
    - **active_only**: Only return active addresses (default: true)
    - **address_type**: Filter by address type (shipping, billing, both)
    - **skip**: Number of addresses to skip (pagination)
    - **limit**: Maximum number of addresses to return
    """
    if address_type:
        addresses = address.get_addresses_by_type(
            db=db, 
            user_id=current_user.id, 
            address_type=address_type,
            active_only=active_only
        )
    else:
        addresses = address.get_user_addresses(
            db=db, 
            user_id=current_user.id, 
            active_only=active_only,
            skip=skip, 
            limit=limit
        )
    
    return [AddressPublic.model_validate(addr) for addr in addresses]


@router.get("/default", response_model=Optional[AddressPublic])
def get_default_address(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Optional[AddressPublic]:
    """
    Get the default address for the current user.
    """
    default_address = address.get_default_address(db=db, user_id=current_user.id)
    if not default_address:
        return None
    
    return AddressPublic.model_validate(default_address)


@router.get("/{address_id}", response_model=AddressPublic)
def get_address(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    address_id: UUID
) -> AddressPublic:
    """
    Get a specific address by ID.
    """
    user_address = address.get_user_address(
        db=db, 
        user_id=current_user.id, 
        address_id=address_id
    )
    if not user_address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    return AddressPublic.model_validate(user_address)


@router.post("/", response_model=AddressPublic, status_code=status.HTTP_201_CREATED)
def create_address(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    address_in: AddressCreate
) -> AddressPublic:
    """
    Create a new address for the current user.
    
    If this is the user's first address, it will automatically be set as default.
    """
    new_address = address.create(
        db=db, 
        user_id=current_user.id, 
        obj_in=address_in
    )
    
    return AddressPublic.model_validate(new_address)


@router.put("/{address_id}", response_model=AddressPublic)
def update_address(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    address_id: UUID,
    address_in: AddressUpdate
) -> AddressPublic:
    """
    Update an existing address.
    """
    updated_address = address.update(
        db=db, 
        user_id=current_user.id, 
        address_id=address_id, 
        obj_in=address_in
    )
    
    if not updated_address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    return AddressPublic.model_validate(updated_address)


@router.post("/set-default", response_model=AddressResponse)
def set_default_address(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: SetDefaultAddressRequest
) -> AddressResponse:
    """
    Set an address as the default address for the current user.
    """
    default_address = address.set_default_address(
        db=db, 
        user_id=current_user.id, 
        address_id=request.address_id
    )
    
    if not default_address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found or inactive"
        )
    
    return AddressResponse(
        success=True,
        message="Address set as default successfully",
        address=AddressPublic.model_validate(default_address)
    )


@router.delete("/{address_id}", response_model=AddressResponse)
def delete_address(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    address_id: UUID,
    hard_delete: bool = False
) -> AddressResponse:
    """
    Delete an address (soft delete by default).
    
    - **hard_delete**: If true, permanently delete the address. If false, just mark as deleted.
    """
    deleted_address = address.remove(
        db=db, 
        user_id=current_user.id, 
        address_id=address_id,
        soft_delete=not hard_delete
    )
    
    if not deleted_address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    delete_type = "permanently deleted" if hard_delete else "deactivated"
    return AddressResponse(
        success=True,
        message=f"Address {delete_type} successfully",
        address=None
    )


@router.get("/type/{address_type}", response_model=List[AddressSummary])
def get_addresses_by_type(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    address_type: str,
    active_only: bool = True
) -> List[AddressSummary]:
    """
    Get addresses by type (shipping, billing, both).
    
    - **address_type**: The type of addresses to retrieve (shipping, billing, both)
    - **active_only**: Only return active addresses (default: true)
    """
    if address_type not in ['shipping', 'billing', 'both']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="address_type must be one of: shipping, billing, both"
        )
    
    addresses = address.get_addresses_by_type(
        db=db, 
        user_id=current_user.id, 
        address_type=address_type,
        active_only=active_only
    )
    
    return [AddressSummary.model_validate(addr) for addr in addresses]
