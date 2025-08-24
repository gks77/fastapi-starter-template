"""
Pytest configuration and shared fixtures for the Fast Users API tests.
"""

import pytest
import tempfile
import os
from typing import Generator, Dict, Any
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.main import app
from app.db.base import Base
from app.api.deps import get_db
from app.crud.user import user as user_crud
from app.schemas.user import UserCreate
from app.core.config import settings

# Override environment for testing
os.environ["ENVIRONMENT"] = "testing"

# Use testing database URL
TEST_DATABASE_URL = settings.get_database_url()


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Clean up
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_users.db"):
        os.remove("./test_users.db")


@pytest.fixture(scope="function")
def test_db(test_engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Standard test user data."""
    return {
        "username": f"testuser_{uuid4().hex[:8]}",
        "email": f"test_{uuid4().hex[:8]}@example.com",
        "password": "testpassword123"
    }


@pytest.fixture
def superuser_data() -> Dict[str, Any]:
    """Standard superuser data."""
    return {
        "username": f"admin_{uuid4().hex[:8]}",
        "email": f"admin_{uuid4().hex[:8]}@example.com",
        "password": "adminpassword123",
        "is_superuser": True
    }


@pytest.fixture
def test_user(test_db: Session, test_user_data: Dict[str, Any]):
    """Create a test user in the database."""
    user_create = UserCreate(**test_user_data)
    user = user_crud.create(test_db, obj_in=user_create)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def superuser(test_db: Session, superuser_data: Dict[str, Any]):
    """Create a superuser in the database."""
    user_create = UserCreate(**superuser_data)
    user = user_crud.create(test_db, obj_in=user_create)
    # Manually set superuser status since it's not in UserCreate
    user.is_superuser = True
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def user_token(client: TestClient, test_user_data: Dict[str, Any]) -> str:
    """Create a user and return their authentication token."""
    # Create user
    response = client.post("/api/v1/users/", json=test_user_data)
    assert response.status_code == 201
    
    # Login and get token
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def superuser_token(client: TestClient, test_db: Session) -> str:
    """Create a superuser and return their authentication token."""
    # Create superuser data
    superuser_data = {
        "username": "test_admin",
        "email": "admin@test.com",
        "password": "adminpassword123"
    }
    
    # Create the user first
    user_create = UserCreate(**superuser_data)
    user = user_crud.create(test_db, obj_in=user_create)
    
    # Make them a superuser
    user.is_superuser = True
    test_db.commit()
    test_db.refresh(user)
    
    # Login and get token
    login_data = {
        "username": superuser_data["username"],
        "password": superuser_data["password"]
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(user_token: str) -> Dict[str, str]:
    """Return authorization headers for a regular user."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def superuser_headers(superuser_token: str) -> Dict[str, str]:
    """Return authorization headers for a superuser."""
    return {"Authorization": f"Bearer {superuser_token}"}


@pytest.fixture
def sample_profile_data() -> Dict[str, Any]:
    """Sample profile data for testing."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "bio": "Software developer with 5 years of experience",
        "location": "San Francisco, CA",
        "company": "Tech Corp",
        "job_title": "Senior Developer",
        "website": "https://johndoe.dev",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "twitter_url": "https://twitter.com/johndoe",
        "github_url": "https://github.com/johndoe",
        "is_profile_public": "public",
        "show_email": "true",
        "show_phone": "false"
    }


@pytest.fixture
def sample_address_data() -> Dict[str, Any]:
    """Sample address data for testing."""
    return {
        "label": "Home",
        "first_name": "John",
        "last_name": "Doe",
        "company": "Tech Corp",
        "address_line_1": "123 Main St",
        "address_line_2": "Apt 4B",
        "city": "San Francisco",
        "state": "CA",
        "country": "USA",
        "postal_code": "94102",
        "phone": "+1-555-012-3456",
        "email": "john.doe@example.com",
        "address_type": "both",
        "is_default": True,
        "delivery_instructions": "Leave at door"
    }
