"""
Pydantic schemas for orders.
"""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, UUID4, EmailStr
from enum import Enum


class OrderStatus(str, Enum):
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


class OrderSource(str, Enum):
    """Order source enum."""
    WEB = "web"
    DISTRIBUTEUR = "distributeur"
    TELEPHONE = "telephone"
    BOUTIQUE = "boutique"


class PaymentMethod(str, Enum):
    """Payment method enum."""
    CARTE_BANCAIRE = "carte_bancaire"
    VIREMENT = "virement"
    CHEQUE = "cheque"
    PAYPAL = "paypal"
    STRIPE = "stripe"


class PaymentStatus(str, Enum):
    """Payment status enum."""
    EN_ATTENTE = "en_attente"
    PAYE = "paye"
    ECHEC = "echec"
    REMBOURSE = "rembourse"
    PARTIEL = "partiel"


class AddressSchema(BaseModel):
    """Address schema."""
    ligne1: str
    ligne2: Optional[str] = None
    ville: str
    code_postal: str
    pays: str = "France"
    
    class Config:
        from_attributes = True


class OrderItemBase(BaseModel):
    """Base schema for order item."""
    product_id: UUID4
    product_reference: str
    product_name: str
    product_description: Optional[str] = None
    quantity: int = Field(gt=0)
    unit_price_ht: Decimal = Field(ge=0)
    tax_rate: Decimal = Field(default=Decimal("0.20"), ge=0, le=1)
    discount_percentage: Optional[Decimal] = Field(default=Decimal("0"), ge=0, le=100)


class OrderItemCreate(OrderItemBase):
    """Schema for creating order item."""
    pass


class OrderItemUpdate(BaseModel):
    """Schema for updating order item."""
    quantity: Optional[int] = Field(default=None, gt=0)
    discount_percentage: Optional[Decimal] = Field(default=None, ge=0, le=100)


class OrderItemResponse(OrderItemBase):
    """Schema for order item response."""
    id: UUID4
    order_id: UUID4
    tax_amount: Decimal
    subtotal_ht: Decimal
    total_ttc: Decimal
    discount_amount: Decimal
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """Base schema for order."""
    customer_id: UUID4
    customer_email: EmailStr
    shipping_address: AddressSchema
    billing_address: AddressSchema
    notes: Optional[str] = None
    source: OrderSource = OrderSource.WEB


class OrderCreate(OrderBase):
    """Schema for creating order."""
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    """Schema for updating order."""
    shipping_address: Optional[AddressSchema] = None
    billing_address: Optional[AddressSchema] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    status: OrderStatus
    notes: Optional[str] = None


class OrderResponse(OrderBase):
    """Schema for order response."""
    id: UUID4
    numero: str
    customer_reference: str
    customer_nom_complet: str
    status: OrderStatus
    payment_status: PaymentStatus
    subtotal_ht: Decimal
    shipping_cost_ht: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_ttc: Decimal
    payment_method: Optional[PaymentMethod] = None
    currency: str
    internal_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    validated_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Schema for order list response."""
    orders: List[OrderResponse]
    total: int
    page: int
    per_page: int
    
    class Config:
        from_attributes = True
