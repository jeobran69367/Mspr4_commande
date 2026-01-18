"""
Cart service - Business logic for shopping carts.
"""
from typing import Optional
from uuid import UUID
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart, CartItem
from app.repositories.cart_repository import CartRepository
from app.schemas.cart import CartCreate, AddToCartRequest, UpdateCartItemRequest
from app.utils.price_calculator import PriceCalculator
from app.config import settings


class CartService:
    """Service for cart business logic."""
    
    def __init__(self, session: AsyncSession):
        self.repository = CartRepository(session)
        self.session = session
    
    async def get_or_create_cart(self, customer_id: UUID, session_id: Optional[str] = None) -> Cart:
        """Get existing active cart or create new one."""
        cart = await self.repository.get_by_customer_id(customer_id)
        
        if not cart:
            # Create new cart
            cart = Cart(
                customer_id=customer_id,
                session_id=session_id,
                is_active="active",
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            cart = await self.repository.create(cart)
        
        return cart
    
    async def add_item(
        self,
        customer_id: UUID,
        add_item_request: AddToCartRequest
    ) -> Cart:
        """Add item to cart."""
        cart = await self.get_or_create_cart(customer_id)
        
        # Check if item already exists in cart
        existing_item = None
        for item in cart.items:
            if item.product_id == add_item_request.product_id:
                existing_item = item
                break
        
        if existing_item:
            # Update quantity
            existing_item.quantity += add_item_request.quantity
            await self.repository.update_item(existing_item)
        else:
            # Add new item
            new_item = CartItem(
                cart_id=cart.id,
                product_id=add_item_request.product_id,
                product_reference=add_item_request.product_reference,
                product_name=add_item_request.product_name,
                quantity=add_item_request.quantity,
                unit_price_ht=add_item_request.unit_price_ht
            )
            await self.repository.add_item(cart.id, new_item)
        
        # Refresh cart
        return await self.repository.get_by_id(cart.id)
    
    async def update_item(
        self,
        customer_id: UUID,
        item_id: UUID,
        update_request: UpdateCartItemRequest
    ) -> Optional[Cart]:
        """Update cart item quantity."""
        cart = await self.repository.get_by_customer_id(customer_id)
        if not cart:
            return None
        
        # Find item
        item = None
        for cart_item in cart.items:
            if cart_item.id == item_id:
                item = cart_item
                break
        
        if not item:
            return None
        
        # Update quantity
        item.quantity = update_request.quantity
        await self.repository.update_item(item)
        
        return await self.repository.get_by_id(cart.id)
    
    async def remove_item(self, customer_id: UUID, item_id: UUID) -> Optional[Cart]:
        """Remove item from cart."""
        cart = await self.repository.get_by_customer_id(customer_id)
        if not cart:
            return None
        
        await self.repository.remove_item(item_id)
        
        return await self.repository.get_by_id(cart.id)
    
    async def clear_cart(self, customer_id: UUID) -> Optional[Cart]:
        """Clear all items from cart."""
        cart = await self.repository.get_by_customer_id(customer_id)
        if not cart:
            return None
        
        await self.repository.clear_cart(cart.id)
        
        return await self.repository.get_by_id(cart.id)
    
    async def get_cart_summary(self, customer_id: UUID) -> dict:
        """Get cart summary with totals."""
        cart = await self.repository.get_by_customer_id(customer_id)
        
        if not cart or not cart.items:
            return {
                "cart_id": None,
                "total_items": 0,
                "subtotal_ht": Decimal("0"),
                "estimated_tax": Decimal("0"),
                "estimated_total_ttc": Decimal("0")
            }
        
        subtotal_ht = Decimal("0")
        for item in cart.items:
            subtotal_ht += item.unit_price_ht * item.quantity
        
        estimated_tax = subtotal_ht * Decimal(str(settings.default_tax_rate))
        estimated_total_ttc = subtotal_ht + estimated_tax
        
        return {
            "cart_id": cart.id,
            "total_items": len(cart.items),
            "subtotal_ht": subtotal_ht,
            "estimated_tax": estimated_tax,
            "estimated_total_ttc": estimated_total_ttc
        }
