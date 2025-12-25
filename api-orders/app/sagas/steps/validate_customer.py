"""
Validate customer saga step.
"""
from typing import Dict, Any
from uuid import UUID
from app.sagas.saga_state import SagaStepResult, SagaContext
from app.integrations.customer_client import CustomerClient


async def validate_customer_step(context: SagaContext) -> SagaStepResult:
    """
    Validate customer exists and is active.
    
    Args:
        context: Saga context with customer_id
        
    Returns:
        SagaStepResult with validation result
    """
    step_name = "validate_customer"
    
    try:
        customer_id = UUID(context.customer_id)
        client = CustomerClient()
        
        # Validate customer
        is_valid = await client.validate_customer(customer_id)
        
        if not is_valid:
            return SagaStepResult(
                success=False,
                step_name=step_name,
                error="Customer not found or inactive"
            )
        
        # Get customer details
        customer = await client.get_customer(customer_id)
        
        return SagaStepResult(
            success=True,
            step_name=step_name,
            data={"customer": customer}
        )
        
    except Exception as e:
        return SagaStepResult(
            success=False,
            step_name=step_name,
            error=str(e)
        )


async def compensate_validate_customer(context: SagaContext) -> bool:
    """Compensation for validate customer step (no action needed)."""
    # No compensation needed for validation
    return True
