#!/bin/bash

# Fast Users API Startup Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Fast Users API...${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run: python -m venv .venv${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}📦 Activating virtual environment...${NC}"
source .venv/bin/activate

# Check if required packages are installed
if ! pip list | grep -q fastapi; then
    echo -e "${RED}❌ FastAPI not installed. Please run: pip install -r requirements.txt${NC}"
    exit 1
fi

# Set environment
export ENVIRONMENT=${ENVIRONMENT:-development}
echo -e "${YELLOW}🌍 Environment: $ENVIRONMENT${NC}"

# Check if PostgreSQL is running (for production)
if [ "$ENVIRONMENT" = "production" ]; then
    if ! docker ps | grep -q fastusers_postgres; then
        echo -e "${YELLOW}🐘 Starting PostgreSQL...${NC}"
        docker compose up -d postgres
        sleep 5
    fi
fi

# Start the application
echo -e "${GREEN}🏃 Starting FastAPI server...${NC}"
echo -e "${YELLOW}📖 API Documentation will be available at: http://127.0.0.1:8000/docs${NC}"
echo -e "${YELLOW}🔍 API ReDoc will be available at: http://127.0.0.1:8000/redoc${NC}"

# Run the server
python -m uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
