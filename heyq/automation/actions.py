from __future__ import annotations
from dataclasses import dataclass
from loguru import logger
from .engine import BrowserManager
from ..nlp.intent import Intent, Intents
from ..pages.flipkart import FlipkartPage


@dataclass
class ActionContext:
    product: str | None = None


class ActionRunner:
    def __init__(self, bm: BrowserManager):
        self.bm = bm
        self.ctx = ActionContext()

    def run(self, intent: Intent):
        page = self.bm.page
        assert page
        if intent.name == Intents.NAVIGATE:
            site = intent.entities.get("site")
            if site:
                self.bm.goto(site)
                FlipkartPage(page).close_initial_popup()
        elif intent.name == Intents.SEARCH:
            q = intent.entities.get("query")
            if q:
                self.ctx.product = q
                FlipkartPage(page).search(q)
        elif intent.name == Intents.ADD_TO_CART:
            fp = FlipkartPage(page)
            product = fp.open_first_result()
            fp.add_selected_to_cart(product)
            fp.go_to_cart()
        elif intent.name == Intents.CHECKOUT:
            FlipkartPage(page).place_order()
        elif intent.name == Intents.CLICK:
            target = intent.entities.get("target")
            if target:
                try:
                    page.get_by_text(target, exact=False).click(timeout=10000)
                except Exception:
                    logger.warning("Failed to click target: {}", target)
        elif intent.name == Intents.LOGIN:
            logger.info("Login intent received - actual login handled during checkout on Flipkart")
        elif intent.name == Intents.PLACE_ORDER:
            FlipkartPage(page).place_order()
        else:
            logger.warning("Unknown intent: {}", intent)
