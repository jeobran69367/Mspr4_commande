"""
Carts API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID

from app.schemas.cart import (
    CartResponse,
    AddToCartRequest,
    UpdateCartItemRequest,
    CartSummary
)
from app.services.cart_service import CartService
from app.dependencies import get_cart_service

router = APIRouter(prefix="/carts", tags=["carts"])


@router.get("/{customer_id}", response_model=CartResponse)
async def get_cart(
    customer_id: UUID,
    service: CartService = Depends(get_cart_service)
):
    """Get or create cart for customer."""
    cart = await service.get_or_create_cart(customer_id)
    return cart


@router.post("/{customer_id}/items", response_model=CartResponse)
async def add_item_to_cart(
    customer_id: UUID,
    add_item: AddToCartRequest,
    service: CartService = Depends(get_cart_service)
):
    """Add item to cart."""
    cart = await service.add_item(customer_id, add_item)
    return cart


@router.put("/{customer_id}/items/{item_id}", response_model=CartResponse)
async def update_cart_item(
    customer_id: UUID,
    item_id: UUID,
    update_item: UpdateCartItemRequest,
    service: CartService = Depends(get_cart_service)
):
    """Update cart item quantity."""
    cart = await service.update_item(customer_id, item_id, update_item)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart or item not found"
        )
    return cart


@router.delete("/{customer_id}/items/{item_id}", response_model=CartResponse)
async def remove_cart_item(
    customer_id: UUID,
    item_id: UUID,
    service: CartService = Depends(get_cart_service)
):
    """Remove item from cart."""
    cart = await service.remove_item(customer_id, item_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    return cart


@router.delete("/{customer_id}", response_model=CartResponse)
async def clear_cart(
    customer_id: UUID,
    service: CartService = Depends(get_cart_service)
):
    """Clear all items from cart."""
    cart = await service.clear_cart(customer_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    return cart


@router.get("/{customer_id}/summary", response_model=CartSummary)
async def get_cart_summary(
    customer_id: UUID,
    service: CartService = Depends(get_cart_service)
):
    """Get cart summary with totals."""
    summary = await service.get_cart_summary(customer_id)
    return summary
