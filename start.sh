#!/bin/bash

echo "Starting Orders Service..."
echo "Current working directory: $(pwd)"
echo "Directory contents:"
ls -la

# Check if api-orders directory exists
if [ ! -d "api-orders" ]; then
    echo "ERROR: api-orders directory not found!"
    echo "This service requires the api-orders subdirectory to be present."
    echo "Available directories:"
    ls -la
    exit 1
fi

# Change to api-orders directory
echo "Changing to api-orders directory..."
cd api-orders || {
    echo "ERROR: Failed to cd into api-orders"
    exit 1
}

echo "Now in directory: $(pwd)"
echo "Contents:"
ls -la

# Set Python path to include current directory
export PYTHONPATH="$(pwd):${PYTHONPATH}"
echo "PYTHONPATH set to: $PYTHONPATH"

# Verify app module is accessible
echo "Verifying app.main module..."
python3 -c "import app.main; print('✓ app.main imported successfully')" || {
    echo "ERROR: Cannot import app.main"
    echo "Current PYTHONPATH: $PYTHONPATH"
    echo "Python version: $(python3 --version)"
    echo "Available Python modules:"
    python3 -c "import sys; print('\n'.join(sys.path))"
    exit 1
}

# Run database migrations (allow failure)
echo "Running database migrations..."
alembic upgrade head 2>&1 || {
    echo "⚠ Warning: Database migration failed or Alembic not available"
    echo "Continuing to start the service..."
}

# Get port from environment or use default
PORT=${PORT:-8003}
echo "Starting uvicorn on 0.0.0.0:$PORT..."

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"