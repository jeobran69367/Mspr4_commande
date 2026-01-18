"""Event handlers for order events (publishers)."""
from app.events.producer import get_event_producer
from typing import Dict, Any


async def publish_order_event(event_type: str, order_data: Dict[str, Any]):
    """Generic order event publisher."""
    producer = await get_event_producer()
    
    if event_type == "created":
        await producer.publish_order_created(order_data)
    elif event_type == "validated":
        await producer.publish_order_validated(order_data)
    elif event_type == "paid":
        await producer.publish_order_paid(order_data)
    elif event_type == "shipped":
        await producer.publish_order_shipped(order_data)
    elif event_type == "delivered":
        await producer.publish_order_delivered(order_data)
    elif event_type == "cancelled":
        await producer.publish_order_cancelled(order_data)
