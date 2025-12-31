"""
Test configuration and fixtures.
"""
import pytest
import asyncio
import os
import sys
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

# Set test environment variables before importing anything
os.environ["RUN_MIGRATIONS"] = "false"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["RABBITMQ_HOST"] = "localhost"
os.environ["RABBITMQ_PORT"] = "5672"
os.environ["RABBITMQ_USER"] = "test"
os.environ["RABBITMQ_PASSWORD"] = "test"
os.environ["TESTING"] = "true"

# Ensure the app directory is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from httpx import AsyncClient, ASGITransport
    from app.main import app
except ImportError as e:
    print(f"Warning: Failed to import dependencies: {e}")
    print("Make sure to install requirements: pip install -r requirements.txt")
    raise


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Create a test client with mocked dependencies.
    This avoids needing a real database or RabbitMQ connection.
    """
    # Mock the event producer and consumer to avoid RabbitMQ connection
    mock_producer = AsyncMock()
    mock_producer.connect = AsyncMock()
    mock_producer.disconnect = AsyncMock()
    mock_producer.publish_event = AsyncMock()
    
    mock_consumer = AsyncMock()
    mock_consumer.connect = AsyncMock()
    mock_consumer.disconnect = AsyncMock()
    mock_consumer.register_handler = MagicMock()
    mock_consumer.start_consuming = AsyncMock()
    
    # Override the lifespan to skip real connections and create tables
    from contextlib import asynccontextmanager
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from app.models.base import Base
    
    @asynccontextmanager
    async def test_lifespan(app):
        # Startup - create in-memory database tables
        print("Test mode: Creating in-memory SQLite tables")
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,
            future=True
        )
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("Test mode: Tables created, skipping RabbitMQ connections")
        yield
        
        # Shutdown - cleanup
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()
        print("Test mode: Cleanup complete")
    
    # Replace the app's lifespan
    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = test_lifespan
    
    # Create test client
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    # Restore original lifespan
    app.router.lifespan_context = original_lifespan


@pytest.fixture
def sample_order_data():
    """Sample order data for tests."""
    from uuid import uuid4
    return {
        "customer_id": str(uuid4()),
        "customer_email": "test@example.com",
        "shipping_address": {
            "ligne1": "123 Test St",
            "ville": "Paris",
            "code_postal": "75001",
            "pays": "France"
        },
        "billing_address": {
            "ligne1": "123 Test St",
            "ville": "Paris",
            "code_postal": "75001",
            "pays": "France"
        },
        "items": [
            {
                "product_id": str(uuid4()),
                "product_reference": "TEST-001",
                "product_name": "Test Product",
                "quantity": 2,
                "unit_price_ht": 25.00,
                "tax_rate": 0.20
            }
        ]
    }
