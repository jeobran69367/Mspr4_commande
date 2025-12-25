"""
Saga model - Saga state management for distributed transactions.
"""
from sqlalchemy import Column, String, Enum, ForeignKey, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from app.models.base import Base


class SagaStatus(str, PyEnum):
    """Saga status enum."""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


class SagaType(str, PyEnum):
    """Saga type enum."""
    CREATE_ORDER = "create_order"
    CANCEL_ORDER = "cancel_order"
    UPDATE_ORDER = "update_order"


class SagaState(Base):
    """Saga state model for tracking distributed transactions."""
    __tablename__ = "saga_states"
    
    # Identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Saga metadata
    saga_type = Column(Enum(SagaType), nullable=False, index=True)
    saga_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Status
    status = Column(Enum(SagaStatus), default=SagaStatus.STARTED, index=True)
    
    # Step tracking
    current_step = Column(String(100), nullable=True)
    completed_steps = Column(JSON, nullable=True, default=list)
    failed_step = Column(String(100), nullable=True)
    
    # Saga data
    saga_data = Column(JSON, nullable=True)
    compensation_data = Column(JSON, nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="saga_states")
    
    def __repr__(self):
        return f"<SagaState(saga_id='{self.saga_id}', type='{self.saga_type}', status='{self.status}')>"
