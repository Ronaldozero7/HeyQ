from __future__ import annotations
from dataclasses import dataclass
import re
from loguru import logger
from playwright.sync_api import Page, TimeoutError as PWTimeoutError


@dataclass
class AmazonSelectors:
    # Header and search
    account_link: str = '#nav-link-accountList'
    search_box: str = '#twotabsearchtextbox'
    search_submit: str = '#nav-search-submit-button'

    # Sign-in
    # Use robust, comma-joined CSS lists; we'll bind through locator() not fill() directly
    email_input: str = 'input#ap_email, input#ap_email_login, input[name="email"], input[type="email"], input[id^="ap_email"]'
    continue_btn: str = 'input#continue, #continue, input[name="continue"]'
    password_input: str = 'input#ap_password, input[name="password"], input[type="password"]'
    sign_in_submit: str = 'input#signInSubmit, input[name="signInSubmit"], input[type="submit"][name="signInSubmit"]'
    use_password_instead: str = 'text=Use a password instead,Use your password instead,Password'  # text-based fallbacks
    other_options: str = 'text=Other options,Try another way'
    not_now_btn: str = 'text=Not now,Cancel'

    # Search results and PDP
    first_result_link: str = 'div[data-asin][data-component-type="s-search-result"] h2 a'
    add_to_cart_btn: str = '#add-to-cart-button, input#add-to-cart-button, input[name="submit.add-to-cart"]'

    # Cart and checkout
    cart_link: str = '#nav-cart, a[href*="/gp/cart/view.html"]'
    proceed_to_checkout: str = 'input[name="proceedToRetailCheckout"], input[name="proceedToALMCheckout"], span#sc-buy-box-ptc-button input'


class AmazonPage:
    def __init__(self, page: Page):
        self.page = page
        self.sel = AmazonSelectors()

    def open_login(self):
        try:
            acct = self.page.locator(self.sel.account_link).first
            acct.wait_for(state='visible', timeout=15000)
            acct.click(timeout=10000)
        except Exception:
            # fallback text search
            self.page.get_by_text('Hello, sign in', exact=False).first.click(timeout=10000)

    def _dismiss_passkey_routes(self):
        """Try to avoid passkey/WebAuthn flows and prefer password entry."""
        try:
            self.page.get_by_text('Use a password instead', exact=False).click(timeout=3000)
            return
        except Exception:
            pass
        try:
            self.page.get_by_text('Use your password instead', exact=False).click(timeout=3000)
            return
        except Exception:
            pass
        try:
            self.page.get_by_text('Other options', exact=False).click(timeout=3000)
        except Exception:
            pass
        try:
            self.page.get_by_text('Not now', exact=False).click(timeout=3000)
        except Exception:
            pass
        # Handle Amazon Passkeys dialog with a Cancel button (QR code modal)
        try:
            dlg = self.page.get_by_role('dialog').filter(has_text=re.compile('Passkey|Passkeys', re.I)).first
            # try common cancel/close names
            try:
                btn = dlg.get_by_role('button', name=re.compile('Cancel|Not now|Close', re.I)).first
                btn.click(timeout=2000)
                return
            except Exception:
                pass
            # fallback by text
            self.page.get_by_text('Cancel', exact=False).first.click(timeout=2000)
            return
        except Exception:
            pass

    def login_with_password(self, email: str, password: str):
        # Enter email/phone and continue
        try:
            email_loc = self.page.locator(self.sel.email_input).first
            email_loc.wait_for(state='visible', timeout=20000)
            try:
                email_loc.click(timeout=5000)
            except Exception:
                pass
            email_loc.fill(str(email), timeout=20000)
        except Exception:
            # Fallbacks: by label or role
            try:
                self.page.get_by_label('Enter mobile number or email', exact=False).fill(str(email), timeout=8000)
            except Exception:
                try:
                    self.page.get_by_placeholder('Email or mobile phone number', exact=False).fill(str(email), timeout=8000)
                except Exception:
                    logger.warning('Could not locate email field; proceeding (may already be filled or different flow).')

        # Continue to password step
        try:
            self.page.locator(self.sel.continue_btn).first.click(timeout=12000)
        except Exception:
            # Try pressing Enter if continue button not accessible
            try:
                self.page.keyboard.press('Enter')
            except Exception:
                logger.warning('Could not activate continue; password step may already be present.')

        # Dismiss passkey routes if prompted
        self._dismiss_passkey_routes()

        # Fill password
        try:
            pwd = self.page.locator(self.sel.password_input).first
            pwd.wait_for(state='visible', timeout=20000)
            pwd.fill(str(password), timeout=20000)
        except Exception:
            try:
                self.page.get_by_label('Password', exact=False).fill(str(password), timeout=8000)
            except Exception:
                logger.warning('Could not locate password field.')

        try:
            self.page.locator(self.sel.sign_in_submit).first.click(timeout=12000)
        except Exception:
            try:
                self.page.get_by_text('Sign in', exact=False).first.click(timeout=8000)
            except Exception:
                logger.warning('Could not click Sign in; trying Enter key.')
                try:
                    self.page.keyboard.press('Enter')
                except Exception:
                    pass

    def search(self, query: str):
        self.page.fill(self.sel.search_box, str(query), timeout=20000)
        self.page.click(self.sel.search_submit)
        self.page.wait_for_load_state('domcontentloaded')

    def open_first_result(self):
        link = self.page.locator(self.sel.first_result_link).first
        try:
            link.wait_for(state='visible', timeout=45000)
        except PWTimeoutError:
            # Fallback to first product title link
            link = self.page.locator('h2 a.a-link-normal').first
        try:
            with self.page.expect_popup(timeout=3000) as pop:
                link.click()
            product = pop.value
            return product
        except PWTimeoutError:
            link.click()
            return self.page

    def add_selected_to_cart(self, product_page: Page):
        product_page.wait_for_load_state('domcontentloaded')
        try:
            product_page.locator(self.sel.add_to_cart_btn).first.click(timeout=45000)
        except Exception:
            product_page.get_by_text('Add to Cart', exact=False).first.click()

    def go_to_cart(self):
        try:
            self.page.locator(self.sel.cart_link).first.click(timeout=15000)
        except Exception:
            self.page.get_by_text('Cart', exact=False).first.click()

    def proceed_to_checkout(self):
        try:
            self.page.locator(self.sel.proceed_to_checkout).first.click(timeout=20000)
        except Exception:
            self.page.get_by_text('Proceed to Buy', exact=False).first.click()
