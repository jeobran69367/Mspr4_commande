"""
OrderItem model - Line items in an order.
"""
from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.models.base import Base


class OrderItem(Base):
    """Order item model representing a line in an order."""
    __tablename__ = "order_items"
    
    # Identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Product reference (external to Product service)
    product_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    product_reference = Column(String(20), nullable=False)
    product_name = Column(String(200), nullable=False)
    product_description = Column(String(500), nullable=True)
    
    # Quantity and pricing
    quantity = Column(Integer, nullable=False)
    unit_price_ht = Column(Numeric(10, 2), nullable=False)
    tax_rate = Column(Numeric(5, 4), nullable=False, default=0.20)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0.0)
    subtotal_ht = Column(Numeric(10, 2), nullable=False)
    total_ttc = Column(Numeric(10, 2), nullable=False)
    
    # Discount
    discount_percentage = Column(Numeric(5, 2), nullable=True, default=0.0)
    discount_amount = Column(Numeric(10, 2), nullable=True, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    
    def __repr__(self):
        return f"<OrderItem(product='{self.product_name}', qty={self.quantity}, total={self.total_ttc})>"
