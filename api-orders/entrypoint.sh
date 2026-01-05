#!/bin/bash
set -e

echo "🚀 Orders Service - Starting Deployment"
echo "========================================="

# Display environment info
echo "📊 Environment Information:"
echo "   - Python Version: $(python --version)"
echo "   - Working Directory: $(pwd)"
echo "   - Port: ${PORT:-8003}"
echo ""

# Check database connectivity
echo "🔍 Checking database connectivity..."
if [ -n "$DATABASE_URL" ]; then
    echo "   ✅ DATABASE_URL is set"
    # Try to connect using psql if available
    if command -v psql &> /dev/null; then
        echo "   🔄 Testing database connection..."
        if psql "$DATABASE_URL" -c "SELECT 1;" &> /dev/null; then
            echo "   ✅ Database connection successful"
        else
            echo "   ⚠️  Database connection test failed (but continuing anyway)"
        fi
    fi
else
    echo "   ⚠️  DATABASE_URL not set - using default"
fi
echo ""

# Run database migrations
echo "📦 Running database migrations..."
if [ -f "alembic.ini" ]; then
    if alembic upgrade head; then
        echo "   ✅ Migrations completed successfully"
    else
        echo "   ❌ Migration failed! Exiting..."
        exit 1
    fi
else
    echo "   ⚠️  alembic.ini not found - skipping migrations"
fi
echo ""

# Start the application
echo "🌐 Starting Orders API Server..."
echo "   - Host: 0.0.0.0"
echo "   - Port: ${PORT:-8003}"
echo "   - Health Check: http://0.0.0.0:${PORT:-8003}/health"
echo "   - API Docs: http://0.0.0.0:${PORT:-8003}/docs"
echo ""
echo "========================================="
echo "✨ Orders Service is starting up..."
echo ""

# Disable migrations in app lifespan
export RUN_MIGRATIONS=false

# Start uvicorn with proper configuration
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8003}" \
    --log-level info \
    --no-access-log \
    --timeout-keep-alive 120
