"""
Order repository for database operations on orders.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.models.order import Order, OrderStatus, OrderSource
from app.models.order_item import OrderItem


class OrderRepository:
    """Repository for Order entity."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, order: Order) -> Order:
        """Create a new order."""
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order
    
    async def get_by_id(self, order_id: UUID) -> Optional[Order]:
        """Get order by ID with all relationships."""
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.items),
                selectinload(Order.payments),
                selectinload(Order.shipments),
                selectinload(Order.saga_states)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_numero(self, numero: str) -> Optional[Order]:
        """Get order by order number."""
        stmt = (
            select(Order)
            .where(Order.numero == numero)
            .options(
                selectinload(Order.items),
                selectinload(Order.payments),
                selectinload(Order.shipments)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_customer_id(
        self,
        customer_id: UUID,
        status: Optional[OrderStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """Get orders by customer ID with optional status filter."""
        stmt = select(Order).where(Order.customer_id == customer_id)
        
        if status:
            stmt = stmt.where(Order.status == status)
        
        stmt = stmt.order_by(Order.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def list_orders(
        self,
        status: Optional[OrderStatus] = None,
        source: Optional[OrderSource] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """List orders with optional filters."""
        stmt = select(Order)
        
        if status:
            stmt = stmt.where(Order.status == status)
        if source:
            stmt = stmt.where(Order.source == source)
        
        stmt = stmt.order_by(Order.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update(self, order: Order) -> Order:
        """Update an existing order."""
        order.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(order)
        return order
    
    async def delete(self, order_id: UUID) -> bool:
        """Delete an order by ID."""
        order = await self.get_by_id(order_id)
        if order:
            await self.session.delete(order)
            await self.session.commit()
            return True
        return False
    
    async def count_by_customer(self, customer_id: UUID) -> int:
        """Count orders for a customer."""
        stmt = select(Order).where(Order.customer_id == customer_id)
        result = await self.session.execute(stmt)
        return len(list(result.scalars().all()))
    
    async def add_item(self, order_id: UUID, item: OrderItem) -> OrderItem:
        """Add an item to an order."""
        item.order_id = order_id
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item
