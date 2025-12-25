"""
Create Order Saga - Orchestrates order creation workflow.
"""
from typing import Dict, Any, List
from uuid import UUID
from app.sagas.saga_state import SagaContext, SagaStepResult, SagaStatus
from app.sagas.steps import (
    validate_customer_step,
    reserve_stock_step,
    create_payment_step,
    create_shipment_step,
    compensate_saga
)
from app.utils.id_generator import generate_saga_id


class CreateOrderSaga:
    """Saga for creating an order with distributed transaction management."""
    
    def __init__(self):
        self.steps = [
            validate_customer_step,
            reserve_stock_step,
            create_payment_step,
            create_shipment_step
        ]
    
    async def execute(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the create order saga.
        
        Args:
            order_data: Order creation data including customer_id, items, payment, shipping
            
        Returns:
            Dict with saga result: {success, saga_id, data, error}
        """
        # Initialize saga context
        saga_id = generate_saga_id("CREATE_ORDER")
        context = SagaContext(
            saga_id=saga_id,
            order_id=order_data.get("order_id", ""),
            customer_id=order_data.get("customer_id", ""),
            data={
                "order_items": order_data.get("items", []),
                "payment": order_data.get("payment", {}),
                "shipping": order_data.get("shipping", {})
            }
        )
        
        print(f"Starting saga {saga_id} for order {context.order_id}")
        
        # Execute steps sequentially
        for step_func in self.steps:
            step_result: SagaStepResult = await step_func(context)
            
            if step_result.success:
                # Store step data
                if step_result.data:
                    context.add_step_data(step_result.step_name, step_result.data)
                
                # Store compensation data
                if step_result.compensation_data:
                    context.add_compensation_data(
                        step_result.step_name,
                        step_result.compensation_data
                    )
                
                print(f"Saga {saga_id}: Step {step_result.step_name} completed")
            else:
                # Step failed - start compensation
                print(f"Saga {saga_id}: Step {step_result.step_name} failed: {step_result.error}")
                
                # Execute compensation for completed steps
                compensation_success = await compensate_saga(context)
                
                return {
                    "success": False,
                    "saga_id": saga_id,
                    "status": SagaStatus.COMPENSATED if compensation_success else SagaStatus.FAILED,
                    "failed_step": step_result.step_name,
                    "error": step_result.error,
                    "compensation_success": compensation_success
                }
        
        # All steps completed successfully
        print(f"Saga {saga_id} completed successfully")
        
        return {
            "success": True,
            "saga_id": saga_id,
            "status": SagaStatus.COMPLETED,
            "data": context.data
        }
