#!/bin/bash

# PostgreSQL Database Setup Script for Fast Users API
# This script sets up a PostgreSQL database for production use

set -e

# Configuration
DB_NAME="fastusers"
DB_USER="fastusers"
DB_PASSWORD="your-secure-password"
POSTGRES_HOST="localhost"
POSTGRES_PORT="5433"

echo "🚀 Setting up PostgreSQL database for Fast Users API..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install PostgreSQL first:"
    echo "   macOS: brew install postgresql"
    echo "   Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    echo "   CentOS/RHEL: sudo yum install postgresql-server postgresql-contrib"
    exit 1
fi

# Check if PostgreSQL service is running
if ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT &> /dev/null; then
    echo "❌ PostgreSQL service is not running. Please start PostgreSQL service:"
    echo "   macOS: brew services start postgresql"
    echo "   Ubuntu: sudo systemctl start postgresql"
    echo "   CentOS/RHEL: sudo systemctl start postgresql"
    exit 1
fi

echo "✅ PostgreSQL is installed and running"

# Create database and user
echo "📝 Creating database and user..."

# Connect as postgres user to create database and user
sudo -u postgres psql << EOF
-- Create user if not exists
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DB_USER') THEN
      CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
   END IF;
END
\$\$;

-- Create database if not exists
SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER USER $DB_USER CREATEDB;

\q
EOF

echo "✅ Database '$DB_NAME' and user '$DB_USER' created successfully"

# Test connection
echo "🔍 Testing database connection..."
PGPASSWORD=$DB_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $DB_USER -d $DB_NAME -c "SELECT version();" > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ Database connection successful!"
else
    echo "❌ Database connection failed!"
    exit 1
fi

echo ""
echo "🎉 PostgreSQL setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Update your .env file with the following database configuration:"
echo "   ENVIRONMENT=production"
echo "   POSTGRES_SERVER=$POSTGRES_HOST"
echo "   POSTGRES_USER=$DB_USER"
echo "   POSTGRES_PASSWORD=$DB_PASSWORD"
echo "   POSTGRES_DB=$DB_NAME"
echo "   POSTGRES_PORT=$POSTGRES_PORT"
echo ""
echo "2. Install Python PostgreSQL adapter:"
echo "   pip install psycopg2-binary"
echo ""
echo "3. Run database migrations:"
echo "   alembic upgrade head"
echo ""
echo "4. Start your FastAPI application"
echo ""
echo "📊 Database connection URL:"
echo "   postgresql://$DB_USER:$DB_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$DB_NAME"
