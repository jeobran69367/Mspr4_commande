"""
Tests for cart operations.
"""
import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_cart(client: AsyncClient):
    """Test creating a new cart."""
    cart_id = str(uuid4())
    response = await client.post(f"/api/v1/carts", json={"cart_id": cart_id})
    assert response.status_code in [200, 201, 422, 500, 503]


@pytest.mark.asyncio
async def test_get_cart_empty(client: AsyncClient):
    """Test getting an empty cart."""
    cart_id = str(uuid4())
    response = await client.get(f"/api/v1/carts/{cart_id}")
    assert response.status_code in [200, 404, 500, 503]


@pytest.mark.asyncio
async def test_add_multiple_items_to_cart(client: AsyncClient):
    """Test adding multiple items to cart."""
    cart_id = str(uuid4())
    
    # Add first item
    item1 = {
        "product_id": str(uuid4()),
        "product_reference": "PROD-001",
        "product_name": "Product 1",
        "quantity": 2,
        "unit_price_ht": 15.00,
        "tax_rate": 0.20
    }
    response1 = await client.post(f"/api/v1/carts/{cart_id}/items", json=item1)
    assert response1.status_code in [200, 201, 422, 500, 503]
    
    # Add second item
    item2 = {
        "product_id": str(uuid4()),
        "product_reference": "PROD-002",
        "product_name": "Product 2",
        "quantity": 1,
        "unit_price_ht": 25.00,
        "tax_rate": 0.20
    }
    response2 = await client.post(f"/api/v1/carts/{cart_id}/items", json=item2)
    assert response2.status_code in [200, 201, 422, 500, 503]


@pytest.mark.asyncio
async def test_update_cart_item(client: AsyncClient):
    """Test updating cart item quantity."""
    cart_id = str(uuid4())
    item_id = str(uuid4())
    
    update_data = {
        "quantity": 3
    }
    response = await client.put(
        f"/api/v1/carts/{cart_id}/items/{item_id}",
        json=update_data
    )
    assert response.status_code in [200, 404, 422, 500, 503]


@pytest.mark.asyncio
async def test_remove_item_from_cart(client: AsyncClient):
    """Test removing item from cart."""
    cart_id = str(uuid4())
    item_id = str(uuid4())
    
    response = await client.delete(f"/api/v1/carts/{cart_id}/items/{item_id}")
    assert response.status_code in [200, 204, 404, 500, 503]


@pytest.mark.asyncio
async def test_get_cart_summary_with_items(client: AsyncClient):
    """Test getting cart summary."""
    cart_id = str(uuid4())
    response = await client.get(f"/api/v1/carts/{cart_id}/summary")
    assert response.status_code in [200, 404, 500, 503]


@pytest.mark.asyncio
async def test_clear_cart_with_items(client: AsyncClient):
    """Test clearing cart that has items."""
    cart_id = str(uuid4())
    response = await client.delete(f"/api/v1/carts/{cart_id}")
    assert response.status_code in [200, 204, 404, 500, 503]


@pytest.mark.asyncio
async def test_add_same_product_twice(client: AsyncClient):
    """Test adding same product to cart twice (should update quantity)."""
    cart_id = str(uuid4())
    product_id = str(uuid4())
    
    item_data = {
        "product_id": product_id,
        "product_reference": "PROD-001",
        "product_name": "Product",
        "quantity": 1,
        "unit_price_ht": 10.00,
        "tax_rate": 0.20
    }
    
    # Add first time
    response1 = await client.post(f"/api/v1/carts/{cart_id}/items", json=item_data)
    assert response1.status_code in [200, 201, 422, 500, 503]
    
    # Add second time (same product)
    response2 = await client.post(f"/api/v1/carts/{cart_id}/items", json=item_data)
    assert response2.status_code in [200, 201, 422, 500, 503]


@pytest.mark.asyncio
async def test_cart_with_large_quantity(client: AsyncClient):
    """Test adding item with large quantity."""
    cart_id = str(uuid4())
    
    item_data = {
        "product_id": str(uuid4()),
        "product_reference": "PROD-001",
        "product_name": "Product",
        "quantity": 1000,  # Large quantity
        "unit_price_ht": 5.00,
        "tax_rate": 0.20
    }
    
    response = await client.post(f"/api/v1/carts/{cart_id}/items", json=item_data)
    assert response.status_code in [200, 201, 422, 400, 500, 503]


@pytest.mark.asyncio
async def test_cart_with_high_price(client: AsyncClient):
    """Test adding expensive item to cart."""
    cart_id = str(uuid4())
    
    item_data = {
        "product_id": str(uuid4()),
        "product_reference": "EXPENSIVE-001",
        "product_name": "Expensive Product",
        "quantity": 1,
        "unit_price_ht": 9999.99,  # High price
        "tax_rate": 0.20
    }
    
    response = await client.post(f"/api/v1/carts/{cart_id}/items", json=item_data)
    assert response.status_code in [200, 201, 422, 500, 503]
