"""
Order model - Main order entity with complete workflow.
"""
from sqlalchemy import Column, String, Numeric, Enum, DateTime, JSON, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from app.models.base import Base


class OrderStatus(str, PyEnum):
    """Order status enum."""
    PANIER = "panier"
    VALIDEE = "validee"
    EN_PREPARATION = "en_preparation"
    EXPEDIEE = "expediee"
    LIVREE = "livree"
    ANNULEE = "annulee"
    RETOURNEE = "retournee"
    EN_ATTENTE_PAIEMENT = "en_attente_paiement"
    PAIEMENT_ECHOUE = "paiement_echoue"


class OrderSource(str, PyEnum):
    """Order source enum."""
    WEB = "web"
    DISTRIBUTEUR = "distributeur"
    TELEPHONE = "telephone"
    BOUTIQUE = "boutique"


class PaymentMethod(str, PyEnum):
    """Payment method enum."""
    CARTE_BANCAIRE = "carte_bancaire"
    VIREMENT = "virement"
    CHEQUE = "cheque"
    PAYPAL = "paypal"
    STRIPE = "stripe"


class PaymentStatus(str, PyEnum):
    """Payment status enum."""
    EN_ATTENTE = "en_attente"
    PAYE = "paye"
    ECHEC = "echec"
    REMBOURSE = "rembourse"
    PARTIEL = "partiel"


class Order(Base):
    """Order model with complete workflow support."""
    __tablename__ = "orders"
    
    # Identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(50), unique=True, nullable=False, index=True)
    
    # Customer (external reference to Customer service)
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    customer_reference = Column(String(20), nullable=False, index=True)
    customer_email = Column(String(150), nullable=False, index=True)
    customer_nom_complet = Column(String(201), nullable=False)
    
    # Addresses (snapshot at order time)
    shipping_address = Column(JSON, nullable=False)
    billing_address = Column(JSON, nullable=False)
    
    # Important dates
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    validated_at = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Status
    status = Column(Enum(OrderStatus), default=OrderStatus.PANIER, index=True)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.EN_ATTENTE, index=True)
    
    # Financial information
    subtotal_ht = Column(Numeric(10, 2), nullable=False, default=0.0)
    shipping_cost_ht = Column(Numeric(8, 2), nullable=False, default=0.0)
    discount_amount = Column(Numeric(8, 2), nullable=False, default=0.0)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0.0)
    total_ttc = Column(Numeric(10, 2), nullable=False, default=0.0)
    
    # Metadata
    source = Column(Enum(OrderSource), default=OrderSource.WEB)
    payment_method = Column(Enum(PaymentMethod), nullable=True)
    currency = Column(String(3), default="EUR")
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="order", cascade="all, delete-orphan")
    saga_states = relationship("SagaState", back_populates="order", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_order_customer_status', 'customer_id', 'status'),
        Index('idx_order_number', 'numero'),
        Index('idx_order_dates', 'created_at', 'status'),
    )
    
    def __repr__(self):
        return f"<Order(numero='{self.numero}', status='{self.status}', total={self.total_ttc})>"
