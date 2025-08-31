from playwright.sync_api import sync_playwright
from heyq.pages.flipkart import FlipkartPage


def run(headless: bool = False):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        fp = FlipkartPage(page)

        page.goto('https://www.flipkart.com', wait_until='domcontentloaded')
        fp.close_initial_popup()
        print('[home] search input visible:', page.locator(fp.sel.search_input).first.is_visible())

        fp.search('iPhone 16 Pro')
        first = page.locator('a[href*="/p/"]').first
        first.wait_for(state='visible', timeout=45000)
        print('[results] first result visible:', first.is_visible())

        try:
            with page.expect_popup(timeout=5000) as pop:
                first.click()
            pdp = pop.value
        except Exception:
            first.click()
            pdp = page
        pdp.wait_for_load_state('domcontentloaded')

        add_btn = pdp.locator(fp.sel.add_to_cart)
        add_btn.wait_for(state='visible', timeout=45000)
        print('[pdp] add to cart visible:', add_btn.is_visible())

        context.close()
        browser.close()


if __name__ == '__main__':
    run(headless=False)
