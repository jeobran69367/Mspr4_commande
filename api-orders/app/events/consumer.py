"""
RabbitMQ Event Consumer for consuming events.
"""
import json
import aio_pika
import asyncio
from typing import Callable, Dict, Any
from app.config import settings


class EventConsumer:
    """RabbitMQ event consumer."""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None
        self.handlers: Dict[str, Callable] = {}
    
    async def connect(self):
        """Establish connection to RabbitMQ."""
        try:
            self.connection = await aio_pika.connect_robust(
                settings.rabbitmq_url
            )
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)
            
            # Declare exchange
            self.exchange = await self.channel.declare_exchange(
                settings.rabbitmq_exchange,
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )
            
            print(f"Consumer connected to RabbitMQ: {settings.rabbitmq_host}")
        except Exception as e:
            print(f"Failed to connect consumer to RabbitMQ: {e}")
            raise
    
    async def disconnect(self):
        """Close connection to RabbitMQ."""
        if self.connection:
            await self.connection.close()
            print("Consumer disconnected from RabbitMQ")
    
    def register_handler(self, event_pattern: str, handler: Callable):
        """
        Register a handler for specific event pattern.
        
        Args:
            event_pattern: Routing key pattern (e.g., "customer.*", "product.stock.updated")
            handler: Async function to handle the event
        """
        self.handlers[event_pattern] = handler
        print(f"Registered handler for pattern: {event_pattern}")
    
    async def process_message(self, message: aio_pika.IncomingMessage):
        """Process incoming message."""
        async with message.process():
            try:
                # Parse message
                body = json.loads(message.body.decode())
                event_type = body.get("event_type")
                
                print(f"Received event: {event_type}")
                
                # Find matching handler
                routing_key = message.routing_key
                handler = self.handlers.get(routing_key)
                
                if not handler:
                    # Try pattern matching
                    for pattern, h in self.handlers.items():
                        if self._matches_pattern(routing_key, pattern):
                            handler = h
                            break
                
                if handler:
                    await handler(body)
                else:
                    print(f"No handler found for event: {event_type}")
                    
            except Exception as e:
                print(f"Error processing message: {e}")
    
    def _matches_pattern(self, routing_key: str, pattern: str) -> bool:
        """Check if routing key matches pattern."""
        # Simple pattern matching (* = any single word, # = zero or more words)
        pattern_parts = pattern.split('.')
        key_parts = routing_key.split('.')
        
        if len(pattern_parts) != len(key_parts):
            if '#' not in pattern:
                return False
        
        for p, k in zip(pattern_parts, key_parts):
            if p == '#':
                return True
            if p != '*' and p != k:
                return False
        
        return True
    
    async def start_consuming(self, queue_name: str, binding_patterns: list):
        """
        Start consuming messages from a queue.
        
        Args:
            queue_name: Name of the queue
            binding_patterns: List of routing key patterns to bind
        """
        if not self.channel:
            await self.connect()
        
        # Declare queue
        queue = await self.channel.declare_queue(
            queue_name,
            durable=True
        )
        
        # Bind queue to exchange with patterns
        for pattern in binding_patterns:
            await queue.bind(self.exchange, routing_key=pattern)
            print(f"Bound queue {queue_name} to pattern: {pattern}")
        
        # Start consuming
        await queue.consume(self.process_message)
        print(f"Started consuming from queue: {queue_name}")


# Global consumer instance
_consumer = None


async def get_event_consumer() -> EventConsumer:
    """Get or create event consumer instance."""
    global _consumer
    if _consumer is None:
        _consumer = EventConsumer()
        await _consumer.connect()
    return _consumer


import pytest
from unittest.mock import AsyncMock
from app.events.consumer import EventConsumer

@pytest.mark.asyncio
async def test_event_consumer():
    mock_consumer = EventConsumer()
    mock_consumer.connect = AsyncMock()
    mock_consumer.start_consuming = AsyncMock()

    await mock_consumer.connect()
    mock_consumer.connect.assert_called_once()

    await mock_consumer.start_consuming()
    mock_consumer.start_consuming.assert_called_once()
