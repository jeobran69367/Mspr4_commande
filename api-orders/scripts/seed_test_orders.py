"""
Seed test orders into database.
"""
import asyncio
import sys
import os
from uuid import uuid4
from decimal import Decimal
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import AsyncSessionLocal, engine
from app.models.order import Order, OrderStatus, OrderSource, PaymentStatus
from app.models.order_item import OrderItem
from app.utils.id_generator import generate_order_number


async def create_test_orders():
    """Create test orders."""
    async with AsyncSessionLocal() as session:
        # Test customer IDs (should exist in Customer service)
        test_customer_id = uuid4()
        
        # Create test order 1
        order1 = Order(
            numero=generate_order_number("CMD"),
            customer_id=test_customer_id,
            customer_reference="CLT-2024-001",
            customer_email="test@example.com",
            customer_nom_complet="Jean Dupont",
            shipping_address={
                "ligne1": "123 Rue de la Paix",
                "ville": "Paris",
                "code_postal": "75001",
                "pays": "France"
            },
            billing_address={
                "ligne1": "123 Rue de la Paix",
                "ville": "Paris",
                "code_postal": "75001",
                "pays": "France"
            },
            status=OrderStatus.VALIDEE,
            payment_status=PaymentStatus.PAYE,
            subtotal_ht=Decimal("100.00"),
            shipping_cost_ht=Decimal("5.99"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("21.20"),
            total_ttc=Decimal("127.19"),
            source=OrderSource.WEB,
            currency="EUR"
        )
        
        session.add(order1)
        await session.flush()
        
        # Add items to order 1
        item1 = OrderItem(
            order_id=order1.id,
            product_id=uuid4(),
            product_reference="CAFE-001",
            product_name="Café Arabica Premium",
            quantity=2,
            unit_price_ht=Decimal("25.00"),
            tax_rate=Decimal("0.20"),
            tax_amount=Decimal("10.00"),
            subtotal_ht=Decimal("50.00"),
            total_ttc=Decimal("60.00")
        )
        
        item2 = OrderItem(
            order_id=order1.id,
            product_id=uuid4(),
            product_reference="CAFE-002",
            product_name="Café Robusta",
            quantity=2,
            unit_price_ht=Decimal("25.00"),
            tax_rate=Decimal("0.20"),
            tax_amount=Decimal("10.00"),
            subtotal_ht=Decimal("50.00"),
            total_ttc=Decimal("60.00")
        )
        
        session.add(item1)
        session.add(item2)
        
        await session.commit()
        
        print(f"Created test order: {order1.numero}")


async def main():
    """Main function."""
    print("Seeding test orders...")
    
    try:
        await create_test_orders()
        print("Test orders created successfully!")
    except Exception as e:
        print(f"Error creating test orders: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
