"""
Saga repository for database operations on saga states.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.saga import SagaState, SagaStatus, SagaType


class SagaRepository:
    """Repository for SagaState entity."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, saga_state: SagaState) -> SagaState:
        """Create a new saga state."""
        self.session.add(saga_state)
        await self.session.commit()
        await self.session.refresh(saga_state)
        return saga_state
    
    async def get_by_id(self, saga_state_id: UUID) -> Optional[SagaState]:
        """Get saga state by ID."""
        stmt = select(SagaState).where(SagaState.id == saga_state_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_saga_id(self, saga_id: str) -> Optional[SagaState]:
        """Get saga state by saga ID."""
        stmt = select(SagaState).where(SagaState.saga_id == saga_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_order_id(self, order_id: UUID) -> List[SagaState]:
        """Get all saga states for an order."""
        stmt = (
            select(SagaState)
            .where(SagaState.order_id == order_id)
            .order_by(SagaState.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def list_sagas(
        self,
        saga_type: Optional[SagaType] = None,
        status: Optional[SagaStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[SagaState]:
        """List saga states with optional filters."""
        stmt = select(SagaState)
        
        if saga_type:
            stmt = stmt.where(SagaState.saga_type == saga_type)
        if status:
            stmt = stmt.where(SagaState.status == status)
        
        stmt = stmt.order_by(SagaState.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update(self, saga_state: SagaState) -> SagaState:
        """Update an existing saga state."""
        saga_state.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(saga_state)
        return saga_state
    
    async def delete(self, saga_state_id: UUID) -> bool:
        """Delete a saga state by ID."""
        saga_state = await self.get_by_id(saga_state_id)
        if saga_state:
            await self.session.delete(saga_state)
            await self.session.commit()
            return True
        return False
