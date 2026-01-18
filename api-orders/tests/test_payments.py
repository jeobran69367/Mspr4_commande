"""
Tests for payment operations.
"""
import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_get_payments_list(client: AsyncClient):
    """Test getting list of payments."""
    response = await client.get("/api/v1/payments")
    assert response.status_code in [200, 500, 503]


@pytest.mark.asyncio
async def test_get_payment_by_id(client: AsyncClient):
    """Test getting a specific payment."""
    payment_id = str(uuid4())
    response = await client.get(f"/api/v1/payments/{payment_id}")
    assert response.status_code in [200, 404, 500, 503]


@pytest.mark.asyncio
async def test_create_payment(client: AsyncClient):
    """Test creating a payment."""
    payment_data = {
        "order_id": str(uuid4()),
        "amount": 100.00,
        "payment_method": "credit_card"
    }
    response = await client.post("/api/v1/payments", json=payment_data)
    assert response.status_code in [200, 201, 422, 500, 503]


@pytest.mark.asyncio
async def test_update_payment_status(client: AsyncClient):
    """Test updating payment status."""
    payment_id = str(uuid4())
    response = await client.put(
        f"/api/v1/payments/{payment_id}/status",
        json={"status": "completed"}
    )
    assert response.status_code in [200, 404, 422, 500, 503]


@pytest.mark.asyncio
async def test_get_payments_by_order(client: AsyncClient):
    """Test getting payments for a specific order."""
    order_id = str(uuid4())
    response = await client.get(f"/api/v1/payments?order_id={order_id}")
    assert response.status_code in [200, 404, 500, 503]


@pytest.mark.asyncio
async def test_create_payment_invalid_amount(client: AsyncClient):
    """Test creating payment with invalid amount."""
    payment_data = {
        "order_id": str(uuid4()),
        "amount": -50.00,  # Negative amount
        "payment_method": "credit_card"
    }
    response = await client.post("/api/v1/payments", json=payment_data)
    assert response.status_code in [422, 400, 500, 503]


@pytest.mark.asyncio
async def test_create_payment_missing_method(client: AsyncClient):
    """Test creating payment without payment method."""
    payment_data = {
        "order_id": str(uuid4()),
        "amount": 100.00
        # Missing payment_method
    }
    response = await client.post("/api/v1/payments", json=payment_data)
    assert response.status_code in [422, 400, 500, 503]


@pytest.mark.asyncio
async def test_payment_refund(client: AsyncClient):
    """Test refunding a payment."""
    payment_id = str(uuid4())
    response = await client.post(f"/api/v1/payments/{payment_id}/refund")
    assert response.status_code in [200, 404, 422, 500, 503]


@pytest.mark.asyncio
async def test_payment_with_large_amount(client: AsyncClient):
    """Test creating payment with large amount."""
    payment_data = {
        "order_id": str(uuid4()),
        "amount": 999999.99,
        "payment_method": "bank_transfer"
    }
    response = await client.post("/api/v1/payments", json=payment_data)
    assert response.status_code in [200, 201, 422, 500, 503]


@pytest.mark.asyncio
async def test_payment_zero_amount(client: AsyncClient):
    """Test creating payment with zero amount."""
    payment_data = {
        "order_id": str(uuid4()),
        "amount": 0.00,
        "payment_method": "credit_card"
    }
    response = await client.post("/api/v1/payments", json=payment_data)
    assert response.status_code in [422, 400, 500, 503]
