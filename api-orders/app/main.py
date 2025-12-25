"""
FastAPI main application for Orders Service.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    print("Starting Orders Service...")
    
    # Initialize event producer
    producer = await get_event_producer()
    print("Event producer initialized")
    
    # Initialize event consumer
    consumer = await get_event_consumer()
    
    # Register event handlers
    consumer.register_handler("customer.created", handle_customer_created)
    consumer.register_handler("customer.updated", handle_customer_updated)
    consumer.register_handler("customer.deleted", handle_customer_deleted)
    consumer.register_handler("product.created", handle_product_created)
    consumer.register_handler("product.updated", handle_product_updated)
    consumer.register_handler("product.deleted", handle_product_deleted)
    consumer.register_handler("product.stock.updated", handle_product_stock_updated)
    
    # Start consuming (non-blocking)
    # await consumer.start_consuming(
    #     queue_name=settings.rabbitmq_queue_orders,
    #     binding_patterns=["customer.*", "product.*"]
    # )
    print("Event consumer initialized")
    
    yield
    
    # Shutdown
    print("Shutting down Orders Service...")
    await producer.disconnect()
    await consumer.disconnect()


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
    """Root endpoint."""
    return {
        "service": "Orders Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
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
