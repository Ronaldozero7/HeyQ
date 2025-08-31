from __future__ import annotations
import re
from typing import Dict, Any
from .intent import Intent, Intents


class NLPEngine:
    """Intent recognizer using regex and simple context, no heavy deps."""

    def __init__(self):
        self.context: Dict[str, Any] = {}

    def parse(self, text: str) -> Intent:
        t = text.lower().strip()

        # Handle multi-step commands first
        if self._is_multi_step_command(t):
            return self._parse_multi_step_command(t)

        product = self._extract_product(t)
        site = self._extract_site(t)

        if any(w in t for w in ["go to", "open", "navigate"]):
            if site:
                self.context["site"] = site
            return Intent(Intents.NAVIGATE, {"site": site or self.context.get("site")})

        if any(w in t for w in ["search for", "find", "look for", "search"]):
            if product:
                self.context["product"] = product
            return Intent(Intents.SEARCH, {"query": product or self.context.get("product")})

        if "add to cart" in t or "add it to cart" in t or "add a" in t:
            # Extract product from add to cart commands
            product = self._extract_product_from_add_to_cart(t)
            if product:
                self.context["product"] = product
            return Intent(Intents.ADD_TO_CART, {"product": product or self.context.get("product")})

        if "checkout" in t or "proceed to checkout" in t:
            return Intent(Intents.CHECKOUT, {})

        if "login" in t or "sign in" in t:
            return Intent(Intents.LOGIN, {"use_saved": True})

        if "place order" in t or "buy now" in t:
            return Intent(Intents.PLACE_ORDER, {})

        if any(w in t for w in ["click", "press"]):
            m = re.search(r"click (?:on )?(.*)", t)
            target = m.group(1).strip() if m else None
            return Intent(Intents.CLICK, {"target": target})

        return Intent(Intents.UNKNOWN, {"raw": text})

    def _is_multi_step_command(self, text: str) -> bool:
        """Check if this is a multi-step automation command"""
        multi_step_indicators = [
            # Complex automation flows
            r"open.*login.*add.*cart.*place.*order",
            r"login.*add.*cart.*place.*order", 
            r"add.*cart.*place.*order",
            r"open.*login.*add.*cart",
            # Verification flows
            r".*verify.*price",
            r".*and verify"
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in multi_step_indicators)

    def _parse_multi_step_command(self, text: str) -> Intent:
        """Parse complex multi-step automation commands"""
        # Extract site first
        site = self._extract_site(text) or "saucedemo"  # Default to saucedemo
        self.context["site"] = site
        
        # Extract product
        product = self._extract_product_from_multi_step(text)
        if product:
            self.context["product"] = product
            
        # Determine primary action based on command structure
        if "place order" in text or "place the order" in text:
            return Intent("FULL_CHECKOUT_FLOW", {
                "site": site,
                "product": product,
                "steps": ["login", "add_to_cart", "checkout", "place_order"],
                "verify_price": "verify" in text
            })
        elif "add" in text and "cart" in text:
            return Intent("ADD_TO_CART_FLOW", {
                "site": site, 
                "product": product,
                "steps": ["login", "add_to_cart"],
                "verify_price": "verify" in text
            })
        else:
            return Intent(Intents.UNKNOWN, {"raw": text})

    def _extract_product_from_add_to_cart(self, text: str) -> str | None:
        """Extract product from add to cart commands"""
        patterns = [
            r"add\s+(?:a\s+)?(\w+)\s+to\s+cart",
            r"add\s+to\s+cart\s+(?:a\s+)?(\w+)",
            r"add\s+(?:a\s+)?(\w+)",
        ]
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return None

    def _extract_product_from_multi_step(self, text: str) -> str | None:
        """Extract product from multi-step commands"""
        patterns = [
            r"add\s+(?:a\s+)?(\w+)\s+to",
            r"add\s+(?:a\s+)?(\w+)",
            r"(?:get|buy)\s+(?:a\s+)?(\w+)",
        ]
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                product = m.group(1).strip()
                # Map common product names
                if product.lower() in ['backpack', 'bag', 'rucksack']:
                    return 'backpack'
                elif product.lower() in ['shirt', 'tshirt', 't-shirt']:
                    return 't-shirt'
                return product
        return None

    def _extract_product(self, t: str) -> str | None:
        m = re.search(r"(?:search(?: for)?|find|look for)\s+(.+)$", t)
        if m:
            return m.group(1).strip()
        # fallback heuristic: last quoted string
        q = re.findall(r"'([^']+)'|\"([^\"]+)\"", t)
        if q:
            s = next(filter(None, q[-1]))
            return s
        # fallback: last 2 tokens
        parts = t.split()
        if len(parts) >= 2:
            return " ".join(parts[-2:])
        return None

    def _extract_site(self, t: str) -> str | None:
        if "flipkart" in t:
            return "https://www.flipkart.com"
        m = re.search(r"(https?://\S+)", t)
        if m:
            return m.group(1)
        return None
