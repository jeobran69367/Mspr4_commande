"""
Create payment saga step.
"""
from typing import Dict, Any
from decimal import Decimal
from uuid import UUID
from app.sagas.saga_state import SagaStepResult, SagaContext
from app.integrations.payment_gateway import PaymentGateway


async def create_payment_step(context: SagaContext) -> SagaStepResult:
    """
    Create payment for the order.
    
    Args:
        context: Saga context with payment details
        
    Returns:
        SagaStepResult with payment result
    """
    step_name = "create_payment"
    
    try:
        payment_data = context.data.get("payment", {})
        amount = Decimal(str(payment_data.get("amount")))
        currency = payment_data.get("currency", "EUR")
        payment_method = payment_data.get("method", "carte_bancaire")
        order_id = UUID(context.order_id)
        
        gateway = PaymentGateway()
        
        # Create payment intent
        result = await gateway.create_payment_intent(
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            order_id=order_id,
            metadata={
                "saga_id": context.saga_id,
                "customer_id": context.customer_id
            }
        )
        
        if not result.get("success"):
            return SagaStepResult(
                success=False,
                step_name=step_name,
                error=result.get("error_message", "Payment failed")
            )
        
        return SagaStepResult(
            success=True,
            step_name=step_name,
            data={
                "payment": {
                    "transaction_id": result.get("transaction_id"),
                    "status": result.get("status"),
                    "amount": result.get("amount")
                }
            },
            compensation_data={
                "transaction_id": result.get("transaction_id"),
                "amount": result.get("amount")
            }
        )
        
    except Exception as e:
        return SagaStepResult(
            success=False,
            step_name=step_name,
            error=str(e)
        )


async def compensate_create_payment(context: SagaContext) -> bool:
    """Compensation: Refund the payment."""
    try:
        compensation_data = context.compensation_data.get("create_payment", {})
        transaction_id = compensation_data.get("transaction_id")
        amount = compensation_data.get("amount")
        
        if not transaction_id:
            return True  # Nothing to refund
        
        gateway = PaymentGateway()
        result = await gateway.refund_payment(
            transaction_id=transaction_id,
            amount=Decimal(str(amount)) if amount else None
        )
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"Failed to compensate create_payment: {e}")
        return False
