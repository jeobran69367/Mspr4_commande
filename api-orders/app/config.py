"""
Configuration module for the Orders Service.
Loads settings from environment variables.
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql+asyncpg://orders_user:orders_password@localhost:5435/orders_db",
        alias="DATABASE_URL"
    )
    database_host: str = Field(default="localhost", alias="DATABASE_HOST")
    database_port: int = Field(default=5435, alias="DATABASE_PORT")
    database_name: str = Field(default="orders_db", alias="DATABASE_NAME")
    database_user: str = Field(default="orders_user", alias="DATABASE_USER")
    database_password: str = Field(default="orders_password", alias="DATABASE_PASSWORD")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8003, alias="API_PORT")
    api_reload: bool = Field(default=True, alias="API_RELOAD")
    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # RabbitMQ Configuration
    rabbitmq_host: str = Field(default="localhost", alias="RABBITMQ_HOST")
    rabbitmq_port: int = Field(default=5672, alias="RABBITMQ_PORT")
    rabbitmq_user: str = Field(default="payetonkawa", alias="RABBITMQ_USER")
    rabbitmq_password: str = Field(default="payetonkawa123", alias="RABBITMQ_PASSWORD")
    rabbitmq_vhost: str = Field(default="/", alias="RABBITMQ_VHOST")
    rabbitmq_exchange: str = Field(default="payetonkawa_events", alias="RABBITMQ_EXCHANGE")
    rabbitmq_queue_orders: str = Field(default="orders_queue", alias="RABBITMQ_QUEUE_ORDERS")
    rabbitmq_queue_customers: str = Field(default="customers_queue", alias="RABBITMQ_QUEUE_CUSTOMERS")
    rabbitmq_queue_products: str = Field(default="products_queue", alias="RABBITMQ_QUEUE_PRODUCTS")
    
    # External Services
    customer_service_url: str = Field(default="http://localhost:8001", alias="CUSTOMER_SERVICE_URL")
    product_service_url: str = Field(default="http://localhost:8002", alias="PRODUCT_SERVICE_URL")
    
    # Payment Gateway
    payment_gateway_url: str = Field(default="http://localhost:9000", alias="PAYMENT_GATEWAY_URL")
    payment_gateway_api_key: str = Field(default="test_key_123", alias="PAYMENT_GATEWAY_API_KEY")
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production", alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        alias="CORS_ORIGINS"
    )
    
    # Order Settings
    order_prefix: str = Field(default="CMD", alias="ORDER_PREFIX")
    currency: str = Field(default="EUR", alias="CURRENCY")
    default_tax_rate: float = Field(default=0.20, alias="DEFAULT_TAX_RATE")
    free_shipping_threshold: float = Field(default=100.00, alias="FREE_SHIPPING_THRESHOLD")
    standard_shipping_cost: float = Field(default=5.99, alias="STANDARD_SHIPPING_COST")
    
    class Config:
        model_config = ConfigDict(env_file=".env", case_sensitive=False)
        
    @property
    def rabbitmq_url(self) -> str:
        """Construct RabbitMQ connection URL."""
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}{self.rabbitmq_vhost}"


# Global settings instance
settings = Settings()
