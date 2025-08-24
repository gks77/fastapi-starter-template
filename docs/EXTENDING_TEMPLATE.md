# 🛠️ Extending the FastAPI Starter Template

## Adding New Models (SQL)
1. Create model in `app/models/your_model.py`
2. Create schemas in `app/schemas/your_model.py`
3. Create CRUD operations in `app/crud/your_model.py`
4. Create API endpoints in `app/api/v1/endpoints/your_model.py`
5. Add to API router in `app/api/v1/api.py`
6. Update `app/models/__init__.py`

## Adding New Models (MongoDB)
1. Create Beanie/Motor model in `app/models/mongo_your_model.py`
2. Create service in `app/services/mongo_your_service.py`
3. Create API endpoints in `app/api/v1/endpoints/mongo_your_model.py`
4. Add to API router in `app/api/v1/api.py`

## Adding Business Logic
1. Create service in `app/services/your_service.py`
2. Implement business logic
3. Use in your API endpoints

## Adding Middleware
1. Create middleware in `app/middleware/your_middleware.py`
2. Add to `app/main.py`

## Adding Tests
1. Write tests in `tests/`
2. Use `pytest` for running tests
3. Check coverage with `pytest --cov=app`

## Customizing Authentication
- Update user model and schemas for custom fields
- Adjust authentication endpoints as needed
- Add new roles/types in `UserType` enum

## API Documentation
- All endpoints are auto-documented via Swagger and ReDoc
- Add docstrings to your endpoints for better docs

## Deployment
- See README and `docs/GETTING_STARTED.md` for deployment steps
- Use Docker for production-ready setup

---

For more advanced guides, see other docs in this folder or open an issue on GitHub!
