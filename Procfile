web: sh -c 'cd api-orders && export PYTHONPATH=${PYTHONPATH}:$(pwd) && alembic upgrade head || true && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8003}'
