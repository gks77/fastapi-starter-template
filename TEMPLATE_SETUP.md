# 🎯 FastAPI Starter Template - Quick Setup Guide

This guide will help you get started with the FastAPI Starter Template in under 5 minutes.

## 🚀 **One-Command Setup**

```bash
# Clone and set up the template
git clone https://github.com/yourusername/fastapi-starter-template.git my-new-project
cd my-new-project
chmod +x setup.sh && ./setup.sh
```

## 📋 **Manual Setup**

### **Step 1: Clone and Rename**
```bash
# Clone the template
git clone https://github.com/yourusername/fastapi-starter-template.git my-new-project
cd my-new-project

# Remove git history (start fresh)
rm -rf .git
git init
```

### **Step 2: Customize Configuration**
```bash
# Copy environment template
cp .env.example .env

# Update project name in .env
sed -i 's/FastAPI Starter Template/My New Project/g' .env

# Update database names
sed -i 's/starter_/mynewproject_/g' .env
```

### **Step 3: Install Dependencies**
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **Step 4: Set Up Database**
```bash
# Option A: PostgreSQL (recommended)
docker-compose up -d postgres
python init_db.py

# Option B: SQLite (quick start)
ENVIRONMENT=development python init_db.py

# Option C: MongoDB (NoSQL)
# 1. Uncomment MongoDB service in docker-compose.yml
# 2. Set database_type = "mongodb" in app/core/config.py
# 3. Install MongoDB dependencies:
pip install motor pymongo beanie
# 4. Use MongoDB connection and models as shown in app/db/mongodb.py
# 5. You can use both SQL and NoSQL by switching database_type or using both service layers
```
#
# ---
#
# **Database Selection**
#
# You can choose which database to use by setting `database_type` in `app/core/config.py`:
#
# ```python
# database_type: str = "postgresql"  # or "sqlite" or "mongodb"
# ```
#
# - To use PostgreSQL, keep `database_type = "postgresql"` and use the default setup.
# - To use SQLite, set `database_type = "sqlite"`.
# - To use MongoDB, set `database_type = "mongodb"` and follow the MongoDB setup instructions above.
# - You can comment/uncomment the database services in `docker-compose.yml` as needed.
# - You can implement both SQL and NoSQL models/services and use them together if desired.
#
# See `app/db/mongodb.py` for MongoDB connection example.
#

### **Step 5: Start Development**
```bash
# Run the application
uvicorn app.main:app --reload

# Run tests
./run_tests.py

# Access API docs
open http://localhost:8000/docs
```

## 🔄 **Customization Checklist**

### **Essential Changes**
- [ ] Update `PROJECT_NAME` in `app/core/config.py`
- [ ] Change database names in `.env` and `docker-compose.yml`
- [ ] Update `README.md` with your project description
- [ ] Customize `FIRST_SUPERUSER_*` settings in `.env`
- [ ] Update container names in `docker-compose.yml`

### **Optional Customizations**
- [ ] Add your own models in `app/models/`
- [ ] Create custom API endpoints in `app/api/v1/endpoints/`
- [ ] Add business logic in `app/services/`
- [ ] Customize middleware in `app/middleware/`
- [ ] Update logging configuration in `app/core/advanced_logging.py`

## 🎨 **Renaming the Project**

### **Update Project References**
```bash
# Update configuration
sed -i 's/FastAPI Starter Template/Your Project Name/g' app/core/config.py
sed -i 's/starter_/yourproject_/g' app/core/config.py
sed -i 's/starter_/yourproject_/g' .env.example
sed -i 's/starter_/yourproject_/g' docker-compose.yml

# Update documentation
sed -i 's/FastAPI Starter Template/Your Project Name/g' README.md
```

### **Database Naming**
```bash
# Update all database references
find . -name "*.py" -exec sed -i 's/starter_db/yourproject_db/g' {} \;
find . -name "*.yml" -exec sed -i 's/starter_/yourproject_/g' {} \;
```

## 🗂️ **Adding Your First Feature**

### **Example: Adding a "Post" Model**

1. **Create the Model** (`app/models/post.py`):
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base
from datetime import datetime

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    author = relationship("User", back_populates="posts")
```

2. **Create Schemas** (`app/schemas/post.py`):
```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    title: Optional[str] = None
    content: Optional[str] = None

class PostResponse(PostBase):
    id: int
    author_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

3. **Create CRUD Operations** (`app/crud/post.py`):
```python
from sqlalchemy.orm import Session
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate
from typing import Optional

def create_post(db: Session, post: PostCreate, author_id: int) -> Post:
    db_post = Post(**post.dict(), author_id=author_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Post).offset(skip).limit(limit).all()
```

4. **Create API Endpoints** (`app/api/v1/endpoints/posts.py`):
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps.database import get_db
from app.api.deps.auth import get_current_user
from app.crud import post as post_crud
from app.schemas.post import PostCreate, PostResponse
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=PostResponse)
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return post_crud.create_post(db, post, current_user.id)

@router.get("/", response_model=list[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    return post_crud.get_posts(db)
```

5. **Add to API Router** (`app/api/v1/api.py`):
```python
from app.api.v1.endpoints import posts

api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
```

6. **Update Models Init** (`app/models/__init__.py`):
```python
from app.models.post import Post
__all__ = ["User", "UserType", "Address", "Profile", "Session", "Post"]
```

## 🔒 **Security Considerations**

### **Before Going to Production**
- [ ] Change `SECRET_KEY` in production
- [ ] Update `FIRST_SUPERUSER_PASSWORD`
- [ ] Configure proper CORS origins
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure rate limiting
- [ ] Set up monitoring and logging
- [ ] Review and update security headers

### **Environment Variables**
```bash
# Production environment
ENVIRONMENT=production
SECRET_KEY=your-super-secret-production-key
POSTGRES_PASSWORD=your-very-secure-password
FIRST_SUPERUSER_PASSWORD=your-admin-password
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
```

## 📚 **Next Steps**

1. **Explore the Documentation**: Check the `docs/` folder for detailed guides
2. **Run the Tests**: `./run_tests.py` to ensure everything works
3. **Add Your Business Logic**: Start building your specific features
4. **Deploy**: Follow the deployment guide in the documentation
5. **Contribute**: Help improve the template for the community

## 💡 **Tips for Success**

- Start with the existing user management system as a reference
- Use the provided CRUD patterns for consistency
- Follow the existing project structure
- Write tests for your new features
- Use the provided development utilities
- Read the comprehensive documentation in `docs/`

## 🆘 **Need Help?**

- Run `./debug_test.py` to check your setup
- Check the `docs/` folder for detailed guides
- Look at existing code patterns in the template
- Open an issue on GitHub if you find bugs

Happy coding with your new FastAPI project! 🚀
