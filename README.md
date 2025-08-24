# 🚀 FastAPI Starter Template

A **production-ready FastAPI starter template** with comprehensive features for building modern web APIs quickly and efficiently.

![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-00C7B7.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## ✨ **Template Features**

### 🔐 **Authentication & Authorization**
- JWT token-based authentication
- OAuth2 with Password (and hashing), Bearer with JWT tokens
- User registration and login
- Role-based access control (ADMIN, USER, EMPLOYEE, HR, SUPER_ADMIN)
- Password hashing and validation

### 👥 **User Management**
- Complete user CRUD operations
- User profiles with customizable fields
- User type/role management
- Address management
- Session tracking and management


### 🗄️ **Database**
- **PostgreSQL** for production (recommended)
- **SQLite** for development and testing
- **MongoDB** (NoSQL) support (optional)
- SQLAlchemy ORM with async support
- Database migrations with Alembic
- Automatic database initialization

#### 🥭 **MongoDB Support**
- Easily switch to MongoDB by setting `database_type = "mongodb"` in `app/core/config.py`
- Example connection and usage in `app/db/mongodb.py`
- Add MongoDB service to `docker-compose.yml` (see TEMPLATE_SETUP.md)
- Use Beanie ODM or Motor for async MongoDB models

### � **Logging & Monitoring**
- Structured JSON logging
- Request/Response logging middleware
- Advanced log analysis utilities
- Elasticsearch integration (optional)
- Health check endpoints

### �️ **Development Tools**
- Comprehensive test suite with pytest
- Code coverage reporting
- Development utility scripts
- Database initialization and management
- Dependency verification


###  **Quick Start**

1. **Clone the Repository**
	```bash
	git clone https://github.com/gks77/fastapi-starter-template.git
	cd fast-users
	```

2. **Set Up Environment**
	```bash
	python -m venv .venv
	source .venv/bin/activate  # On Windows: .venv\Scripts\activate
	pip install -r requirements.txt
	```

3. **Configure Environment**
	```bash
	cp .env.example .env
	# Edit .env with your settings
	nano .env
	```

4. **Choose Database**
	- PostgreSQL (default):
		```bash
		docker-compose up -d postgres
		python init_db.py
		```
	- SQLite (quick start):
		```bash
		ENVIRONMENT=development python init_db.py
		```
	- MongoDB (NoSQL):
		```bash
		# Uncomment MongoDB service in docker-compose.yml
		# Set database_type = "mongodb" in app/core/config.py
		pip install motor pymongo beanie
		# See app/db/mongodb.py for usage
		```

5. **Run the Application**
	```bash
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
	# Or use the provided script
	./run.sh
	```

6. **Access the API**
	- **API Documentation**: http://localhost:8000/docs
	- **ReDoc Documentation**: http://localhost:8000/redoc
	- **Health Check**: http://localhost:8000/health

### **5. Run the Application**
```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the run script
./run.sh
```

### **6. Access the API**
- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📁 **Template Structure**

```
fastapi-starter-template/
├── app/                          # Main application package
│   ├── api/                      # API routes
│   │   ├── deps/                 # Dependencies
│   │   └── v1/                   # API version 1
│   │       └── endpoints/        # API endpoints
│   ├── core/                     # Core functionality
│   │   ├── config.py            # Configuration settings
│   │   ├── security.py          # Security utilities
│   │   └── advanced_logging.py  # Logging configuration
│   ├── crud/                     # CRUD operations
│   ├── db/                       # Database configuration
│   ├── middleware/               # Custom middleware
│   ├── models/                   # SQLAlchemy models
│   ├── schemas/                  # Pydantic schemas
│   ├── services/                 # Business logic
│   └── utils/                    # Utility functions
├── tests/                        # Test suite
├── docs/                         # Documentation
├── scripts/                      # Database and utility scripts
├── docker-compose.yml            # Docker services
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

### 📚 **What's Included**

#### **Core Models**
- **User**: Authentication and profile management
- **UserType**: Role-based access control
- **Address**: User address information
- **Profile**: Extended user profile data
- **Session**: User session tracking
- **MongoDB Models**: Example Beanie/Motor models for NoSQL

#### **API Endpoints**
- **Authentication**: Register, login, logout, refresh token
- **User Management**: CRUD operations with role-based access
- **User Types**: Role management for admins
- **Profiles**: User profile management
- **Addresses**: Address management
- **Logging**: Log analysis and monitoring

#### **Utilities**
- Database initialization and management
- Test runner with coverage
- Debug and dependency verification
- Log analysis tools
---


## 🔧 **Customization Guide**

### **Adding New Models (SQL & NoSQL)**

**SQL (PostgreSQL/SQLite):**
1. Create model in `app/models/your_model.py`
2. Create schemas in `app/schemas/your_model.py`
3. Create CRUD operations in `app/crud/your_model.py`
4. Create API endpoints in `app/api/v1/endpoints/your_model.py`
5. Add to API router in `app/api/v1/api.py`
6. Update `app/models/__init__.py`

**NoSQL (MongoDB):**
1. Create Beanie/Motor model in `app/models/mongo_your_model.py`
2. Create service in `app/services/mongo_your_service.py`
3. Create API endpoints in `app/api/v1/endpoints/mongo_your_model.py`
4. Add to API router in `app/api/v1/api.py`

### **Adding Business Logic**
1. Create service in `app/services/your_service.py`
2. Implement business logic
3. Use in your API endpoints

### **Adding Middleware**
1. Create middleware in `app/middleware/your_middleware.py`
2. Add to `app/main.py`

---

## 🧪 **Testing**

### **Run Tests**
```bash
# Run all tests
./run_tests.py

# Run with coverage
./run_tests.py --html-report

# Run specific test markers
./run_tests.py -m auth

# Run tests in parallel
./run_tests.py --parallel
```

### **Test Categories**
- `auth`: Authentication tests
- `users`: User management tests
- `integration`: Integration tests
- `unit`: Unit tests

---

## 🛠️ **Development Utilities**

### **Database Management**
```bash
# Initialize database
./init_db.py

# Reset database
python scripts/db_manager.py --reset

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### **Debugging**
```bash
# Debug application setup
./debug_test.py

# Verify dependencies
./verify_dependencies.py
```

### **Code Quality**
```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/
```

---

## 🐳 **Docker Development**

### **Start Services**
```bash
# Start all services
docker-compose up -d

# Start only database
docker-compose up -d postgres

# View logs
docker-compose logs -f
```

### **Available Services**
- **PostgreSQL**: `localhost:5433`
- **pgAdmin**: `localhost:5050`
- **Redis**: `localhost:6379`
- **Elasticsearch**: `localhost:9200`

---

## 📚 **API Documentation**

### **Authentication Endpoints**
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `POST /api/v1/auth/logout` - User logout

### **User Management**
- `GET /api/v1/users/` - List users (admin only)
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user
- `DELETE /api/v1/users/{user_id}` - Delete user (admin only)

### **User Types/Roles**
- `GET /api/v1/user-types/` - List user types
- `POST /api/v1/user-types/` - Create user type (admin only)
- `PUT /api/v1/user-types/{id}` - Update user type (admin only)

---

## � **Deployment**

### **Production Deployment**

1. **Set Environment Variables**
```bash
ENVIRONMENT=production
SECRET_KEY=your-production-secret
POSTGRES_SERVER=your-db-server
# ... other production settings
```

2. **Database Setup**
```bash
# Run migrations
alembic upgrade head

# Create superuser
python init_db.py
```

3. **Run with Gunicorn**
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### **Docker Production**
```bash
# Build production image
docker build -t your-api .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🤝 **Contributing**

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- [FastAPI](https://fastapi.tiangolo.com/) for the amazing web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) for the powerful ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
- The Python community for excellent tools and libraries

---

## 📞 **Support**

If you have any questions or need help with this template:

1. Check the [documentation](./docs/)
2. Run the debug utility: `./debug_test.py`
3. Open an issue on GitHub
4. Refer to the comprehensive setup guides in the `docs/` folder

---

**Happy coding! 🎉**

### **Testing Framework**
```python
pytest==7.4.3                # Testing framework
pytest-cov==6.2.1            # Test coverage reporting
httpx==0.25.2                # HTTP client for testing FastAPI
```

### **File Processing**
```python
pillow==11.3.0               # Image processing (Updated for security)
```

## 🔧 Library Purposes Explained

### **FastAPI**
- **What**: Modern, fast web framework for building APIs with Python
- **Why**: Automatic API documentation, async support, type hints integration
- **Used for**: Creating REST endpoints, request/response handling, dependency injection

### **SQLAlchemy**
- **What**: Python SQL toolkit and Object-Relational Mapping (ORM) library
- **Why**: Database abstraction, query building, relationship management
- **Used for**: Database models, queries, transactions, migrations

### **Pydantic**
- **What**: Data validation library using Python type annotations
- **Why**: Automatic validation, serialization, and documentation
- **Used for**: Request/response schemas, configuration management, data validation

### **Python-JOSE**
- **What**: JavaScript Object Signing and Encryption implementation for Python
- **Why**: JWT token creation, validation, and parsing
- **Used for**: User authentication, session management, API security

### **Passlib + Bcrypt**
- **What**: Password hashing library with bcrypt algorithm
- **Why**: Secure password storage, salt generation, hash verification
- **Used for**: Password encryption, user authentication

### **Uvicorn**
- **What**: Lightning-fast ASGI server
- **Why**: High-performance async server for FastAPI applications
- **Used for**: Running the FastAPI application in development and production

### **Pytest + HTTPX**
- **What**: Testing framework and HTTP client
- **Why**: Comprehensive testing capabilities, async HTTP client
- **Used for**: Unit tests, integration tests, API endpoint testing

## 🚀 Quick Start

### 1. Installation
```bash
# Clone the repository
git clone <repository-url>
cd fast-users

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install production dependencies
pip install -r requirements.txt

# For development (includes testing and security tools)
pip install -r requirements-dev.txt
```

### 2. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# SECRET_KEY=your-secret-key-here
# DATABASE_URL=sqlite:///./users.db
```

### 3. Database Setup
```bash
# Initialize database (creates tables and superuser)
python -c "from app.db.init_db import init_db; init_db()"
```

### 4. Run Application
```bash
# Development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or use the provided script
chmod +x run.sh
./run.sh
```

### 5. Access API
- **API Base**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Default Credentials

The system creates a default superuser for initial access:
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@example.com`

⚠️ **Security Note**: Change these credentials in production!

## 📋 API Endpoints

### Authentication
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| POST | `/api/v1/auth/login` | Login and get JWT token | Public |

### User Management
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| POST | `/api/v1/users/` | Register new user | Public |
| GET | `/api/v1/users/me` | Get current user info | Authenticated |
| GET | `/api/v1/users/` | List all users | Superuser only |
| GET | `/api/v1/users/{id}` | Get user by ID | Owner or superuser |
| PUT | `/api/v1/users/{id}` | Update user | Owner or superuser |
| DELETE | `/api/v1/users/{id}` | Delete user | Superuser only |

### System
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| GET | `/` | API welcome message | Public |
| GET | `/health` | Health check | Public |

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/api/test_users.py

# Run with verbose output
pytest -v

# Generate coverage report
pytest --cov=app --cov-report=html
```

## 🔒 Security Tools

```bash
# Run security analysis with bandit
bandit -r app/ -f json -o bandit-report.json

# Check for known security vulnerabilities
safety check

# Run both security checks
python -m bandit -r app/ && safety check
```

## 🔧 Development

### Adding New Features

1. **Database Model**: Add to `app/models/`
2. **Pydantic Schema**: Define in `app/schemas/`
3. **CRUD Operations**: Implement in `app/crud/`
4. **Business Logic**: Add to `app/services/`
5. **API Endpoints**: Create in `app/api/v1/endpoints/`
6. **Tests**: Write in `tests/`

### Database Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```


## 🚀 Production Deployment

### Environment Variables
```env
SECRET_KEY=your-super-secret-production-key
DATABASE_URL=postgresql://user:password@localhost/dbname
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
# For MongoDB:
MONGODB_URL=mongodb://admin:password@localhost:27017
MONGODB_DATABASE=starter_db
```

### Security Checklist
- [ ] Change default superuser credentials
- [ ] Use strong SECRET_KEY
- [ ] Configure CORS origins properly
- [ ] Use HTTPS in production
- [ ] Set up proper logging
- [ ] Configure rate limiting
- [ ] Use production database (PostgreSQL)
- [ ] Set up monitoring and health checks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Review the API documentation at `/docs`
- Check the test files for usage examples

---

Built with ❤️ using FastAPI and modern Python best practices.
