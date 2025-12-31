"""
Order service - Business logic for orders.
"""
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.order_item import OrderItem
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderUpdate
from app.utils.id_generator import generate_order_number
from app.utils.price_calculator import PriceCalculator
from app.utils.validators import OrderValidator
from app.config import settings


class OrderService:
    """Service for order business logic."""
    
    def __init__(self, session: AsyncSession):
        self.repository = OrderRepository(session)
        self.session = session
    
    async def create_order(self, order_data: OrderCreate, customer_info: dict) -> Order:
        """Create a new order."""
        # Validate order data
        is_valid, error = OrderValidator.validate_order_items(
            [item.dict() for item in order_data.items]
        )
        if not is_valid:
            raise ValueError(error)
        
        # Validate addresses
        is_valid, error = OrderValidator.validate_address(order_data.shipping_address.dict())
        if not is_valid:
            raise ValueError(f"Invalid shipping address: {error}")
        
        is_valid, error = OrderValidator.validate_address(order_data.billing_address.dict())
        if not is_valid:
            raise ValueError(f"Invalid billing address: {error}")
        
        # Generate order number
        order_numero = generate_order_number(settings.order_prefix)
        
        # Calculate totals
        items_data = [item.dict() for item in order_data.items]
        shipping_cost = PriceCalculator.calculate_shipping_cost(
            Decimal("0"),  # Will be calculated below
            settings.free_shipping_threshold,
            settings.standard_shipping_cost
        )
        
        totals = PriceCalculator.calculate_order_total(
            items_data,
            shipping_cost,
            Decimal(str(settings.default_tax_rate))
        )
        
        # Create order
        order = Order(
            numero=order_numero,
            customer_id=order_data.customer_id,
            customer_reference=customer_info.get("reference", ""),
            customer_email=order_data.customer_email,
            customer_nom_complet=customer_info.get("nom_complet", ""),
            shipping_address=order_data.shipping_address.dict(),
            billing_address=order_data.billing_address.dict(),
            status=OrderStatus.PANIER,
            payment_status=PaymentStatus.EN_ATTENTE,
            subtotal_ht=totals["subtotal_ht"],
            shipping_cost_ht=totals["shipping_cost_ht"],
            discount_amount=totals["discount_amount"],
            tax_amount=totals["tax_amount"],
            total_ttc=totals["total_ttc"],
            source=order_data.source,
            notes=order_data.notes
        )
        
        # Create order in database
        order = await self.repository.create(order)
        
        # Add items
        for item_data in order_data.items:
            item_totals = PriceCalculator.calculate_item_total(
                item_data.unit_price_ht,
                item_data.quantity,
                item_data.tax_rate,
                item_data.discount_percentage or Decimal("0")
            )
            
            item = OrderItem(
                order_id=order.id,
                product_id=item_data.product_id,
                product_reference=item_data.product_reference,
                product_name=item_data.product_name,
                product_description=item_data.product_description,
                quantity=item_data.quantity,
                unit_price_ht=item_data.unit_price_ht,
                tax_rate=item_data.tax_rate,
                tax_amount=item_totals["tax_amount"],
                subtotal_ht=item_totals["subtotal_ht"],
                total_ttc=item_totals["total_ttc"],
                discount_percentage=item_data.discount_percentage or Decimal("0"),
                discount_amount=item_totals["discount_amount"]
            )
            
            await self.repository.add_item(order.id, item)
        
        # Refresh to get items
        return await self.repository.get_by_id(order.id)
    
    async def get_order(self, order_id: UUID) -> Optional[Order]:
        """Get order by ID."""
        return await self.repository.get_by_id(order_id)
    
    async def get_order_by_numero(self, numero: str) -> Optional[Order]:
        """Get order by order number."""
        return await self.repository.get_by_numero(numero)
    
    async def list_orders(
        self,
        customer_id: Optional[UUID] = None,
        status: Optional[OrderStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """List orders with filters."""
        if customer_id:
            return await self.repository.get_by_customer_id(customer_id, status, skip, limit)
        return await self.repository.list_orders(status, None, skip, limit)
    
    async def update_order(self, order_id: UUID, order_update: OrderUpdate) -> Optional[Order]:
        """Update order."""
        order = await self.repository.get_by_id(order_id)
        if not order:
            return None
        
        if order_update.shipping_address:
            order.shipping_address = order_update.shipping_address.dict()
        if order_update.billing_address:
            order.billing_address = order_update.billing_address.dict()
        if order_update.notes is not None:
            order.notes = order_update.notes
        if order_update.internal_notes is not None:
            order.internal_notes = order_update.internal_notes
        
        return await self.repository.update(order)
    
    async def update_order_status(
        self,
        order_id: UUID,
        new_status: OrderStatus,
        notes: Optional[str] = None
    ) -> Optional[Order]:
        """Update order status."""
        order = await self.repository.get_by_id(order_id)
        if not order:
            return None
        
        # Validate transition
        is_valid, error = OrderValidator.validate_order_transition(
            order.status.value,
            new_status.value
        )
        if not is_valid:
            raise ValueError(error)
        
        # Update status and timestamps
        order.status = new_status
        
        if new_status == OrderStatus.VALIDEE:
            order.validated_at = datetime.utcnow()
        elif new_status == OrderStatus.EXPEDIEE:
            order.shipped_at = datetime.utcnow()
        elif new_status == OrderStatus.LIVREE:
            order.delivered_at = datetime.utcnow()
        elif new_status == OrderStatus.ANNULEE:
            order.cancelled_at = datetime.utcnow()
        
        if notes:
            order.internal_notes = (order.internal_notes or "") + f"\n{notes}"
        
        return await self.repository.update(order)
    
    async def cancel_order(self, order_id: UUID, reason: Optional[str] = None) -> Optional[Order]:
        """Cancel an order."""
        return await self.update_order_status(order_id, OrderStatus.ANNULEE, reason)
    

import pytest
from app.services.order_service import OrderService

@pytest.mark.asyncio
async def test_create_order():
    service = OrderService()
    order_data = {
        "customer_id": "12345",
        "items": [
            {"product_id": "67890", "quantity": 2, "unit_price_ht": 25.00}
        ]
    }
    order = await service.create_order(order_data)
    assert order.customer_id == "12345"
    assert len(order.items) == 1

@pytest.mark.asyncio
async def test_get_order():
    service = OrderService()
    order = await service.get_order("12345")
    assert order.customer_id == "12345"
