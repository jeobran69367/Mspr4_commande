"""
Pydantic schemas for shipments.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, UUID4
from enum import Enum


class ShipmentStatus(str, Enum):
    """Shipment status enum."""
    EN_ATTENTE = "en_attente"
    PREPAREE = "preparee"
    EXPEDIEE = "expediee"
    EN_TRANSIT = "en_transit"
    LIVREE = "livree"
    ECHEC = "echec"
    RETOURNEE = "retournee"


class ShipmentCarrier(str, Enum):
    """Shipment carrier enum."""
    COLISSIMO = "colissimo"
    CHRONOPOST = "chronopost"
    DHL = "dhl"
    UPS = "ups"
    FEDEX = "fedex"
    AUTRE = "autre"


class ShipmentBase(BaseModel):
    """Base schema for shipment."""
    order_id: UUID4
    carrier: Optional[ShipmentCarrier] = None
    carrier_service: Optional[str] = None


class ShipmentCreate(ShipmentBase):
    """Schema for creating shipment."""
    shipping_address: Dict[str, Any]
    notes: Optional[str] = None


class ShipmentUpdate(BaseModel):
    """Schema for updating shipment."""
    status: Optional[ShipmentStatus] = None
    tracking_number: Optional[str] = None
    carrier: Optional[ShipmentCarrier] = None
    estimated_delivery: Optional[datetime] = None
    notes: Optional[str] = None


class ShipmentResponse(ShipmentBase):
    """Schema for shipment response."""
    id: UUID4
    tracking_number: Optional[str] = None
    status: ShipmentStatus
    shipping_address: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    estimated_delivery: Optional[datetime] = None
    tracking_events: Optional[List[Dict[str, Any]]] = []
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class TrackingEvent(BaseModel):
    """Schema for tracking event."""
    timestamp: datetime
    status: str
    location: Optional[str] = None
    description: Optional[str] = None


class AddTrackingEventRequest(BaseModel):
    """Schema for add tracking event request."""
    status: str
    location: Optional[str] = None
    description: Optional[str] = None
