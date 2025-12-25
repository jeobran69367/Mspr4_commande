"""
RabbitMQ Event Producer for publishing events.
"""
import json
import aio_pika
from typing import Dict, Any
from datetime import datetime
from app.config import settings
from app.schemas.event import EventType


class EventProducer:
    """RabbitMQ event producer."""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None
    
    async def connect(self):
        """Establish connection to RabbitMQ."""
        try:
            self.connection = await aio_pika.connect_robust(
                settings.rabbitmq_url
            )
            self.channel = await self.connection.channel()
            
            # Declare exchange
            self.exchange = await self.channel.declare_exchange(
                settings.rabbitmq_exchange,
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )
            
            print(f"Connected to RabbitMQ: {settings.rabbitmq_host}")
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    async def disconnect(self):
        """Close connection to RabbitMQ."""
        if self.connection:
            await self.connection.close()
            print("Disconnected from RabbitMQ")
    
    async def publish_event(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        routing_key: str = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Publish an event to RabbitMQ.
        
        Args:
            event_type: Type of event
            data: Event data
            routing_key: Optional routing key (defaults to event_type)
            metadata: Optional metadata
            
        Returns:
            True if published successfully, False otherwise
        """
        if not self.exchange:
            await self.connect()
        
        try:
            # Prepare event message
            event_message = {
                "event_type": event_type.value,
                "event_id": f"{event_type.value}_{int(datetime.utcnow().timestamp())}",
                "timestamp": datetime.utcnow().isoformat(),
                "source_service": "orders",
                "data": data,
                "metadata": metadata or {}
            }
            
            # Use event_type as routing key if not provided
            if not routing_key:
                routing_key = event_type.value
            
            # Publish message
            message = aio_pika.Message(
                body=json.dumps(event_message).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            
            await self.exchange.publish(
                message,
                routing_key=routing_key
            )
            
            print(f"Published event: {event_type.value} with routing key: {routing_key}")
            return True
            
        except Exception as e:
            print(f"Failed to publish event {event_type.value}: {e}")
            return False
    
    async def publish_order_created(self, order_data: Dict[str, Any]) -> bool:
        """Publish order created event."""
        return await self.publish_event(
            EventType.ORDER_CREATED,
            order_data,
            routing_key="order.created"
        )
    
    async def publish_order_validated(self, order_data: Dict[str, Any]) -> bool:
        """Publish order validated event."""
        return await self.publish_event(
            EventType.ORDER_VALIDATED,
            order_data,
            routing_key="order.validated"
        )
    
    async def publish_order_paid(self, order_data: Dict[str, Any]) -> bool:
        """Publish order paid event."""
        return await self.publish_event(
            EventType.ORDER_PAID,
            order_data,
            routing_key="order.paid"
        )
    
    async def publish_order_shipped(self, order_data: Dict[str, Any]) -> bool:
        """Publish order shipped event."""
        return await self.publish_event(
            EventType.ORDER_SHIPPED,
            order_data,
            routing_key="order.shipped"
        )
    
    async def publish_order_delivered(self, order_data: Dict[str, Any]) -> bool:
        """Publish order delivered event."""
        return await self.publish_event(
            EventType.ORDER_DELIVERED,
            order_data,
            routing_key="order.delivered"
        )
    
    async def publish_order_cancelled(self, order_data: Dict[str, Any]) -> bool:
        """Publish order cancelled event."""
        return await self.publish_event(
            EventType.ORDER_CANCELLED,
            order_data,
            routing_key="order.cancelled"
        )


# Global producer instance
_producer = None


async def get_event_producer() -> EventProducer:
    """Get or create event producer instance."""
    global _producer
    if _producer is None:
        _producer = EventProducer()
        await _producer.connect()
    return _producer
