"""
Workflow for order status transitions.
"""
from enum import Enum
from typing import Dict, List


class OrderStatus(str, Enum):
    """Order status enum."""
    PANIER = "panier"
    VALIDEE = "validee"
    EN_PREPARATION = "en_preparation"
    EXPEDIEE = "expediee"
    LIVREE = "livree"
    ANNULEE = "annulee"
    RETOURNEE = "retournee"
    EN_ATTENTE_PAIEMENT = "en_attente_paiement"
    PAIEMENT_ECHOUE = "paiement_echoue"


# Define valid status transitions
STATUS_TRANSITIONS: Dict[OrderStatus, List[OrderStatus]] = {
    OrderStatus.PANIER: [
        OrderStatus.VALIDEE,
        OrderStatus.ANNULEE
    ],
    OrderStatus.VALIDEE: [
        OrderStatus.EN_ATTENTE_PAIEMENT,
        OrderStatus.EN_PREPARATION,
        OrderStatus.ANNULEE
    ],
    OrderStatus.EN_ATTENTE_PAIEMENT: [
        OrderStatus.VALIDEE,
        OrderStatus.PAIEMENT_ECHOUE,
        OrderStatus.ANNULEE
    ],
    OrderStatus.PAIEMENT_ECHOUE: [
        OrderStatus.EN_ATTENTE_PAIEMENT,
        OrderStatus.ANNULEE
    ],
    OrderStatus.EN_PREPARATION: [
        OrderStatus.EXPEDIEE,
        OrderStatus.ANNULEE
    ],
    OrderStatus.EXPEDIEE: [
        OrderStatus.LIVREE,
        OrderStatus.RETOURNEE
    ],
    OrderStatus.LIVREE: [
        OrderStatus.RETOURNEE
    ],
    OrderStatus.ANNULEE: [],
    OrderStatus.RETOURNEE: []
}


def is_valid_transition(current_status: OrderStatus, new_status: OrderStatus) -> bool:
    """Check if status transition is valid."""
    if current_status not in STATUS_TRANSITIONS:
        return False
    return new_status in STATUS_TRANSITIONS[current_status]


def get_allowed_transitions(current_status: OrderStatus) -> List[OrderStatus]:
    """Get list of allowed transitions from current status."""
    return STATUS_TRANSITIONS.get(current_status, [])
