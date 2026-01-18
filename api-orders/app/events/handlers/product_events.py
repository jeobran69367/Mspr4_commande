"""Event handlers for product events."""
from typing import Dict, Any


async def handle_product_created(event: Dict[str, Any]):
    """Handle product created event."""
    product_data = event.get("data", {})
    product_id = product_data.get("product_id")
    print(f"Product created: {product_id}")


async def handle_product_updated(event: Dict[str, Any]):
    """Handle product updated event."""
    product_data = event.get("data", {})
    product_id = product_data.get("product_id")
    print(f"Product updated: {product_id}")


async def handle_product_deleted(event: Dict[str, Any]):
    """Handle product deleted event."""
    product_data = event.get("data", {})
    product_id = product_data.get("product_id")
    print(f"Product deleted: {product_id}")


async def handle_product_stock_updated(event: Dict[str, Any]):
    """Handle product stock updated event."""
    product_data = event.get("data", {})
    product_id = product_data.get("product_id")
    stock = product_data.get("stock", 0)
    print(f"Product {product_id} stock updated: {stock}")
