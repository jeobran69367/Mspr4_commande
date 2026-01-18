"""
Pydantic schemas for payments.
"""
from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, UUID4
from enum import Enum


class PaymentStatus(str, Enum):
    """Payment status enum."""
    EN_ATTENTE = "en_attente"
    PAYE = "paye"
    ECHEC = "echec"
    REMBOURSE = "rembourse"
    PARTIEL = "partiel"
    EN_COURS = "en_cours"


class PaymentMethod(str, Enum):
    """Payment method enum."""
    CARTE_BANCAIRE = "carte_bancaire"
    VIREMENT = "virement"
    CHEQUE = "cheque"
    PAYPAL = "paypal"
    STRIPE = "stripe"


class PaymentBase(BaseModel):
    """Base schema for payment."""
    order_id: UUID4
    amount: Decimal = Field(ge=0)
    currency: str = "EUR"
    method: PaymentMethod


class PaymentCreate(PaymentBase):
    """Schema for creating payment."""
    external_reference: Optional[str] = None
    notes: Optional[str] = None


class PaymentUpdate(BaseModel):
    """Schema for updating payment."""
    status: PaymentStatus
    external_reference: Optional[str] = None
    error_message: Optional[str] = None


class PaymentResponse(PaymentBase):
    """Schema for payment response."""
    id: UUID4
    transaction_id: str
    external_reference: Optional[str] = None
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime] = None
    error_message: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class PaymentIntentRequest(BaseModel):
    """Schema for payment intent request."""
    order_id: UUID4
    method: PaymentMethod
    return_url: Optional[str] = None


class PaymentIntentResponse(BaseModel):
    """Schema for payment intent response."""
    payment_id: UUID4
    transaction_id: str
    amount: Decimal
    currency: str
    status: PaymentStatus
    client_secret: Optional[str] = None
    redirect_url: Optional[str] = None
