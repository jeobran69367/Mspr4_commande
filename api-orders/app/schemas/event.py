"""
Pydantic schemas for events (RabbitMQ).
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, UUID4
from enum import Enum


class EventType(str, Enum):
    """Event type enum."""
    # Order events
    ORDER_CREATED = "order.created"
    ORDER_VALIDATED = "order.validated"
    ORDER_PAID = "order.paid"
    ORDER_SHIPPED = "order.shipped"
    ORDER_DELIVERED = "order.delivered"
    ORDER_CANCELLED = "order.cancelled"
    
    # Customer events
    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_UPDATED = "customer.updated"
    CUSTOMER_DELETED = "customer.deleted"
    
    # Product events
    PRODUCT_CREATED = "product.created"
    PRODUCT_UPDATED = "product.updated"
    PRODUCT_DELETED = "product.deleted"
    PRODUCT_STOCK_UPDATED = "product.stock.updated"


class EventBase(BaseModel):
    """Base schema for events."""
    event_type: EventType
    event_id: str
    timestamp: datetime
    source_service: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class OrderEvent(EventBase):
    """Schema for order events."""
    order_id: UUID4
    customer_id: UUID4


class CustomerEvent(EventBase):
    """Schema for customer events."""
    customer_id: UUID4


class ProductEvent(EventBase):
    """Schema for product events."""
    product_id: UUID4


class EventPublishRequest(BaseModel):
    """Schema for event publish request."""
    event_type: EventType
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
