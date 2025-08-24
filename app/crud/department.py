import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate


class CRUDDepartment:
    """CRUD operations for Department model."""
    
    def get(self, db: Session, id: uuid.UUID) -> Optional[Department]:
        """Get department by UUID."""
        return db.query(Department).filter(Department.id == id, Department.is_deleted == False).first()
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Department]:
        """Get department by name."""
        return db.query(Department).filter(
            Department.name == name, Department.is_deleted == False
        ).first()
    
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Department]:
        """Get department by slug."""
        return db.query(Department).filter(
            Department.slug == slug, Department.is_deleted == False
        ).first()
    
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Department]:
        """Get multiple departments with pagination."""
        return (
            db.query(Department)
            .filter(Department.is_deleted == False)
            .order_by(Department.display_order, Department.name)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_active(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Department]:
        """Get active departments."""
        return (
            db.query(Department)
            .filter(Department.is_active == True, Department.is_deleted == False)
            .order_by(Department.display_order, Department.name)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create(self, db: Session, *, obj_in: DepartmentCreate) -> Department:
        """Create new department."""
        # Generate slug from name if not provided
        slug = obj_in.slug or obj_in.name.lower().replace(" ", "-").replace("_", "-")
        
        db_obj = Department(
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
        self, db: Session, *, db_obj: Department, obj_in: DepartmentUpdate
    ) -> Department:
        """Update department."""
        obj_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: uuid.UUID) -> Optional[Department]:
        """Soft delete department."""
        obj = self.get(db=db, id=id)
        if obj:
            obj.is_deleted = True
            db.commit()
        return obj


department = CRUDDepartment()
