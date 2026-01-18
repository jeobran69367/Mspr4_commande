"""Event handlers for customer events."""
from typing import Dict, Any


async def handle_customer_created(event: Dict[str, Any]):
    """Handle customer created event."""
    customer_data = event.get("data", {})
    customer_id = customer_data.get("customer_id")
    print(f"Customer created: {customer_id}")
    # Cache customer data if needed


async def handle_customer_updated(event: Dict[str, Any]):
    """Handle customer updated event."""
    customer_data = event.get("data", {})
    customer_id = customer_data.get("customer_id")
    print(f"Customer updated: {customer_id}")
    # Update cached customer data if needed


async def handle_customer_deleted(event: Dict[str, Any]):
    """Handle customer deleted event."""
    customer_data = event.get("data", {})
    customer_id = customer_data.get("customer_id")
    print(f"Customer deleted: {customer_id}")
    # Handle customer deletion (mark orders, etc.)
