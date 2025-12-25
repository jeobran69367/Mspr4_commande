"""
Pydantic schemas for carts.
"""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, UUID4, EmailStr


class CartItemBase(BaseModel):
    """Base schema for cart item."""
    product_id: UUID4
    product_reference: str
    product_name: str
    quantity: int = Field(gt=0)
    unit_price_ht: Decimal = Field(ge=0)


class CartItemCreate(CartItemBase):
    """Schema for creating cart item."""
    pass


class CartItemUpdate(BaseModel):
    """Schema for updating cart item."""
    quantity: int = Field(gt=0)


class CartItemResponse(CartItemBase):
    """Schema for cart item response."""
    id: UUID4
    cart_id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CartBase(BaseModel):
    """Base schema for cart."""
    customer_id: UUID4
    customer_email: Optional[EmailStr] = None


class CartCreate(CartBase):
    """Schema for creating cart."""
    session_id: Optional[str] = None


class CartResponse(CartBase):
    """Schema for cart response."""
    id: UUID4
    session_id: Optional[str] = None
    is_active: str
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    items: List[CartItemResponse] = []
    
    class Config:
        from_attributes = True


class AddToCartRequest(BaseModel):
    """Schema for add to cart request."""
    product_id: UUID4
    product_reference: str
    product_name: str
    quantity: int = Field(gt=0)
    unit_price_ht: Decimal = Field(ge=0)


class UpdateCartItemRequest(BaseModel):
    """Schema for update cart item request."""
    quantity: int = Field(gt=0)


class CartSummary(BaseModel):
    """Schema for cart summary."""
    cart_id: UUID4
    total_items: int
    subtotal_ht: Decimal
    estimated_tax: Decimal
    estimated_total_ttc: Decimal
    
    class Config:
        from_attributes = True
