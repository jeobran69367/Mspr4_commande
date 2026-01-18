"""
Create shipment saga step.
"""
from typing import Dict, Any
from uuid import UUID
from app.sagas.saga_state import SagaStepResult, SagaContext
from app.utils.id_generator import generate_tracking_number


async def create_shipment_step(context: SagaContext) -> SagaStepResult:
    """
    Create shipment for the order.
    
    Args:
        context: Saga context with shipping details
        
    Returns:
        SagaStepResult with shipment result
    """
    step_name = "create_shipment"
    
    try:
        shipping_data = context.data.get("shipping", {})
        address = shipping_data.get("address", {})
        carrier = shipping_data.get("carrier", "colissimo")
        
        # Generate tracking number
        tracking_number = generate_tracking_number(carrier.upper())
        
        shipment_data = {
            "tracking_number": tracking_number,
            "carrier": carrier,
            "address": address,
            "status": "en_attente"
        }
        
        return SagaStepResult(
            success=True,
            step_name=step_name,
            data={"shipment": shipment_data},
            compensation_data={"tracking_number": tracking_number}
        )
        
    except Exception as e:
        return SagaStepResult(
            success=False,
            step_name=step_name,
            error=str(e)
        )


async def compensate_create_shipment(context: SagaContext) -> bool:
    """Compensation: Cancel the shipment."""
    try:
        compensation_data = context.compensation_data.get("create_shipment", {})
        tracking_number = compensation_data.get("tracking_number")
        
        if tracking_number:
            print(f"Cancelling shipment: {tracking_number}")
            # Call shipment cancellation API if available
        
        return True
        
    except Exception as e:
        print(f"Failed to compensate create_shipment: {e}")
        return False
