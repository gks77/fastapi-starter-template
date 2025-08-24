"""
Custom exception classes for the application.

This module defines custom exceptions with structured error handling
for better error tracking and user experience.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class FastUsersException(Exception):
    """Base exception class for the Fast Users application."""
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None
    ):
        self.message = message
        self.details = details or {}
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(FastUsersException):
    """Raised when data validation fails."""
    pass


class BusinessLogicError(FastUsersException):
    """Raised when business logic constraints are violated."""
    pass


class ResourceNotFoundError(FastUsersException):
    """Raised when a requested resource is not found."""
    pass


class DuplicateResourceError(FastUsersException):
    """Raised when trying to create a resource that already exists."""
    pass


class InsufficientPermissionsError(FastUsersException):
    """Raised when user lacks required permissions."""
    pass


class DatabaseError(FastUsersException):
    """Raised when database operations fail."""
    pass


# Product-specific exceptions
class ProductNotFoundError(ResourceNotFoundError):
    """Raised when a product is not found."""
    
    def __init__(self, product_id: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Product with ID {product_id} not found",
            details,
            "PRODUCT_NOT_FOUND"
        )


class ProductSKUExistsError(DuplicateResourceError):
    """Raised when trying to create a product with an existing SKU."""
    
    def __init__(self, sku: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Product with SKU '{sku}' already exists",
            details,
            "PRODUCT_SKU_EXISTS"
        )


class ProductSlugExistsError(DuplicateResourceError):
    """Raised when trying to create a product with an existing slug."""
    
    def __init__(self, slug: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Product with slug '{slug}' already exists",
            details,
            "PRODUCT_SLUG_EXISTS"
        )


class InvalidPriceError(ValidationError):
    """Raised when product pricing is invalid."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, "INVALID_PRICE")


class InsufficientInventoryError(BusinessLogicError):
    """Raised when there's insufficient inventory for an operation."""
    
    def __init__(self, available: int, requested: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Insufficient inventory. Available: {available}, Requested: {requested}",
            details,
            "INSUFFICIENT_INVENTORY"
        )


# HTTP Exception converters
def convert_to_http_exception(exc: FastUsersException) -> HTTPException:
    """Convert a FastUsersException to an HTTPException."""
    
    status_code_mapping = {
        ResourceNotFoundError: status.HTTP_404_NOT_FOUND,
        ProductNotFoundError: status.HTTP_404_NOT_FOUND,
        DuplicateResourceError: status.HTTP_409_CONFLICT,
        ProductSKUExistsError: status.HTTP_409_CONFLICT,
        ProductSlugExistsError: status.HTTP_409_CONFLICT,
        ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        InvalidPriceError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        BusinessLogicError: status.HTTP_400_BAD_REQUEST,
        InsufficientInventoryError: status.HTTP_400_BAD_REQUEST,
        InsufficientPermissionsError: status.HTTP_403_FORBIDDEN,
        DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    status_code = status_code_mapping.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return HTTPException(
        status_code=status_code,
        detail={
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details
        }
    )
