# 🚀 Getting Started with FastAPI Starter Template

This guide will help you quickly set up and run your FastAPI project.

## 1. Clone the Repository
```bash
git clone https://github.com/gks77/fast-users.git
cd fast-users
```

## 2. Set Up Your Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Configure Environment Variables
```bash
cp .env.example .env
nano .env  # Edit your settings
```

## 4. Choose Your Database
- **PostgreSQL** (default):
  ```bash
  docker-compose up -d postgres
  python init_db.py
  ```
- **SQLite** (quick start):
  ```bash
  ENVIRONMENT=development python init_db.py
  ```
- **MongoDB** (NoSQL):
  ```bash
  # Uncomment MongoDB service in docker-compose.yml
  # Set database_type = "mongodb" in app/core/config.py
  pip install motor pymongo beanie
  # See app/db/mongodb.py for usage
  ```

## 5. Run the Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 6. Access the API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 7. Next Steps
- Explore the codebase and add your own models/endpoints
- See other guides in the `docs/` folder for more help
- Check the README for customization and deployment tips

Happy coding! 🎉
