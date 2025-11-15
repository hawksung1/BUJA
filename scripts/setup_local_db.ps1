# Local PostgreSQL Database Setup Script (PowerShell)

Write-Host "🚀 Setting up local PostgreSQL database..." -ForegroundColor Cyan

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

# Start PostgreSQL container
Write-Host "📦 Starting PostgreSQL container..." -ForegroundColor Yellow
docker-compose -f docker-compose.local.yml up -d postgres

# Wait for PostgreSQL to be ready
Write-Host "⏳ Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
$timeout = 30
$counter = 0
$ready = $false

while ($counter -lt $timeout) {
    try {
        docker exec buja_postgres_local pg_isready -U postgres | Out-Null
        $ready = $true
        break
    } catch {
        Start-Sleep -Seconds 1
        $counter++
    }
}

if (-not $ready) {
    Write-Host "❌ PostgreSQL failed to start within $timeout seconds" -ForegroundColor Red
    exit 1
}

Write-Host "✅ PostgreSQL is ready!" -ForegroundColor Green

# Create database if it doesn't exist
Write-Host "📝 Creating database if needed..." -ForegroundColor Yellow
$dbExists = docker exec buja_postgres_local psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'buja_local'"

if (-not $dbExists) {
    docker exec buja_postgres_local psql -U postgres -c "CREATE DATABASE buja_local"
}

Write-Host "✅ Database setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Connection details:" -ForegroundColor Cyan
Write-Host "   Host: localhost"
Write-Host "   Port: 5432"
Write-Host "   Database: buja_local"
Write-Host "   User: postgres"
Write-Host "   Password: postgres"
Write-Host ""
Write-Host "🔧 To stop the database: docker-compose -f docker-compose.local.yml down" -ForegroundColor Yellow
Write-Host "🔧 To view logs: docker-compose -f docker-compose.local.yml logs -f postgres" -ForegroundColor Yellow

