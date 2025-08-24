from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from decimal import Decimal

from app.crud.base import CRUDBase
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductSearchRequest


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    """CRUD operations for Product model."""
    
    def get_by_sku(self, db: Session, *, sku: str) -> Optional[Product]:
        """Get product by SKU."""
        return db.query(Product).filter(
            and_(Product.sku == sku.upper(), Product.is_deleted == False)
        ).first()
    
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Product]:
        """Get product by slug."""
        return db.query(Product).filter(
            and_(Product.slug == slug, Product.is_deleted == False)
        ).first()
    
    def get_by_barcode(self, db: Session, *, barcode: str) -> Optional[Product]:
        """Get product by barcode."""
        return db.query(Product).filter(
            and_(Product.barcode == barcode, Product.is_deleted == False)
        ).first()
    
    def get_active_products(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """Get all active products."""
        return db.query(Product).filter(
            and_(Product.is_active == True, Product.is_deleted == False)
        ).offset(skip).limit(limit).all()
    
    def get_featured_products(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Product]:
        """Get featured products."""
        return db.query(Product).filter(
            and_(
                Product.is_featured == True,
                Product.is_active == True,
                Product.is_deleted == False
            )
        ).order_by(Product.display_order, Product.name).offset(skip).limit(limit).all()
    
    def get_by_category(
        self, 
        db: Session, 
        *, 
        category_id: UUID, 
        active_only: bool = True,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """Get products by category."""
        query = db.query(Product).filter(
            and_(Product.category_id == category_id, Product.is_deleted == False)
        )
        
        if active_only:
            query = query.filter(Product.is_active == True)
        
        return query.order_by(Product.display_order, Product.name).offset(skip).limit(limit).all()
    
    def get_by_subcategory(
        self, 
        db: Session, 
        *, 
        subcategory_id: UUID, 
        active_only: bool = True,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """Get products by subcategory."""
        query = db.query(Product).filter(
            and_(Product.subcategory_id == subcategory_id, Product.is_deleted == False)
        )
        
        if active_only:
            query = query.filter(Product.is_active == True)
        
        return query.order_by(Product.display_order, Product.name).offset(skip).limit(limit).all()
    
    def get_by_brand(
        self, 
        db: Session, 
        *, 
        brand: str, 
        active_only: bool = True,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """Get products by brand."""
        query = db.query(Product).filter(
            and_(Product.brand == brand, Product.is_deleted == False)
        )
        
        if active_only:
            query = query.filter(Product.is_active == True)
        
        return query.order_by(Product.display_order, Product.name).offset(skip).limit(limit).all()
    
    def get_by_vendor(
        self, 
        db: Session, 
        *, 
        vendor: str, 
        active_only: bool = True,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """Get products by vendor."""
        query = db.query(Product).filter(
            and_(Product.vendor == vendor, Product.is_deleted == False)
        )
        
        if active_only:
            query = query.filter(Product.is_active == True)
        
        return query.order_by(Product.display_order, Product.name).offset(skip).limit(limit).all()
    
    def get_low_stock_products(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """Get products with low stock."""
        return db.query(Product).filter(
            and_(
                Product.track_inventory == True,
                Product.quantity <= Product.low_stock_threshold,
                Product.is_active == True,
                Product.is_deleted == False
            )
        ).order_by(Product.quantity).offset(skip).limit(limit).all()
    
    def get_out_of_stock_products(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """Get products that are out of stock."""
        return db.query(Product).filter(
            and_(
                Product.track_inventory == True,
                Product.quantity == 0,
                Product.allow_backorder == False,
                Product.is_active == True,
                Product.is_deleted == False
            )
        ).order_by(Product.name).offset(skip).limit(limit).all()
    
    def search_products(
        self, 
        db: Session, 
        *, 
        search_params: ProductSearchRequest,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """Search products with multiple filters."""
        query = db.query(Product).filter(Product.is_deleted == False)
        
        # Text search
        if search_params.query:
            search_term = f"%{search_params.query}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.short_description.ilike(search_term),
                    Product.sku.ilike(search_term),
                    Product.brand.ilike(search_term),
                    Product.tags.ilike(search_term)
                )
            )
        
        # Category filter
        if search_params.category_id:
            query = query.filter(Product.category_id == search_params.category_id)
        
        # Subcategory filter
        if search_params.subcategory_id:
            query = query.filter(Product.subcategory_id == search_params.subcategory_id)
        
        # Brand filter
        if search_params.brand:
            query = query.filter(Product.brand == search_params.brand)
        
        # Vendor filter
        if search_params.vendor:
            query = query.filter(Product.vendor == search_params.vendor)
        
        # Price range filter
        if search_params.min_price is not None:
            query = query.filter(Product.price >= search_params.min_price)
        
        if search_params.max_price is not None:
            query = query.filter(Product.price <= search_params.max_price)
        
        # Featured filter
        if search_params.is_featured is not None:
            query = query.filter(Product.is_featured == search_params.is_featured)
        
        # On sale filter
        if search_params.is_on_sale:
            query = query.filter(
                and_(
                    Product.compare_at_price.isnot(None),
                    Product.compare_at_price > Product.price
                )
            )
        
        # Stock filter
        if search_params.in_stock_only:
            query = query.filter(
                or_(
                    Product.track_inventory == False,
                    and_(
                        Product.track_inventory == True,
                        or_(
                            Product.quantity > 0,
                            Product.allow_backorder == True
                        )
                    )
                )
            )
        
        # Active products only
        query = query.filter(Product.is_active == True)
        
        # Sorting
        sort_field = getattr(Product, search_params.sort_by, Product.name)
        if search_params.sort_order == "desc":
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(asc(sort_field))
        
        return query.offset(skip).limit(limit).all()
    
    def update_inventory(
        self, 
        db: Session, 
        *, 
        product_id: UUID, 
        quantity_change: int
    ) -> Optional[Product]:
        """Update product inventory (add or subtract quantity)."""
        product = self.get(db, id=product_id)
        if not product:
            return None
        
        new_quantity = max(0, product.quantity + quantity_change)
        product.quantity = new_quantity
        db.commit()
        db.refresh(product)
        return product
    
    def set_inventory(
        self, 
        db: Session, 
        *, 
        product_id: UUID, 
        quantity: int
    ) -> Optional[Product]:
        """Set product inventory to specific quantity."""
        product = self.get(db, id=product_id)
        if not product:
            return None
        
        product.quantity = max(0, quantity)
        db.commit()
        db.refresh(product)
        return product
    
    def get_brands(self, db: Session) -> List[str]:
        """Get all unique brands."""
        result = db.query(Product.brand).filter(
            and_(
                Product.brand.isnot(None), 
                Product.is_active == True,
                Product.is_deleted == False
            )
        ).distinct().all()
        return [brand[0] for brand in result if brand[0]]
    
    def get_vendors(self, db: Session) -> List[str]:
        """Get all unique vendors."""
        result = db.query(Product.vendor).filter(
            and_(
                Product.vendor.isnot(None), 
                Product.is_active == True,
                Product.is_deleted == False
            )
        ).distinct().all()
        return [vendor[0] for vendor in result if vendor[0]]
    
    def get_price_range(self, db: Session) -> Dict[str, Optional[Decimal]]:
        """Get the price range (min and max) of active products."""
        result = db.query(
            db.func.min(Product.price).label('min_price'),
            db.func.max(Product.price).label('max_price')
        ).filter(
            and__(Product.is_active == True, Product.is_deleted == False)
        ).first()
        
        return {
            "min_price": result.min_price if result else None,
            "max_price": result.max_price if result else None
        }
    
    def create_with_slug(self, db: Session, *, obj_in: ProductCreate) -> Product:
        """Create product and auto-generate slug if not provided."""
        import re
        
        # Auto-generate slug if not provided
        if not obj_in.slug:
            # Create slug from name
            slug_base = re.sub(r'[^a-zA-Z0-9\s-]', '', obj_in.name.lower())
            slug_base = re.sub(r'\s+', '-', slug_base.strip())
            
            # Check for existing slug and append number if needed
            slug = slug_base
            counter = 1
            while self.get_by_slug(db, slug=slug):
                slug = f"{slug_base}-{counter}"
                counter += 1
            
            obj_in.slug = slug
        
        # Ensure SKU is uppercase
        obj_in.sku = obj_in.sku.upper()
        
        return self.create(db, obj_in=obj_in)


# Create instance
product = CRUDProduct(Product)
