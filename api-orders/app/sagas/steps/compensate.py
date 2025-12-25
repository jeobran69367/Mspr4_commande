"""
Compensation orchestration for saga steps.
"""
from typing import List, Callable, Dict
from app.sagas.saga_state import SagaContext
from app.sagas.steps.validate_customer import compensate_validate_customer
from app.sagas.steps.reserve_stock import compensate_reserve_stock
from app.sagas.steps.create_payment import compensate_create_payment
from app.sagas.steps.create_shipment import compensate_create_shipment


# Map step names to compensation functions
COMPENSATION_FUNCTIONS: Dict[str, Callable] = {
    "validate_customer": compensate_validate_customer,
    "reserve_stock": compensate_reserve_stock,
    "create_payment": compensate_create_payment,
    "create_shipment": compensate_create_shipment,
}


async def compensate_saga(context: SagaContext) -> bool:
    """
    Execute compensation for all completed steps in reverse order.
    
    Args:
        context: Saga context with completed steps
        
    Returns:
        True if all compensations succeeded, False otherwise
    """
    print(f"Starting compensation for saga {context.saga_id}")
    
    # Reverse the order of completed steps
    steps_to_compensate = list(reversed(context.completed_steps))
    
    all_succeeded = True
    
    for step_name in steps_to_compensate:
        compensation_func = COMPENSATION_FUNCTIONS.get(step_name)
        
        if compensation_func:
            print(f"Compensating step: {step_name}")
            success = await compensation_func(context)
            
            if not success:
                print(f"Compensation failed for step: {step_name}")
                all_succeeded = False
            else:
                print(f"Compensation succeeded for step: {step_name}")
        else:
            print(f"No compensation function found for step: {step_name}")
    
    return all_succeeded
