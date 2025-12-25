"""
HTTP Client for Customer Service integration.
"""
import httpx
from typing import Optional, Dict, Any
from uuid import UUID
from app.config import settings


class CustomerClient:
    """Client for interacting with Customer Service."""
    
    def __init__(self):
        self.base_url = settings.customer_service_url
        self.timeout = 10.0
    
    async def get_customer(self, customer_id: UUID) -> Optional[Dict[str, Any]]:
        """Get customer details by ID."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/customers/{customer_id}"
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"Error fetching customer {customer_id}: {e}")
            return None
    
    async def validate_customer(self, customer_id: UUID) -> bool:
        """Validate that a customer exists and is active."""
        customer = await self.get_customer(customer_id)
        if not customer:
            return False
        
        # Check if customer is active
        return customer.get("status") == "active"
    
    async def get_customer_addresses(self, customer_id: UUID) -> Optional[Dict[str, Any]]:
        """Get customer addresses."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/customers/{customer_id}/addresses"
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"Error fetching customer addresses {customer_id}: {e}")
            return None
    
    async def check_customer_credit_limit(
        self,
        customer_id: UUID,
        order_amount: float
    ) -> bool:
        """Check if customer has sufficient credit limit."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/customers/{customer_id}/check-credit",
                    json={"amount": order_amount}
                )
                response.raise_for_status()
                result = response.json()
                return result.get("has_credit", False)
        except httpx.HTTPError as e:
            print(f"Error checking customer credit limit: {e}")
            return False
