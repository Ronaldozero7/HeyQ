from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Intent:
    name: str
    entities: Dict[str, Any]


class Intents:
    NAVIGATE = "navigate"
    SEARCH = "search"
    CLICK = "click"
    ADD_TO_CART = "add_to_cart"
    CHECKOUT = "checkout"
    LOGIN = "login"
    FILL_FORM = "fill_form"
    PLACE_ORDER = "place_order"
    UNKNOWN = "unknown"
    
    # Multi-step automation intents
    FULL_CHECKOUT_FLOW = "full_checkout_flow"
    ADD_TO_CART_FLOW = "add_to_cart_flow"
