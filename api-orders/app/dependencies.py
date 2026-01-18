"""
Dependencies for FastAPI application.
"""
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.order_service import OrderService
from app.services.cart_service import CartService
from app.integrations.customer_client import CustomerClient
from app.integrations.product_client import ProductClient
from app.integrations.payment_gateway import PaymentGateway


async def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    """Get order service instance."""
    return OrderService(db)


async def get_cart_service(db: AsyncSession = Depends(get_db)) -> CartService:
    """Get cart service instance."""
    return CartService(db)


def get_customer_client() -> CustomerClient:
    """Get customer client instance."""
    return CustomerClient()


def get_product_client() -> ProductClient:
    """Get product client instance."""
    return ProductClient()


def get_payment_gateway() -> PaymentGateway:
    """Get payment gateway instance."""
    return PaymentGateway()
