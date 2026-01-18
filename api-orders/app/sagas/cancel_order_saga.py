"""
Cancel Order Saga - Orchestrates order cancellation workflow.
"""
from typing import Dict, Any
from uuid import UUID
from app.sagas.saga_state import SagaContext, SagaStatus
from app.sagas.steps import (
    compensate_reserve_stock,
    compensate_create_payment,
    compensate_create_shipment
)
from app.utils.id_generator import generate_saga_id


class CancelOrderSaga:
    """Saga for cancelling an order."""
    
    async def execute(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the cancel order saga.
        
        Args:
            order_data: Order data including order_id, reservations, payment, shipment
            
        Returns:
            Dict with saga result
        """
        # Initialize saga context with cancellation data
        saga_id = generate_saga_id("CANCEL_ORDER")
        context = SagaContext(
            saga_id=saga_id,
            order_id=order_data.get("order_id", ""),
            customer_id=order_data.get("customer_id", ""),
        )
        
        # Build compensation data from existing order state
        if order_data.get("reservations"):
            context.add_compensation_data("reserve_stock", {
                "reservations": order_data["reservations"]
            })
            context.completed_steps.append("reserve_stock")
        
        if order_data.get("payment"):
            context.add_compensation_data("create_payment", {
                "transaction_id": order_data["payment"].get("transaction_id"),
                "amount": order_data["payment"].get("amount")
            })
            context.completed_steps.append("create_payment")
        
        if order_data.get("shipment"):
            context.add_compensation_data("create_shipment", {
                "tracking_number": order_data["shipment"].get("tracking_number")
            })
            context.completed_steps.append("create_shipment")
        
        print(f"Starting cancel saga {saga_id} for order {context.order_id}")
        
        # Execute compensations
        all_succeeded = True
        
        if "reserve_stock" in context.completed_steps:
            success = await compensate_reserve_stock(context)
            if not success:
                all_succeeded = False
        
        if "create_payment" in context.completed_steps:
            success = await compensate_create_payment(context)
            if not success:
                all_succeeded = False
        
        if "create_shipment" in context.completed_steps:
            success = await compensate_create_shipment(context)
            if not success:
                all_succeeded = False
        
        status = SagaStatus.COMPENSATED if all_succeeded else SagaStatus.FAILED
        
        return {
            "success": all_succeeded,
            "saga_id": saga_id,
            "status": status,
            "data": context.data
        }
