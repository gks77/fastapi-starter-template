import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CRUDCategory:
    """CRUD operations for Category model."""
    
    def get(self, db: Session, id: uuid.UUID) -> Optional[Category]:
        """Get category by UUID."""
        return db.query(Category).filter(Category.id == id, Category.is_deleted == False).first()
    
    def get_by_name(self, db: Session, *, name: str, department_id: uuid.UUID) -> Optional[Category]:
        """Get category by name within a department."""
        return db.query(Category).filter(
            Category.name == name,
            Category.department_id == department_id,
            Category.is_deleted == False
        ).first()
    
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Category]:
        """Get category by slug."""
        return db.query(Category).filter(
            Category.slug == slug, Category.is_deleted == False
        ).first()
    
    def get_by_department(
        self, db: Session, *, department_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Category]:
        """Get categories by department."""
        return (
            db.query(Category)
            .filter(Category.department_id == department_id, Category.is_deleted == False)
            .order_by(Category.display_order, Category.name)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_active_by_department(
        self, db: Session, *, department_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Category]:
        """Get active categories by department."""
        return (
            db.query(Category)
            .filter(
                Category.department_id == department_id,
                Category.is_active == True,
                Category.is_deleted == False
            )
            .order_by(Category.display_order, Category.name)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Category]:
        """Get multiple categories with pagination."""
        return (
            db.query(Category)
            .filter(Category.is_deleted == False)
            .order_by(Category.display_order, Category.name)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create(self, db: Session, *, obj_in: CategoryCreate) -> Category:
        """Create new category."""
        # Generate slug from name if not provided
        slug = obj_in.slug or obj_in.name.lower().replace(" ", "-").replace("_", "-")
        
        db_obj = Category(
            department_id=obj_in.department_id,
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
        self, db: Session, *, db_obj: Category, obj_in: CategoryUpdate
    ) -> Category:
        """Update category."""
        obj_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: uuid.UUID) -> Optional[Category]:
        """Soft delete category."""
        obj = self.get(db=db, id=id)
        if obj:
            obj.is_deleted = True
            db.commit()
        return obj


category = CRUDCategory()
