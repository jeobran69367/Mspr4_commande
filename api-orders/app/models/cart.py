"""
Cart model - Shopping cart before order validation.
"""
from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.models.base import Base


class Cart(Base):
    """Shopping cart model."""
    __tablename__ = "carts"
    
    # Identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Customer reference
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    customer_email = Column(String(150), nullable=True)
    
    # Session tracking
    session_id = Column(String(100), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(String(20), default="active")  # active, converted, expired, abandoned
    
    # Relationships
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Cart(customer_id='{self.customer_id}', items={len(self.items)})>"


class CartItem(Base):
    """Cart item model."""
    __tablename__ = "cart_items"
    
    # Identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = Column(UUID(as_uuid=True), ForeignKey('carts.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Product reference
    product_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    product_reference = Column(String(20), nullable=False)
    product_name = Column(String(200), nullable=False)
    
    # Quantity and price snapshot
    quantity = Column(Integer, nullable=False)
    unit_price_ht = Column(Numeric(10, 2), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cart = relationship("Cart", back_populates="items")
    
    def __repr__(self):
        return f"<CartItem(product='{self.product_name}', qty={self.quantity})>"
