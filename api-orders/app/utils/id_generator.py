"""
ID Generator utility for generating order numbers and references.
"""
from datetime import datetime
import random
import string


def generate_order_number(prefix: str = "CMD") -> str:
    """
    Generate a unique order number.
    Format: PREFIX-YYYYMMDD-NNNNN
    Example: CMD-20240215-00001
    """
    date_str = datetime.now().strftime("%Y%m%d")
    random_num = ''.join(random.choices(string.digits, k=5))
    return f"{prefix}-{date_str}-{random_num}"


def generate_transaction_id(prefix: str = "TXN") -> str:
    """
    Generate a unique transaction ID for payments.
    Format: PREFIX-TIMESTAMP-RANDOM
    Example: TXN-1708012345-ABC123
    """
    timestamp = int(datetime.now().timestamp())
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{timestamp}-{random_str}"


def generate_tracking_number(carrier_prefix: str = "TRK") -> str:
    """
    Generate a unique tracking number for shipments.
    Format: CARRIER-YYYYMMDD-RANDOM
    Example: TRK-20240215-XYZ789ABC
    """
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
    return f"{carrier_prefix}-{date_str}-{random_str}"


def generate_saga_id(saga_type: str) -> str:
    """
    Generate a unique saga ID.
    Format: SAGA-TYPE-TIMESTAMP-RANDOM
    Example: SAGA-CREATE_ORDER-1708012345-A1B2C3
    """
    timestamp = int(datetime.now().timestamp())
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"SAGA-{saga_type.upper()}-{timestamp}-{random_str}"
