from __future__ import annotations
from dataclasses import dataclass
from playwright.sync_api import Page
from difflib import SequenceMatcher
import re


@dataclass
class SauceSelectors:
    username: str = '#user-name'
    password: str = '#password'
    login_btn: str = '#login-button'

    # Inventory / cart
    cart_link: str = '.shopping_cart_link'
    cart_badge: str = '.shopping_cart_badge'
    inventory_item: str = '.inventory_item'
    inventory_item_price: str = '.inventory_item_price'
    cart_item: str = '.cart_item'
    cart_item_price: str = '.inventory_item_price'
    add_to_cart_by_name_tpl: str = '//div[@class="inventory_item"]//div[@class="inventory_item_name" and normalize-space()="{name}"]/ancestor::div[@class="inventory_item"]//button[contains(@data-test,"add-to-cart")]'

    # Checkout
    checkout_btn: str = '#checkout'
    first_name: str = '#first-name'
    last_name: str = '#last-name'
    postal_code: str = '#postal-code'
    continue_btn: str = '#continue'
    finish_btn: str = '#finish'
    complete_header: str = '.complete-header'


class SauceDemoPage:
    def __init__(self, page: Page):
        self.page = page
        self.sel = SauceSelectors()

    def goto_home(self):
        self.page.goto('https://www.saucedemo.com', wait_until='domcontentloaded')

    def login(self, username: str, password: str):
        # Fill creds and submit
        self.page.locator(self.sel.username).fill(username, timeout=20000)
        self.page.locator(self.sel.password).fill(password, timeout=20000)
        # Use locator.click for auto-waits
        self.page.locator(self.sel.login_btn).click(timeout=15000)
        # Wait until inventory page is ready (post-login navigation)
        try:
            self.page.wait_for_url("**/inventory.html", timeout=20000)
        except Exception:
            # Fallback to waiting for inventory items
            self.page.locator(self.sel.inventory_item).first.wait_for(state='visible', timeout=20000)

    def _wait_for_inventory(self):
        # Ensure inventory is visible before interacting
        try:
            self.page.wait_for_url("**/inventory.html", timeout=10000)
        except Exception:
            pass
        self.page.locator(self.sel.inventory_item).first.wait_for(state='visible', timeout=20000)

    def _wait_cart_count_at_least(self, n: int = 1, timeout: int = 15000) -> bool:
        # Poll cart badge text until it reaches n or timeout
        elapsed = 0
        step = 250
        while elapsed < timeout:
            try:
                badge = self.page.locator(self.sel.cart_badge).first
                if badge.count() > 0:
                    txt = (badge.inner_text(timeout=1000) or '').strip()
                    if txt.isdigit() and int(txt) >= n:
                        return True
            except Exception:
                pass
            self.page.wait_for_timeout(step)
            elapsed += step
        return False

    def add_to_cart_by_name(self, name: str = 'Sauce Labs Backpack'):
        # Wait for inventory to be rendered
        self._wait_for_inventory()
        # Prefer the product-specific add button by name
        xp = self.sel.add_to_cart_by_name_tpl.format(name=name)
        item = None
        try:
            loc = self.page.locator(xp).first
            loc.scroll_into_view_if_needed(timeout=5000)
            # Keep a reference to the item card for verifying toggle to Remove
            item = loc.locator('xpath=ancestor::div[@class="inventory_item"]').first
            loc.click(timeout=15000)
            # Verify button toggled to Remove and cart badge updated
            try:
                if item is not None:
                    item.get_by_role('button', name=re.compile(r'^Remove$', re.I)).first.wait_for(state='visible', timeout=8000)
            except Exception:
                pass
            self._wait_cart_count_at_least(1, timeout=10000)
            return
        except Exception:
            # fallback to fuzzy match if exact text XPATH fails
            pass
        # As another fallback, click the add-to-cart within the best-matching product card
        self.add_to_cart_best_match(name)

    def _inventory_items(self):
        return self.page.locator(self.sel.inventory_item)

    def list_product_names(self) -> list[str]:
        names = []
        items = self._inventory_items()
        count = items.count()
        for i in range(count):
            try:
                nm = items.nth(i).locator('.inventory_item_name').inner_text().strip()
                names.append(nm)
            except Exception:
                continue
        return names

    @staticmethod
    def _score(a: str, b: str) -> float:
        a = a.lower().strip(); b = b.lower().strip()
        # high score if substring match
        if a in b or b in a:
            return 1.0
        return SequenceMatcher(None, a, b).ratio()

    def add_to_cart_best_match(self, query: str):
        # Try to find the best matching product card and click its Add to cart
        self._wait_for_inventory()
        names = self.list_product_names()
        if not names:
            # inventory might not be loaded yet; try waiting briefly
            try:
                self.page.wait_for_load_state('domcontentloaded', timeout=5000)
                names = self.list_product_names()
            except Exception:
                pass
        if not names:
            # As a last resort, click the first visible add-to-cart button
            self.page.get_by_role('button', name=re.compile(r'^Add to cart$', re.I)).first.click(timeout=10000)
            return
        best = max(names, key=lambda n: self._score(query, n))
        item = self.page.locator(self.sel.inventory_item).filter(has_text=re.compile(re.escape(best), re.I)).first
        btn = item.get_by_role('button', name=re.compile(r'^Add to cart$', re.I))
        try:
            btn.first.scroll_into_view_if_needed(timeout=5000)
            btn.first.click(timeout=10000)
            # Verify toggled to Remove and badge increased
            try:
                item.get_by_role('button', name=re.compile(r'^Remove$', re.I)).first.wait_for(state='visible', timeout=8000)
            except Exception:
                pass
            self._wait_cart_count_at_least(1, timeout=10000)
        except Exception:
            # alternative class-based button
            item.locator('button.btn_small.btn_inventory').first.click(timeout=10000)
            self._wait_cart_count_at_least(1, timeout=10000)

    def go_to_cart(self):
        self.page.locator(self.sel.cart_link).first.click(timeout=10000)
        # Wait for cart page to load
        try:
            self.page.wait_for_url("**/cart.html", timeout=10000)
        except Exception:
            # Ensure checkout button is present
            self.page.locator(self.sel.checkout_btn).first.wait_for(state='visible', timeout=10000)

    def checkout(self, first_name: str, last_name: str, postal: str):
        # Cart -> Checkout step one
        self.page.locator(self.sel.checkout_btn).first.click(timeout=15000)
        # Wait for form fields then fill
        self.page.locator(self.sel.first_name).wait_for(state='visible', timeout=15000)
        self.page.locator(self.sel.first_name).fill(str(first_name), timeout=10000)
        self.page.locator(self.sel.last_name).fill(str(last_name), timeout=10000)
        self.page.locator(self.sel.postal_code).fill(str(postal), timeout=10000)
        self.page.locator(self.sel.continue_btn).click(timeout=15000)
        # Step two -> Finish
        self.page.locator(self.sel.finish_btn).wait_for(state='visible', timeout=15000)
        self.page.locator(self.sel.finish_btn).click(timeout=15000)
        # Return true if we see completion
        try:
            self.page.locator(self.sel.complete_header).first.wait_for(state='visible', timeout=20000)
            return True
        except Exception:
            return False

    def get_product_price_on_inventory(self, product_name: str) -> str | None:
        """Get the price of a product from the inventory page"""
        try:
            # Find the product item by name
            product_xpath = f'//div[@class="inventory_item"]//div[@class="inventory_item_name" and normalize-space()="{product_name}"]/ancestor::div[@class="inventory_item"]'
            product_item = self.page.locator(product_xpath).first
            price_element = product_item.locator(self.sel.inventory_item_price).first
            price_text = price_element.inner_text(timeout=5000)
            return price_text.strip()
        except Exception:
            return None

    def get_product_price_in_cart(self, product_name: str) -> str | None:
        """Get the price of a product from the cart page"""
        try:
            # Find the cart item by name
            cart_xpath = f'//div[@class="cart_item"]//div[@class="inventory_item_name" and normalize-space()="{product_name}"]/ancestor::div[@class="cart_item"]'
            cart_item = self.page.locator(cart_xpath).first
            price_element = cart_item.locator(self.sel.cart_item_price).first
            price_text = price_element.inner_text(timeout=5000)
            return price_text.strip()
        except Exception:
            return None

    def verify_product_in_cart(self, product_name: str, expected_price: str | None = None) -> dict:
        """Verify a product is in the cart and optionally check its price"""
        result = {
            'product_found': False,
            'price_match': None,
            'actual_price': None,
            'expected_price': expected_price
        }
        
        try:
            # Check if product is in cart
            cart_xpath = f'//div[@class="cart_item"]//div[@class="inventory_item_name" and normalize-space()="{product_name}"]'
            product_in_cart = self.page.locator(cart_xpath).first
            product_in_cart.wait_for(state='visible', timeout=5000)
            result['product_found'] = True
            
            # If expected price provided, verify it
            if expected_price:
                actual_price = self.get_product_price_in_cart(product_name)
                result['actual_price'] = actual_price
                result['price_match'] = actual_price == expected_price
                
        except Exception:
            pass
            
        return result
