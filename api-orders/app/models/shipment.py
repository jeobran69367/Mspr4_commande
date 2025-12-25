"""
Shipment model - Shipment tracking for orders.
"""
from sqlalchemy import Column, String, Enum, ForeignKey, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from app.models.base import Base


class ShipmentStatus(str, PyEnum):
    """Shipment status enum."""
    EN_ATTENTE = "en_attente"
    PREPAREE = "preparee"
    EXPEDIEE = "expediee"
    EN_TRANSIT = "en_transit"
    LIVREE = "livree"
    ECHEC = "echec"
    RETOURNEE = "retournee"


class ShipmentCarrier(str, PyEnum):
    """Shipment carrier enum."""
    COLISSIMO = "colissimo"
    CHRONOPOST = "chronopost"
    DHL = "dhl"
    UPS = "ups"
    FEDEX = "fedex"
    AUTRE = "autre"


class Shipment(Base):
    """Shipment model."""
    __tablename__ = "shipments"
    
    # Identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Shipment reference
    tracking_number = Column(String(100), unique=True, nullable=True, index=True)
    
    # Carrier information
    carrier = Column(Enum(ShipmentCarrier), nullable=True)
    carrier_service = Column(String(100), nullable=True)
    
    # Status
    status = Column(Enum(ShipmentStatus), default=ShipmentStatus.EN_ATTENTE, index=True)
    
    # Shipping address
    shipping_address = Column(JSON, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    estimated_delivery = Column(DateTime, nullable=True)
    
    # Tracking events
    tracking_events = Column(JSON, nullable=True, default=list)
    
    # Metadata
    notes = Column(Text, nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="shipments")
    
    def __repr__(self):
        return f"<Shipment(tracking_number='{self.tracking_number}', status='{self.status}')>"
