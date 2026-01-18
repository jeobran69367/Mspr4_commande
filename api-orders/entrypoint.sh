#!/bin/bash
set -e

echo "🚀 Orders Service - Starting"

# Run database migrations
if [ -f "alembic.ini" ]; then
    echo "📦 Running migrations..."
    alembic upgrade head || exit 1
else
    echo "⚠️  No migrations found"
fi

# Disable migrations in app lifespan
export RUN_MIGRATIONS=false

# Start uvicorn
echo "🌐 Starting on port ${PORT:-8003}"
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8003}" \
    --log-level warning \
    --no-access-log \
    --timeout-keep-alive 120
