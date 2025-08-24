from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import secrets


class Settings(BaseSettings):
    """Application settings."""
    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True,
        extra="ignore"  # Allow extra fields without validation errors
    )
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Starter Template"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A production-ready FastAPI starter template with authentication, user management, and comprehensive tooling"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Environment
    ENVIRONMENT: str = "development"  # development, testing, production
    
    # Database Configuration
    # PostgreSQL settings for production
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "starter_user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "starter_db"
    POSTGRES_PORT: int = 5433
    

    # SQLite for development/testing
    SQLITE_DB_PATH: str = "./app.db"
    TEST_SQLITE_DB_PATH: str = "./test_app.db"

    # MongoDB configuration
    mongodb_url: str = "mongodb://admin:password@localhost:27017"
    mongodb_database: str = "starter_db"
    mongodb_test_database: str = "test_starter_db"

    # Database type selection
    # Choose one: 'postgresql', 'sqlite', 'mongodb'
    database_type: str = "postgresql"  # Change to 'mongodb' or 'sqlite' as needed

        # MongoDB configuration
        MONGODB_URL: str = "mongodb://admin:password@localhost:27017"
        MONGODB_DATABASE: str = "starter_db"
        MONGODB_TEST_DATABASE: str = "test_starter_db"

        # Database type selection
        # Choose one: 'postgresql', 'sqlite', 'mongodb'
        DATABASE_TYPE: str = "postgresql"  # Change to 'mongodb' or 'sqlite' as needed
    
    def get_database_url(self) -> str:
        """Get database URL based on database_type and environment."""
        if self.database_type == "mongodb":
            if self.ENVIRONMENT == "testing":
                return f"{self.mongodb_url}/{self.mongodb_test_database}"
            return f"{self.mongodb_url}/{self.mongodb_database}"
        elif self.database_type == "sqlite":
            if self.ENVIRONMENT == "testing":
                return f"sqlite:///{self.TEST_SQLITE_DB_PATH}"
            return f"sqlite:///{self.SQLITE_DB_PATH}"
        else:  # Default to PostgreSQL
            if self.ENVIRONMENT == "testing":
                return f"sqlite:///{self.TEST_SQLITE_DB_PATH}"
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def get_mongodb_url(self) -> str:
        """Get MongoDB URL based on environment."""
        if self.ENVIRONMENT == "testing":
            return f"{self.mongodb_url}/{self.mongodb_test_database}"
        return f"{self.mongodb_url}/{self.mongodb_database}"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]  # Configure for production
    
    # Superuser
    FIRST_SUPERUSER_USERNAME: str = "admin"
    FIRST_SUPERUSER_EMAIL: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"


settings = Settings()
