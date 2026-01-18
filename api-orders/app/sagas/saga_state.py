"""
Saga state management.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class SagaStatus(str, Enum):
    """Saga status enum."""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


@dataclass
class SagaContext:
    """Context data passed through saga steps."""
    saga_id: str
    order_id: str
    customer_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    completed_steps: List[str] = field(default_factory=list)
    compensation_data: Dict[str, Any] = field(default_factory=dict)
    
    def add_step_data(self, step_name: str, data: Dict[str, Any]):
        """Add data from a completed step."""
        self.data[step_name] = data
        if step_name not in self.completed_steps:
            self.completed_steps.append(step_name)
    
    def add_compensation_data(self, step_name: str, data: Dict[str, Any]):
        """Add compensation data for a step."""
        self.compensation_data[step_name] = data
    
    def get_step_data(self, step_name: str) -> Optional[Dict[str, Any]]:
        """Get data from a specific step."""
        return self.data.get(step_name)


@dataclass
class SagaStepResult:
    """Result of a saga step execution."""
    success: bool
    step_name: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    compensation_data: Optional[Dict[str, Any]] = None
