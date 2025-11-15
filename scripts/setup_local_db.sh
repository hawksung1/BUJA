#!/bin/bash
# Local PostgreSQL Database Setup Script

set -e

echo "🚀 Setting up local PostgreSQL database..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start PostgreSQL container
echo "📦 Starting PostgreSQL container..."
docker-compose -f docker-compose.local.yml up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
timeout=30
counter=0
until docker exec buja_postgres_local pg_isready -U postgres > /dev/null 2>&1; do
    sleep 1
    counter=$((counter + 1))
    if [ $counter -ge $timeout ]; then
        echo "❌ PostgreSQL failed to start within $timeout seconds"
        exit 1
    fi
done

echo "✅ PostgreSQL is ready!"

# Create database if it doesn't exist
echo "📝 Creating database if needed..."
docker exec buja_postgres_local psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'buja_local'" | grep -q 1 || \
    docker exec buja_postgres_local psql -U postgres -c "CREATE DATABASE buja_local"

echo "✅ Database setup complete!"
echo ""
echo "📋 Connection details:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: buja_local"
echo "   User: postgres"
echo "   Password: postgres"
echo ""
echo "🔧 To stop the database: docker-compose -f docker-compose.local.yml down"
echo "🔧 To view logs: docker-compose -f docker-compose.local.yml logs -f postgres"

