import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.subcategory import Subcategory
from app.schemas.subcategory import SubcategoryCreate, SubcategoryUpdate


class CRUDSubcategory:
    """CRUD operations for Subcategory model."""
    
    def get(self, db: Session, id: uuid.UUID) -> Optional[Subcategory]:
        """Get subcategory by UUID."""
        return db.query(Subcategory).filter(Subcategory.id == id, Subcategory.is_deleted == False).first()
    
    def get_by_name(self, db: Session, *, name: str, category_id: uuid.UUID) -> Optional[Subcategory]:
        """Get subcategory by name within a category."""
        return db.query(Subcategory).filter(
            Subcategory.name == name,
            Subcategory.category_id == category_id,
            Subcategory.is_deleted == False
        ).first()
    
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Subcategory]:
        """Get subcategory by slug."""
        return db.query(Subcategory).filter(
            Subcategory.slug == slug, Subcategory.is_deleted == False
        ).first()
    
    def get_by_category(
        self, db: Session, *, category_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Subcategory]:
        """Get subcategories by category."""
        return (
            db.query(Subcategory)
            .filter(Subcategory.category_id == category_id, Subcategory.is_deleted == False)
            .order_by(Subcategory.display_order, Subcategory.name)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_active_by_category(
        self, db: Session, *, category_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Subcategory]:
        """Get active subcategories by category."""
        return (
            db.query(Subcategory)
            .filter(
                Subcategory.category_id == category_id,
                Subcategory.is_active == True,
                Subcategory.is_deleted == False
            )
            .order_by(Subcategory.display_order, Subcategory.name)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Subcategory]:
        """Get multiple subcategories with pagination."""
        return (
            db.query(Subcategory)
            .filter(Subcategory.is_deleted == False)
            .order_by(Subcategory.display_order, Subcategory.name)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create(self, db: Session, *, obj_in: SubcategoryCreate) -> Subcategory:
        """Create new subcategory."""
        # Generate slug from name if not provided
        slug = obj_in.slug or obj_in.name.lower().replace(" ", "-").replace("_", "-")
        
        db_obj = Subcategory(
            category_id=obj_in.category_id,
            name=obj_in.name,
            description=obj_in.description,
            slug=slug,
            display_order=obj_in.display_order,
            is_active=obj_in.is_active,
            image_url=obj_in.image_url
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: Subcategory, obj_in: SubcategoryUpdate
    ) -> Subcategory:
        """Update subcategory."""
        obj_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: uuid.UUID) -> Optional[Subcategory]:
        """Soft delete subcategory."""
        obj = self.get(db=db, id=id)
        if obj:
            obj.is_deleted = True
            db.commit()
        return obj


subcategory = CRUDSubcategory()
