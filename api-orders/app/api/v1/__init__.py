"""API v1 package."""
from fastapi import APIRouter
from app.api.v1 import orders, carts

api_router = APIRouter()

# Include routers
api_router.include_router(orders.router)
api_router.include_router(carts.router)

__all__ = ["api_router"]
