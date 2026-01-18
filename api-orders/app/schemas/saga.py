"""
Pydantic schemas for sagas.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, UUID4
from enum import Enum


class SagaStatus(str, Enum):
    """Saga status enum."""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


class SagaType(str, Enum):
    """Saga type enum."""
    CREATE_ORDER = "create_order"
    CANCEL_ORDER = "cancel_order"
    UPDATE_ORDER = "update_order"


class SagaStateBase(BaseModel):
    """Base schema for saga state."""
    order_id: UUID4
    saga_type: SagaType


class SagaStateCreate(SagaStateBase):
    """Schema for creating saga state."""
    saga_data: Optional[Dict[str, Any]] = None


class SagaStateUpdate(BaseModel):
    """Schema for updating saga state."""
    status: SagaStatus
    current_step: Optional[str] = None
    error_message: Optional[str] = None


class SagaStateResponse(SagaStateBase):
    """Schema for saga state response."""
    id: UUID4
    saga_id: str
    status: SagaStatus
    current_step: Optional[str] = None
    completed_steps: Optional[List[str]] = []
    failed_step: Optional[str] = None
    saga_data: Optional[Dict[str, Any]] = None
    compensation_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SagaStepResult(BaseModel):
    """Schema for saga step result."""
    success: bool
    step_name: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
