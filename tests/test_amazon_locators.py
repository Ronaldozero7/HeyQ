import os
import pytest
from playwright.sync_api import sync_playwright

from heyq.pages.amazon import AmazonPage

pytestmark = pytest.mark.smoke


@pytest.mark.e2e
@pytest.mark.skipif(os.environ.get('CI') == 'true', reason='Skip live site in CI')
def test_amazon_locators_health_check():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        az = AmazonPage(page)

        page.goto('https://www.amazon.in', wait_until='domcontentloaded')
        az.open_login()
        # Don't actually login; just ensure email field exists on sign-in page
        assert page.locator(az.sel.email_input).first.is_visible()

        # Back to home for search
        page.goto('https://www.amazon.in', wait_until='domcontentloaded')
        az.search('iPhone 16 Pro')
        first = page.locator(az.sel.first_result_link).first
        first.wait_for(state='visible', timeout=45000)
        assert first.is_visible()

        # PDP open (no add to cart click to avoid stash)
        try:
            with page.expect_popup(timeout=3000) as pop:
                first.click()
            pdp = pop.value
        except Exception:
            first.click()
            pdp = page
        pdp.wait_for_load_state('domcontentloaded')
        assert pdp.locator(az.sel.add_to_cart_btn).first.is_visible()

        context.close()
        browser.close()
