"""
Reserve stock saga step.
"""
from typing import Dict, Any, List
from uuid import UUID
from app.sagas.saga_state import SagaStepResult, SagaContext
from app.integrations.product_client import ProductClient


async def reserve_stock_step(context: SagaContext) -> SagaStepResult:
    """
    Reserve stock for all order items.
    
    Args:
        context: Saga context with order items
        
    Returns:
        SagaStepResult with reservation result
    """
    step_name = "reserve_stock"
    
    try:
        order_items = context.data.get("order_items", [])
        order_id = UUID(context.order_id)
        client = ProductClient()
        
        reservations = []
        
        # Reserve stock for each item
        for item in order_items:
            product_id = UUID(item["product_id"])
            quantity = item["quantity"]
            
            # Check availability first
            is_available = await client.check_stock_availability(product_id, quantity)
            
            if not is_available:
                # Release any reservations made so far
                for reservation in reservations:
                    await client.release_stock(
                        UUID(reservation["product_id"]),
                        reservation["quantity"],
                        order_id
                    )
                
                return SagaStepResult(
                    success=False,
                    step_name=step_name,
                    error=f"Insufficient stock for product {product_id}"
                )
            
            # Reserve stock
            reservation_id = await client.reserve_stock(product_id, quantity, order_id)
            
            if not reservation_id:
                # Release any reservations made so far
                for reservation in reservations:
                    await client.release_stock(
                        UUID(reservation["product_id"]),
                        reservation["quantity"],
                        order_id
                    )
                
                return SagaStepResult(
                    success=False,
                    step_name=step_name,
                    error=f"Failed to reserve stock for product {product_id}"
                )
            
            reservations.append({
                "product_id": str(product_id),
                "quantity": quantity,
                "reservation_id": reservation_id
            })
        
        return SagaStepResult(
            success=True,
            step_name=step_name,
            data={"reservations": reservations},
            compensation_data={"reservations": reservations}
        )
        
    except Exception as e:
        return SagaStepResult(
            success=False,
            step_name=step_name,
            error=str(e)
        )


async def compensate_reserve_stock(context: SagaContext) -> bool:
    """Compensation: Release reserved stock."""
    try:
        compensation_data = context.compensation_data.get("reserve_stock", {})
        reservations = compensation_data.get("reservations", [])
        order_id = UUID(context.order_id)
        client = ProductClient()
        
        for reservation in reservations:
            product_id = UUID(reservation["product_id"])
            quantity = reservation["quantity"]
            await client.release_stock(product_id, quantity, order_id)
        
        return True
    except Exception as e:
        print(f"Failed to compensate reserve_stock: {e}")
        return False
