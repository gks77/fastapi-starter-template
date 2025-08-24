-- Initialize FastAPI Starter Template database with extensions and initial setup

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create a schema for the application (optional)
-- CREATE SCHEMA IF NOT EXISTS starter_app;

-- Set default privileges
GRANT ALL PRIVILEGES ON DATABASE starter_db TO starter_user;

-- Add any additional initialization SQL here
-- For example, creating initial tables, indexes, or data

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'FastAPI Starter Template database initialized successfully!';
END $$;
