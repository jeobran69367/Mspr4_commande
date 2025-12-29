#!/bin/bash
set -e  # Exit on error

echo "Starting Orders Service..."

# Check if api-orders directory exists
if [ ! -d "api-orders" ]; then
    echo "Error: api-orders directory not found!"
    exit 1
fi

# Change to api-orders directory
cd api-orders

echo "Current directory: $(pwd)"
echo "Contents: $(ls -la)"

# Set Python path to include current directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check if app module is accessible
python -c "import app.main" || {
    echo "Error: Cannot import app.main"
    echo "Python path: $PYTHONPATH"
    exit 1
}

# Run database migrations
echo "Running database migrations..."
alembic upgrade head || {
    echo "Warning: Database migration failed, continuing anyway..."
}

# Get port from environment or use default
PORT=${PORT:-8003}
echo "Starting uvicorn on port $PORT..."

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port $PORT