# 🗄️ Database Guide

This template supports multiple databases. Here’s how to use each:

## PostgreSQL (Recommended for Production)
- Default setup in `docker-compose.yml`.
- Configuration in `.env` and `app/core/config.py`.
- Use Alembic for migrations.

## SQLite (For Quick Testing)
- No external service required.
- Set `ENVIRONMENT=development` in `.env` or your shell.
- Fast for local development and tests.

## MongoDB (NoSQL Option)
- Uncomment MongoDB service in `docker-compose.yml`.
- Set `database_type = "mongodb"` in `app/core/config.py`.
- Install dependencies:
  ```bash
  pip install motor pymongo beanie
  ```
- See `app/db/mongodb.py` for connection example.
- Use Beanie or Motor for async ODM/models.

## Switching Databases
- Change `database_type` in `app/core/config.py` to `postgresql`, `sqlite`, or `mongodb`.
- Update `.env` with the correct database credentials.
- Comment/uncomment services in `docker-compose.yml` as needed.

## Migrations
- **PostgreSQL/SQLite**: Use Alembic for schema migrations.
- **MongoDB**: Use Beanie migrations or manage collections manually.

## Example Environment Variables
```env
# PostgreSQL
POSTGRES_SERVER=localhost
POSTGRES_USER=starter_user
POSTGRES_PASSWORD=password
POSTGRES_DB=starter_db
POSTGRES_PORT=5433

# SQLite
SQLITE_DB_PATH=./app.db
TEST_SQLITE_DB_PATH=./test_app.db

# MongoDB
MONGODB_URL=mongodb://admin:password@localhost:27017
MONGODB_DATABASE=starter_db
MONGODB_TEST_DATABASE=test_starter_db
```
