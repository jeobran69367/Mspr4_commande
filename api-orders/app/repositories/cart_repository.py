"""
Cart repository for database operations on carts.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.models.cart import Cart, CartItem


class CartRepository:
    """Repository for Cart entity."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, cart: Cart) -> Cart:
        """Create a new cart."""
        self.session.add(cart)
        await self.session.commit()
        await self.session.refresh(cart)
        return cart
    
    async def get_by_id(self, cart_id: UUID) -> Optional[Cart]:
        """Get cart by ID with items."""
        stmt = (
            select(Cart)
            .where(Cart.id == cart_id)
            .options(selectinload(Cart.items))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_customer_id(self, customer_id: UUID) -> Optional[Cart]:
        """Get active cart for a customer."""
        stmt = (
            select(Cart)
            .where(Cart.customer_id == customer_id, Cart.is_active == "active")
            .options(selectinload(Cart.items))
            .order_by(Cart.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_session_id(self, session_id: str) -> Optional[Cart]:
        """Get cart by session ID."""
        stmt = (
            select(Cart)
            .where(Cart.session_id == session_id, Cart.is_active == "active")
            .options(selectinload(Cart.items))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update(self, cart: Cart) -> Cart:
        """Update an existing cart."""
        cart.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(cart)
        return cart
    
    async def delete(self, cart_id: UUID) -> bool:
        """Delete a cart by ID."""
        cart = await self.get_by_id(cart_id)
        if cart:
            await self.session.delete(cart)
            await self.session.commit()
            return True
        return False
    
    async def add_item(self, cart_id: UUID, item: CartItem) -> CartItem:
        """Add an item to a cart."""
        item.cart_id = cart_id
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item
    
    async def update_item(self, item: CartItem) -> CartItem:
        """Update a cart item."""
        item.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(item)
        return item
    
    async def remove_item(self, item_id: UUID) -> bool:
        """Remove an item from a cart."""
        stmt = select(CartItem).where(CartItem.id == item_id)
        result = await self.session.execute(stmt)
        item = result.scalar_one_or_none()
        
        if item:
            await self.session.delete(item)
            await self.session.commit()
            return True
        return False
    
    async def clear_cart(self, cart_id: UUID) -> bool:
        """Clear all items from a cart."""
        cart = await self.get_by_id(cart_id)
        if cart:
            for item in cart.items:
                await self.session.delete(item)
            await self.session.commit()
            return True
        return False
