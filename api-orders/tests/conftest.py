"""
Test configuration and fixtures.
"""
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient

from app.main import app
from app.database import Base, get_db
from app.config import settings

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://orders_test_user:orders_test_password@localhost:5436/orders_test_db"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


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
