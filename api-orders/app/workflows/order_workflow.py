"""
Order workflow management.
"""
from typing import Optional
from app.workflows.status_transitions import OrderStatus, is_valid_transition
from app.events.handlers.order_events import publish_order_event


class OrderWorkflow:
    """Manages order workflow and status transitions."""
    
    @staticmethod
    async def validate_and_transition(
        current_status: OrderStatus,
        new_status: OrderStatus,
        order_data: dict
    ) -> tuple[bool, Optional[str]]:
        """
        Validate and execute status transition.
        
        Returns:
            Tuple of (success, error_message)
        """
        # Validate transition
        if not is_valid_transition(current_status, new_status):
            return False, f"Invalid transition from {current_status} to {new_status}"
        
        # Execute transition logic
        success = await OrderWorkflow._execute_transition(current_status, new_status, order_data)
        
        if success:
            # Publish event
            event_type = OrderWorkflow._get_event_type(new_status)
            if event_type:
                await publish_order_event(event_type, order_data)
            
            return True, None
        else:
            return False, "Failed to execute transition"
    
    @staticmethod
    async def _execute_transition(
        current_status: OrderStatus,
        new_status: OrderStatus,
        order_data: dict
    ) -> bool:
        """Execute transition-specific logic."""
        
        # Add transition-specific logic here
        if new_status == OrderStatus.VALIDEE:
            # Validation logic
            print(f"Order {order_data.get('numero')} validated")
        
        elif new_status == OrderStatus.EN_PREPARATION:
            # Start preparation
            print(f"Order {order_data.get('numero')} in preparation")
        
        elif new_status == OrderStatus.EXPEDIEE:
            # Mark as shipped
            print(f"Order {order_data.get('numero')} shipped")
        
        elif new_status == OrderStatus.LIVREE:
            # Mark as delivered
            print(f"Order {order_data.get('numero')} delivered")
        
        elif new_status == OrderStatus.ANNULEE:
            # Handle cancellation
            print(f"Order {order_data.get('numero')} cancelled")
        
        return True
    
    @staticmethod
    def _get_event_type(status: OrderStatus) -> Optional[str]:
        """Map status to event type."""
        status_event_map = {
            OrderStatus.VALIDEE: "validated",
            OrderStatus.EXPEDIEE: "shipped",
            OrderStatus.LIVREE: "delivered",
            OrderStatus.ANNULEE: "cancelled"
        }
        return status_event_map.get(status)
