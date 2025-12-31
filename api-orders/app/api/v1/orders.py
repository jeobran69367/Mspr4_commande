"""
Orders API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID

from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderStatusUpdate,
    OrderListResponse
)
from app.services.order_service import OrderService
from app.dependencies import get_order_service, get_customer_client
from app.integrations.customer_client import CustomerClient
from app.sagas.create_order_saga import CreateOrderSaga
from app.events.handlers.order_events import publish_order_event

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    service: OrderService = Depends(get_order_service),
    customer_client: CustomerClient = Depends(get_customer_client)
):
    """Create a new order."""
    try:
        # Validate customer
        customer = await customer_client.get_customer(order_data.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Create order
        order = await service.create_order(order_data, customer)
        
        # Publish order created event
        await publish_order_event("created", {
            "order_id": str(order.id),
            "order_numero": order.numero,
            "customer_id": str(order.customer_id),
            "total_ttc": float(order.total_ttc)
        })
        
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    service: OrderService = Depends(get_order_service)
):
    """Get order by ID."""
    order = await service.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order


@router.get("/numero/{numero}", response_model=OrderResponse)
async def get_order_by_numero(
    numero: str,
    service: OrderService = Depends(get_order_service)
):
    """Get order by order number."""
    order = await service.get_order_by_numero(numero)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order


@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    customer_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: OrderService = Depends(get_order_service)
):
    """List orders with optional filters."""
    from app.models.order import OrderStatus
    
    order_status = OrderStatus(status) if status else None
    orders = await service.list_orders(customer_id, order_status, skip, limit)
    return orders


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: UUID,
    order_update: OrderUpdate,
    service: OrderService = Depends(get_order_service)
):
    """Update order."""
    order = await service.update_order(order_id, order_update)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: UUID,
    status_update: OrderStatusUpdate,
    service: OrderService = Depends(get_order_service)
):
    """Update order status."""
    try:
        order = await service.update_order_status(
            order_id,
            status_update.status,
            status_update.notes
        )
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Publish status change event
        event_map = {
            "validee": "validated",
            "expediee": "shipped",
            "livree": "delivered",
            "annulee": "cancelled"
        }
        event_type = event_map.get(status_update.status.value)
        if event_type:
            await publish_order_event(event_type, {
                "order_id": str(order.id),
                "order_numero": order.numero,
                "status": status_update.status.value
            })
        
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: UUID,
    reason: Optional[str] = None,
    service: OrderService = Depends(get_order_service)
):
    """Cancel an order."""
    order = await service.cancel_order(order_id, reason)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Publish cancellation event
    await publish_order_event("cancelled", {
        "order_id": str(order.id),
        "order_numero": order.numero,
        "reason": reason
    })
    
    return order


import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_order(client):
    order_data = {
        "customer_id": "12345",
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
                "product_id": "67890",
                "product_reference": "TEST-001",
                "product_name": "Test Product",
                "quantity": 2,
                "unit_price_ht": 25.00,
                "tax_rate": 0.20
            }
        ]
    }
    response = await client.post("/api/v1/orders", json=order_data)
    assert response.status_code == 201
    assert response.json()["customer_email"] == "test@example.com"

@pytest.mark.asyncio
async def test_get_order(client):
    response = await client.get("/api/v1/orders/12345")
    assert response.status_code == 200
    assert response.json()["customer_id"] == "12345"
