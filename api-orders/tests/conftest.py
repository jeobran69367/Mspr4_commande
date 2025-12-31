"""
Test configuration and fixtures.
"""
import pytest
import asyncio
import os
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

# Set test environment variables before importing app
os.environ["RUN_MIGRATIONS"] = "false"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["RABBITMQ_HOST"] = "localhost"
os.environ["RABBITMQ_PORT"] = "5672"
os.environ["RABBITMQ_USER"] = "test"
os.environ["RABBITMQ_PASSWORD"] = "test"

from app.main import app


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
    
    # Override the lifespan to skip real connections
    from contextlib import asynccontextmanager
    
    @asynccontextmanager
    async def test_lifespan(app):
        # Startup - do nothing or minimal setup
        print("Test mode: Skipping real RabbitMQ and DB connections")
        yield
        # Shutdown - do nothing
        print("Test mode: Cleanup")
    
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
