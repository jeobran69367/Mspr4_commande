"""
FastAPI main application for Orders Service.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from alembic import command
from alembic.config import Config
import os

from app.config import settings
from app.api.v1 import api_router
from app.events.producer import get_event_producer
from app.events.consumer import get_event_consumer
from app.events.handlers.customer_events import (
    handle_customer_created,
    handle_customer_updated,
    handle_customer_deleted
)
from app.events.handlers.product_events import (
    handle_product_created,
    handle_product_updated,
    handle_product_deleted,
    handle_product_stock_updated
)


def run_migrations():
    """
    Run Alembic migrations.
    """
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""

    # ------------------
    # Startup
    # ------------------
    print("Starting Orders Service...")

    # Run migrations (DEV / TEST only)
    if os.getenv("RUN_MIGRATIONS", "true").lower() == "true":
        print("Running database migrations...")
        try:
            run_migrations()
            print("Database migrations completed")
        except Exception as e:
            print(f"Warning: Migration failed: {e}")
            print("Continuing startup anyway...")

    # Initialize event producer (with error handling)
    producer = None
    consumer = None
    
    try:
        producer = await get_event_producer()
        print("Event producer initialized")
    except Exception as e:
        print(f"Warning: Could not initialize event producer: {e}")
        print("Continuing without event producer (RabbitMQ may be unavailable)")

    # Initialize event consumer (with error handling)
    try:
        consumer = await get_event_consumer()

        # Register event handlers
        consumer.register_handler("customer.created", handle_customer_created)
        consumer.register_handler("customer.updated", handle_customer_updated)
        consumer.register_handler("customer.deleted", handle_customer_deleted)
        consumer.register_handler("product.created", handle_product_created)
        consumer.register_handler("product.updated", handle_product_updated)
        consumer.register_handler("product.deleted", handle_product_deleted)
        consumer.register_handler("product.stock.updated", handle_product_stock_updated)

        print("Event consumer initialized")
    except Exception as e:
        print(f"Warning: Could not initialize event consumer: {e}")
        print("Continuing without event consumer (RabbitMQ may be unavailable)")

    print("Orders Service startup complete!")

    yield

    # ------------------
    # Shutdown
    # ------------------
    print("Shutting down Orders Service...")
    
    if producer:
        try:
            await producer.disconnect()
        except Exception as e:
            print(f"Warning during producer shutdown: {e}")
    
    if consumer:
        try:
            await consumer.disconnect()
        except Exception as e:
            print(f"Warning during consumer shutdown: {e}")
    
    print("Orders Service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Orders Service API - PayeTonKawa",
    description="Service de gestion des commandes avec Saga Pattern",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "service": "Orders Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "orders",
        "port": settings.api_port
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )
