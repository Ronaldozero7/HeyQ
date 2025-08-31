from __future__ import annotations
from dataclasses import dataclass
from loguru import logger
from playwright.sync_api import Page, TimeoutError as PWTimeoutError


@dataclass
class FlipkartSelectors:
    close_login_popup_btn: str = 'button._2KpZ6l._2doB4z'  # close initial login popup
    search_input: str = 'input[title="Search for Products, Brands and More"]'
    search_submit: str = 'button[type="submit"]'
    first_result: str = 'a._1fQZEK, a.s1Q9rs'  # depends on layout
    add_to_cart: str = 'button._2KpZ6l._2U9uOA._3v1-ww'
    go_to_cart: str = 'a._3SkBxJ'  # View Cart
    place_order: str = 'button._2KpZ6l._2ObVJD._3AWRsL'  # Place Order
    login_link_text: str = 'Login'
    login_continue_btn: str = 'button._2KpZ6l._2HKlqd._3AWRsL'  # Continue/login
    username_input: str = 'input[class*="_2IX_2-"][type="text"]'
    password_input: str = 'input[class*="_2IX_2-"][type="password"]'
    use_password_link: str = 'span:has-text("Use Password")'


class FlipkartPage:
    def __init__(self, page: Page):
        self.page = page
        self.sel = FlipkartSelectors()

    def close_initial_popup(self):
        try:
            self.page.click(self.sel.close_login_popup_btn, timeout=5000)
            logger.info("Closed initial login popup")
        except Exception:
            pass

    def search(self, query: str):
        self.page.fill(self.sel.search_input, str(query), timeout=30000)
        self.page.click(self.sel.search_submit)
        # Ensure results load
        self.page.wait_for_load_state("domcontentloaded")

    def open_login(self):
        # Try to click Login in header, or trigger login popup if present
        try:
            self.page.get_by_text(self.sel.login_link_text, exact=False).first.click(timeout=5000)
        except Exception:
            # If popup already shown, ignore
            pass

    def login_with_password(self, username: str, password: str):
        # On some layouts, default is OTP; try switch to password
        try:
            self.page.locator(self.sel.use_password_link).click(timeout=4000)
        except Exception:
            pass
        # Fill username
        filled_user = False
        for sel in [self.sel.username_input, 'input[autocomplete="username"]', 'input[placeholder*="Enter Email"], input[placeholder*="Mobile"]']:
            try:
                self.page.fill(sel, str(username), timeout=5000)
                filled_user = True
                break
            except Exception:
                continue
        if not filled_user:
            logger.warning("Username field not found; continuing")
        # Fill password
        filled_pwd = False
        for sel in [self.sel.password_input, 'input[autocomplete="current-password"]', 'input[type="password"]']:
            try:
                self.page.fill(sel, str(password), timeout=5000)
                filled_pwd = True
                break
            except Exception:
                continue
        if not filled_pwd:
            logger.warning("Password field not found; continuing")
        # Click Continue/Login
        for sel in [self.sel.login_continue_btn, 'button:has-text("Login")', 'button:has-text("Request OTP")', 'button[type="submit"]']:
            try:
                self.page.click(sel, timeout=5000)
                break
            except Exception:
                continue

    def open_first_result(self):
        # Try multiple robust selectors for first product tile link
        candidates = [
            'a[href*="/p/"]',
            'a._1fQZEK',
            'a.s1Q9rs',
        ]
        first_link = None
        for sel in candidates:
            locator = self.page.locator(sel).first
            try:
                locator.wait_for(state="visible", timeout=45000)
                first_link = locator
                break
            except PWTimeoutError:
                continue
            except Exception:
                continue
        if first_link is None:
            # As a last resort, click the first visible link on the page
            first_link = self.page.locator('a').first
        try:
            with self.page.expect_popup(timeout=5000) as pop:
                first_link.click()
            product = pop.value
            return product
        except PWTimeoutError:
            # Opened in same tab
            first_link.click()
            return self.page

    def add_selected_to_cart(self, product_page: Page):
        product_page.wait_for_load_state("domcontentloaded")
        try:
            product_page.click(self.sel.add_to_cart, timeout=45000)
        except Exception:
            # Fallback button text contains
            product_page.get_by_text("Add to cart", exact=False).click()

    def go_to_cart(self):
        try:
            self.page.click(self.sel.go_to_cart, timeout=15000)
        except Exception:
            self.page.get_by_text("Cart", exact=False).click()

    def place_order(self):
        try:
            self.page.click(self.sel.place_order, timeout=20000)
        except Exception:
            self.page.get_by_text("Place Order", exact=False).click()

    def try_fill_payment(self, card_number: str, card_name: str, card_exp: str, card_cvv: str):
        # This is highly environment-specific and often blocked in prod. Best effort only.
        selectors = {
            "card_number": ["input[name='cardNumber']", "input[placeholder*='Card number']"],
            "card_name": ["input[name='nameOnCard']", "input[placeholder*='Name']"],
            "card_exp": ["input[name='expiryDate']", "input[placeholder*='MM/YY']", "input[placeholder*='MM / YY']"],
            "card_cvv": ["input[name='cvv']", "input[placeholder*='CVV']"],
        }
        for sel in selectors["card_number"]:
            try:
                self.page.fill(sel, str(card_number), timeout=5000)
                break
            except Exception:
                continue
        for sel in selectors["card_name"]:
            try:
                self.page.fill(sel, str(card_name), timeout=3000)
                break
            except Exception:
                continue
        for sel in selectors["card_exp"]:
            try:
                self.page.fill(sel, str(card_exp), timeout=3000)
                break
            except Exception:
                continue
        for sel in selectors["card_cvv"]:
            try:
                self.page.fill(sel, str(card_cvv), timeout=3000)
                break
            except Exception:
                continue
