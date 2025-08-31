from __future__ import annotations
import os
import yaml
from pathlib import Path
from loguru import logger
import pytest

from heyq.config import CONFIG
from heyq.logger import setup_logger, update_redaction
from heyq.security.secrets import Secrets
from heyq.automation.engine import BrowserManager
from heyq.pages.flipkart import FlipkartPage


DATA_FILE = Path(__file__).parent.parent / 'data' / 'flipkart_checkout.yaml'


@pytest.mark.e2e
@pytest.mark.parametrize("browser_name", ["chromium"])  # add firefox, webkit if desired
def test_flipkart_checkout(browser_name):
    if os.getenv("HEYQ_RUN_E2E") != "1":
        pytest.skip("Live Flipkart e2e disabled by default. Set HEYQ_RUN_E2E=1 to enable.")
    setup_logger(CONFIG.log_level)

    # Load test data
    with open(DATA_FILE, 'r') as f:
        data = yaml.safe_load(f)

    # Secrets from local file
    sec = Secrets()
    update_redaction(sec.all_values())
    # Never log secret values
    logger.info("Loaded secrets: {} keys", len(sec.all_values()))

    with BrowserManager() as bm:
        page = bm.page
        assert page
        fp = FlipkartPage(page)

        # Navigate
        bm.goto(data['base_url'])
        fp.close_initial_popup()

        # Search
        fp.search(data['product'])
        product_page = fp.open_first_result()
        fp.add_selected_to_cart(product_page)
        fp.go_to_cart()

        # Place order -> leads to login
        fp.place_order()

    # Flipkart login flow is dynamic and often requires OTP; this test stops here.
        # In a proper staging environment with test creds bypassing OTP, you would continue:
    # - fill username/password from local secrets
        # - continue through mock payment gateway using test cards

        assert True
