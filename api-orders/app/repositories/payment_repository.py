"""
Payment repository for database operations on payments.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.payment import Payment, PaymentStatus


class PaymentRepository:
    """Repository for Payment entity."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, payment: Payment) -> Payment:
        """Create a new payment."""
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment
    
    async def get_by_id(self, payment_id: UUID) -> Optional[Payment]:
        """Get payment by ID."""
        stmt = select(Payment).where(Payment.id == payment_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_transaction_id(self, transaction_id: str) -> Optional[Payment]:
        """Get payment by transaction ID."""
        stmt = select(Payment).where(Payment.transaction_id == transaction_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_order_id(self, order_id: UUID) -> List[Payment]:
        """Get all payments for an order."""
        stmt = (
            select(Payment)
            .where(Payment.order_id == order_id)
            .order_by(Payment.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def list_payments(
        self,
        status: Optional[PaymentStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """List payments with optional filters."""
        stmt = select(Payment)
        
        if status:
            stmt = stmt.where(Payment.status == status)
        
        stmt = stmt.order_by(Payment.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update(self, payment: Payment) -> Payment:
        """Update an existing payment."""
        payment.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(payment)
        return payment
    
    async def delete(self, payment_id: UUID) -> bool:
        """Delete a payment by ID."""
        payment = await self.get_by_id(payment_id)
        if payment:
            await self.session.delete(payment)
            await self.session.commit()
            return True
        return False
