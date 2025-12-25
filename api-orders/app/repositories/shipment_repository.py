"""
Shipment repository for database operations on shipments.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.shipment import Shipment, ShipmentStatus


class ShipmentRepository:
    """Repository for Shipment entity."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, shipment: Shipment) -> Shipment:
        """Create a new shipment."""
        self.session.add(shipment)
        await self.session.commit()
        await self.session.refresh(shipment)
        return shipment
    
    async def get_by_id(self, shipment_id: UUID) -> Optional[Shipment]:
        """Get shipment by ID."""
        stmt = select(Shipment).where(Shipment.id == shipment_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_tracking_number(self, tracking_number: str) -> Optional[Shipment]:
        """Get shipment by tracking number."""
        stmt = select(Shipment).where(Shipment.tracking_number == tracking_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_order_id(self, order_id: UUID) -> List[Shipment]:
        """Get all shipments for an order."""
        stmt = (
            select(Shipment)
            .where(Shipment.order_id == order_id)
            .order_by(Shipment.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def list_shipments(
        self,
        status: Optional[ShipmentStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Shipment]:
        """List shipments with optional filters."""
        stmt = select(Shipment)
        
        if status:
            stmt = stmt.where(Shipment.status == status)
        
        stmt = stmt.order_by(Shipment.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update(self, shipment: Shipment) -> Shipment:
        """Update an existing shipment."""
        shipment.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(shipment)
        return shipment
    
    async def delete(self, shipment_id: UUID) -> bool:
        """Delete a shipment by ID."""
        shipment = await self.get_by_id(shipment_id)
        if shipment:
            await self.session.delete(shipment)
            await self.session.commit()
            return True
        return False
