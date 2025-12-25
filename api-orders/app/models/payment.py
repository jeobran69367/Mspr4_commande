"""
Payment model - Payment transactions for orders.
"""
from sqlalchemy import Column, String, Numeric, Enum, ForeignKey, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from app.models.base import Base


class PaymentStatus(str, PyEnum):
    """Payment status enum."""
    EN_ATTENTE = "en_attente"
    PAYE = "paye"
    ECHEC = "echec"
    REMBOURSE = "rembourse"
    PARTIEL = "partiel"
    EN_COURS = "en_cours"


class PaymentMethod(str, PyEnum):
    """Payment method enum."""
    CARTE_BANCAIRE = "carte_bancaire"
    VIREMENT = "virement"
    CHEQUE = "cheque"
    PAYPAL = "paypal"
    STRIPE = "stripe"


class Payment(Base):
    """Payment model."""
    __tablename__ = "payments"
    
    # Identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Payment reference
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    external_reference = Column(String(100), nullable=True)
    
    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="EUR")
    method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.EN_ATTENTE, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
    
    # Payment gateway response
    gateway_response = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(transaction_id='{self.transaction_id}', amount={self.amount}, status='{self.status}')>"
