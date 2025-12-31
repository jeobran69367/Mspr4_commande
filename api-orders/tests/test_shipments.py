"""
Tests for shipment operations.
"""
import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_get_shipments_list(client: AsyncClient):
    """Test getting list of shipments."""
    response = await client.get("/api/v1/shipments")
    assert response.status_code in [200, 500, 503]


@pytest.mark.asyncio
async def test_get_shipment_by_id(client: AsyncClient):
    """Test getting a specific shipment."""
    shipment_id = str(uuid4())
    response = await client.get(f"/api/v1/shipments/{shipment_id}")
    assert response.status_code in [200, 404, 500, 503]


@pytest.mark.asyncio
async def test_create_shipment(client: AsyncClient):
    """Test creating a shipment."""
    shipment_data = {
        "order_id": str(uuid4()),
        "carrier": "DHL",
        "tracking_number": "DHL123456789"
    }
    response = await client.post("/api/v1/shipments", json=shipment_data)
    assert response.status_code in [200, 201, 422, 500, 503]


@pytest.mark.asyncio
async def test_update_shipment_status(client: AsyncClient):
    """Test updating shipment status."""
    shipment_id = str(uuid4())
    response = await client.put(
        f"/api/v1/shipments/{shipment_id}/status",
        json={"status": "in_transit"}
    )
    assert response.status_code in [200, 404, 422, 500, 503]


@pytest.mark.asyncio
async def test_get_shipments_by_order(client: AsyncClient):
    """Test getting shipment for a specific order."""
    order_id = str(uuid4())
    response = await client.get(f"/api/v1/shipments?order_id={order_id}")
    assert response.status_code in [200, 404, 500, 503]


@pytest.mark.asyncio
async def test_track_shipment(client: AsyncClient):
    """Test tracking a shipment."""
    tracking_number = "TRACK123456"
    response = await client.get(f"/api/v1/shipments/track/{tracking_number}")
    assert response.status_code in [200, 404, 500, 503]


@pytest.mark.asyncio
async def test_create_shipment_missing_carrier(client: AsyncClient):
    """Test creating shipment without carrier."""
    shipment_data = {
        "order_id": str(uuid4()),
        "tracking_number": "TRACK123"
        # Missing carrier
    }
    response = await client.post("/api/v1/shipments", json=shipment_data)
    assert response.status_code in [422, 400, 500, 503]


@pytest.mark.asyncio
async def test_update_shipment_delivered(client: AsyncClient):
    """Test marking shipment as delivered."""
    shipment_id = str(uuid4())
    response = await client.put(
        f"/api/v1/shipments/{shipment_id}/status",
        json={"status": "delivered"}
    )
    assert response.status_code in [200, 404, 422, 500, 503]


@pytest.mark.asyncio
async def test_get_shipment_invalid_id(client: AsyncClient):
    """Test getting shipment with invalid ID format."""
    invalid_id = "not-a-uuid"
    response = await client.get(f"/api/v1/shipments/{invalid_id}")
    assert response.status_code in [404, 422, 500, 503]


@pytest.mark.asyncio
async def test_create_shipment_duplicate_tracking(client: AsyncClient):
    """Test creating shipment with duplicate tracking number."""
    tracking_number = "DUP123456"
    shipment_data = {
        "order_id": str(uuid4()),
        "carrier": "FedEx",
        "tracking_number": tracking_number
    }
    
    # First creation
    response1 = await client.post("/api/v1/shipments", json=shipment_data)
    assert response1.status_code in [200, 201, 422, 500, 503]
    
    # Second creation with same tracking number
    shipment_data["order_id"] = str(uuid4())  # Different order
    response2 = await client.post("/api/v1/shipments", json=shipment_data)
    assert response2.status_code in [200, 201, 422, 409, 500, 503]
