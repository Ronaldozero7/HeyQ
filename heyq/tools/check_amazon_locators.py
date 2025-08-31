from playwright.sync_api import sync_playwright
from heyq.pages.amazon import AmazonPage, AmazonSelectors


def run(headless: bool = False):
    sel = AmazonSelectors()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto('https://www.amazon.in', wait_until='domcontentloaded')

        az = AmazonPage(page)
        az.open_login()

        def exists(locator_str: str) -> int:
            try:
                return page.locator(locator_str).count()
            except Exception:
                return 0

        print('[login] candidates present:')
        print('  email_input (css list):', exists(sel.email_input))
        print('  label("Enter mobile number or email"):', page.get_by_label('Enter mobile number or email', exact=False).count())
        print('  placeholder("Email or mobile phone number"):', page.get_by_placeholder('Email or mobile phone number', exact=False).count())
        print('  continue_btn:', exists(sel.continue_btn))

        ctx.close(); browser.close()


if __name__ == '__main__':
    run(headless=False)
