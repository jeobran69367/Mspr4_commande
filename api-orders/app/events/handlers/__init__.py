"""Event handlers package."""
from app.events.handlers.customer_events import (
    handle_customer_created,
    handle_customer_updated,
    handle_customer_deleted,
)
from app.events.handlers.product_events import (
    handle_product_created,
    handle_product_updated,
    handle_product_deleted,
    handle_product_stock_updated,
)
from app.events.handlers.order_events import publish_order_event

__all__ = [
    "handle_customer_created",
    "handle_customer_updated",
    "handle_customer_deleted",
    "handle_product_created",
    "handle_product_updated",
    "handle_product_deleted",
    "handle_product_stock_updated",
    "publish_order_event",
]
