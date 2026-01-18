"""
Payment Gateway integration (Simulator).
Simulates Stripe/PayPal payment processing.
"""
import httpx
from typing import Optional, Dict, Any
from decimal import Decimal
from uuid import UUID
import random
from app.config import settings
from app.utils.id_generator import generate_transaction_id


class PaymentGateway:
    """Payment Gateway client (simulator)."""
    
    def __init__(self):
        self.base_url = settings.payment_gateway_url
        self.api_key = settings.payment_gateway_api_key
        self.timeout = 15.0
    
    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        payment_method: str,
        order_id: UUID,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a payment intent.
        Simulates payment gateway response.
        """
        # In production, this would call external payment gateway
        # For now, we simulate the response
        
        transaction_id = generate_transaction_id("PAY")
        
        # Simulate 90% success rate
        success = random.random() < 0.9
        
        if success:
            return {
                "success": True,
                "transaction_id": transaction_id,
                "status": "succeeded",
                "amount": float(amount),
                "currency": currency,
                "payment_method": payment_method,
                "client_secret": f"pi_{transaction_id}_secret",
                "metadata": metadata or {}
            }
        else:
            return {
                "success": False,
                "transaction_id": transaction_id,
                "status": "failed",
                "error": "payment_declined",
                "error_message": "The payment was declined by your bank. Please try another card.",
                "metadata": metadata or {}
            }
    
    async def capture_payment(
        self,
        transaction_id: str,
        amount: Decimal
    ) -> Dict[str, Any]:
        """Capture a previously authorized payment."""
        # Simulate capture
        success = random.random() < 0.95
        
        if success:
            return {
                "success": True,
                "transaction_id": transaction_id,
                "status": "captured",
                "amount": float(amount),
                "captured_at": "2024-02-15T10:30:00Z"
            }
        else:
            return {
                "success": False,
                "transaction_id": transaction_id,
                "status": "failed",
                "error": "capture_failed",
                "error_message": "Failed to capture payment"
            }
    
    async def refund_payment(
        self,
        transaction_id: str,
        amount: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Refund a payment (full or partial)."""
        # Simulate refund
        success = random.random() < 0.95
        
        if success:
            return {
                "success": True,
                "transaction_id": transaction_id,
                "status": "refunded",
                "amount": float(amount) if amount else None,
                "refunded_at": "2024-02-15T10:30:00Z"
            }
        else:
            return {
                "success": False,
                "transaction_id": transaction_id,
                "status": "failed",
                "error": "refund_failed",
                "error_message": "Failed to refund payment"
            }
    
    async def get_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """Get payment status."""
        # Simulate status check
        return {
            "transaction_id": transaction_id,
            "status": "succeeded",
            "amount": 100.00,
            "currency": "EUR"
        }
