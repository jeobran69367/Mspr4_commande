"""
HTTP Client for Product Service integration.
"""
import httpx
from typing import Optional, Dict, Any, List
from uuid import UUID
from app.config import settings


class ProductClient:
    """Client for interacting with Product Service."""
    
    def __init__(self):
        self.base_url = settings.product_service_url
        self.timeout = 10.0
    
    async def get_product(self, product_id: UUID) -> Optional[Dict[str, Any]]:
        """Get product details by ID."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/products/{product_id}"
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"Error fetching product {product_id}: {e}")
            return None
    
    async def check_stock_availability(
        self,
        product_id: UUID,
        quantity: int
    ) -> bool:
        """Check if product has sufficient stock."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/products/{product_id}/check-stock",
                    json={"quantity": quantity}
                )
                response.raise_for_status()
                result = response.json()
                return result.get("available", False)
        except httpx.HTTPError as e:
            print(f"Error checking stock for product {product_id}: {e}")
            return False
    
    async def reserve_stock(
        self,
        product_id: UUID,
        quantity: int,
        order_id: UUID
    ) -> Optional[str]:
        """Reserve stock for an order."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/products/{product_id}/reserve",
                    json={
                        "quantity": quantity,
                        "order_id": str(order_id),
                        "reservation_type": "order"
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result.get("reservation_id")
        except httpx.HTTPError as e:
            print(f"Error reserving stock for product {product_id}: {e}")
            return None
    
    async def release_stock(
        self,
        product_id: UUID,
        quantity: int,
        order_id: UUID
    ) -> bool:
        """Release reserved stock (compensation action)."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/products/{product_id}/release",
                    json={
                        "quantity": quantity,
                        "order_id": str(order_id)
                    }
                )
                response.raise_for_status()
                return True
        except httpx.HTTPError as e:
            print(f"Error releasing stock for product {product_id}: {e}")
            return False
    
    async def get_product_prices(self, product_ids: List[UUID]) -> Dict[UUID, float]:
        """Get prices for multiple products."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/products/prices",
                    json={"product_ids": [str(pid) for pid in product_ids]}
                )
                response.raise_for_status()
                result = response.json()
                return {UUID(k): v for k, v in result.get("prices", {}).items()}
        except httpx.HTTPError as e:
            print(f"Error fetching product prices: {e}")
            return {}
