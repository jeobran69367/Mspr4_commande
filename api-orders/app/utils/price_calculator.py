"""
Price calculator utility for order calculations.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any


class PriceCalculator:
    """Utility class for price calculations."""
    
    @staticmethod
    def calculate_item_total(
        unit_price_ht: Decimal,
        quantity: int,
        tax_rate: Decimal,
        discount_percentage: Decimal = Decimal("0")
    ) -> Dict[str, Decimal]:
        """
        Calculate totals for an order item.
        
        Returns:
            Dict with: subtotal_ht, discount_amount, tax_amount, total_ttc
        """
        # Calculate subtotal HT
        subtotal_ht = (unit_price_ht * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        # Calculate discount
        discount_amount = (subtotal_ht * discount_percentage / 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        
        # Calculate subtotal after discount
        subtotal_after_discount = subtotal_ht - discount_amount
        
        # Calculate tax
        tax_amount = (subtotal_after_discount * tax_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        
        # Calculate total TTC
        total_ttc = (subtotal_after_discount + tax_amount).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        
        return {
            "subtotal_ht": subtotal_ht,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "total_ttc": total_ttc
        }
    
    @staticmethod
    def calculate_order_total(
        items: List[Dict[str, Any]],
        shipping_cost_ht: Decimal,
        default_tax_rate: Decimal = Decimal("0.20")
    ) -> Dict[str, Decimal]:
        """
        Calculate totals for entire order.
        
        Returns:
            Dict with: subtotal_ht, shipping_cost_ht, total_discount, tax_amount, total_ttc
        """
        subtotal_ht = Decimal("0")
        total_discount = Decimal("0")
        tax_amount = Decimal("0")
        
        for item in items:
            item_calcs = PriceCalculator.calculate_item_total(
                unit_price_ht=Decimal(str(item.get("unit_price_ht", 0))),
                quantity=item.get("quantity", 1),
                tax_rate=Decimal(str(item.get("tax_rate", default_tax_rate))),
                discount_percentage=Decimal(str(item.get("discount_percentage", 0)))
            )
            
            subtotal_ht += item_calcs["subtotal_ht"]
            total_discount += item_calcs["discount_amount"]
            tax_amount += item_calcs["tax_amount"]
        
        # Add shipping tax
        shipping_tax = (shipping_cost_ht * default_tax_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        tax_amount += shipping_tax
        
        # Calculate total TTC
        total_ttc = (subtotal_ht - total_discount + shipping_cost_ht + tax_amount).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        
        return {
            "subtotal_ht": subtotal_ht,
            "shipping_cost_ht": shipping_cost_ht,
            "discount_amount": total_discount,
            "tax_amount": tax_amount,
            "total_ttc": total_ttc
        }
    
    @staticmethod
    def calculate_shipping_cost(
        subtotal: Decimal,
        free_shipping_threshold: Decimal = Decimal("100.00"),
        standard_shipping_cost: Decimal = Decimal("5.99")
    ) -> Decimal:
        """Calculate shipping cost based on order subtotal."""
        if subtotal >= free_shipping_threshold:
            return Decimal("0.00")
        return standard_shipping_cost
