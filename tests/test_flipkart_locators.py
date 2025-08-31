import os
import pytest
from playwright.sync_api import sync_playwright

from heyq.pages.flipkart import FlipkartPage

pytestmark = pytest.mark.smoke


@pytest.mark.e2e
@pytest.mark.skipif(os.environ.get('CI') == 'true', reason='Skip live site in CI')
def test_flipkart_locators_health_check():
    """
    Fast health-check to validate critical locators resolve on real pages.
    - Home: search input present
    - Search results: first product element clickable
    - PDP: add-to-cart visible
    - Cart: place order visible (after adding)
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        fp = FlipkartPage(page)

        # Home
        page.goto('https://www.flipkart.com', wait_until='domcontentloaded')
        fp.close_initial_popup()
        assert page.locator(fp.sel.search_input).first.is_visible(), 'search input not visible'

        # Search -> Results
        fp.search('iPhone 16 Pro')
        res_locator = page.locator('a[href*="/p/"]').first
        res_locator.wait_for(state='visible', timeout=45000)
        assert res_locator.is_visible(), 'first result not visible'

        # Open PDP (popup or same-tab)
        try:
            with page.expect_popup(timeout=5000) as pop:
                res_locator.click()
            pdp = pop.value
        except Exception:
            res_locator.click()
            pdp = page
        pdp.wait_for_load_state('domcontentloaded')

        # PDP: Add to cart
        add_btn = pdp.locator(fp.sel.add_to_cart)
        add_btn.wait_for(state='visible', timeout=45000)
        assert add_btn.is_visible(), 'Add to cart not visible on PDP'

        # Add and go to cart
        add_btn.click()
        fp.go_to_cart()

        # Cart: Place order
        place_btn = page.locator(fp.sel.place_order)
        place_btn.wait_for(state='visible', timeout=45000)
        assert place_btn.is_visible(), 'Place Order not visible in cart'

        context.close()
        browser.close()
