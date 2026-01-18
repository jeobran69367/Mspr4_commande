"""
Validators utility for data validation.
"""
from typing import Dict, Any, List
from decimal import Decimal
from pydantic import ValidationError, field_validator
from pydantic_core import PydanticCustomError
import re


class OrderValidator:
    """Validator for order data."""
    
    @staticmethod
    def validate_address(address: Dict[str, Any]) -> tuple[bool, str]:
        """Validate address structure and content."""
        required_fields = ["ligne1", "ville", "code_postal", "pays"]
        
        for field in required_fields:
            if field not in address or not address[field]:
                return False, f"Missing required field: {field}"
        
        # Validate postal code format (French format)
        postal_code = address["code_postal"]
        if not re.match(r'^\d{5}$', postal_code):
            return False, "Invalid postal code format. Expected 5 digits."
        
        return True, "Valid address"
    
    @staticmethod
    def validate_order_items(items: List[Dict[str, Any]]) -> tuple[bool, str]:
        """Validate order items."""
        if not items:
            return False, "Order must have at least one item"
        
        for idx, item in enumerate(items):
            # Check required fields
            required_fields = ["product_id", "quantity", "unit_price_ht"]
            for field in required_fields:
                if field not in item:
                    return False, f"Item {idx}: Missing required field '{field}'"
            
            # Validate quantity
            if item["quantity"] <= 0:
                return False, f"Item {idx}: Quantity must be greater than 0"
            
            # Validate price
            if Decimal(str(item["unit_price_ht"])) < 0:
                return False, f"Item {idx}: Price cannot be negative"
        
        return True, "Valid items"
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format using simple regex."""
        # Simple email validation using regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    @staticmethod
    def validate_order_transition(
        current_status: str,
        new_status: str
    ) -> tuple[bool, str]:
        """Validate order status transition."""
        valid_transitions = {
            "panier": ["validee", "annulee"],
            "validee": ["en_attente_paiement", "en_preparation", "annulee"],
            "en_attente_paiement": ["validee", "paiement_echoue", "annulee"],
            "paiement_echoue": ["en_attente_paiement", "annulee"],
            "en_preparation": ["expediee", "annulee"],
            "expediee": ["livree", "retournee"],
            "livree": ["retournee"],
            "annulee": [],
            "retournee": []
        }
        
        if current_status not in valid_transitions:
            return False, f"Unknown current status: {current_status}"
        
        if new_status not in valid_transitions[current_status]:
            return False, f"Invalid transition from {current_status} to {new_status}"
        
        return True, "Valid transition"


class PaymentValidator:
    """Validator for payment data."""
    
    @staticmethod
    def validate_amount(amount: Decimal, order_total: Decimal) -> tuple[bool, str]:
        """Validate payment amount matches order total."""
        if amount != order_total:
            return False, f"Payment amount ({amount}) does not match order total ({order_total})"
        return True, "Valid amount"
    
    @staticmethod
    def validate_payment_method(method: str) -> bool:
        """Validate payment method."""
        valid_methods = ["carte_bancaire", "virement", "cheque", "paypal", "stripe"]
        return method in valid_methods
