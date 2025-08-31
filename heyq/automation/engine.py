from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_fixed
from loguru import logger
from playwright.sync_api import sync_playwright, Browser, Page

from ..config import CONFIG


@dataclass
class BrowserConfig:
    name: str = CONFIG.browser  # chromium|firefox|webkit|chrome|edge|safari
    headed: bool = CONFIG.headed
    channel: Optional[str] = None  # e.g., 'msedge', 'chrome'
    slow_mo: Optional[int] = None  # ms; if None uses CONFIG.slow_mo (or 250 when headed)


class BrowserManager:
    def __init__(self, cfg: BrowserConfig | None = None, *, headed: Optional[bool] = None, browser: Optional[str] = None, channel: Optional[str] = None, slow_mo: Optional[int] = None):
        base = cfg or BrowserConfig()
        if headed is not None:
            base.headed = headed
        if browser is not None:
            base.name = browser
        if channel is not None:
            base.channel = channel
        if slow_mo is not None:
            base.slow_mo = slow_mo
        self.cfg = base
        self._pw = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    def __enter__(self):
        self._pw = sync_playwright().start()
        name, channel = self._normalize(self.cfg.name, self.cfg.channel)
        # Determine slow_mo: prefer explicit, else CONFIG.slow_mo, else 250ms when headed
        slow_mo = self.cfg.slow_mo if self.cfg.slow_mo is not None else (CONFIG.slow_mo or (250 if self.cfg.headed else 0))
        launch_args = {"headless": (not self.cfg.headed)}
        if slow_mo and slow_mo > 0:
            launch_args["slow_mo"] = slow_mo
        if channel:
            launch_args["channel"] = channel
        self.browser = getattr(self._pw, name).launch(**launch_args)
        context = self.browser.new_context()
        self.page = context.new_page()
        logger.info("Launched {} (headed={}, channel={}, slow_mo={}ms)", name, self.cfg.headed, channel, launch_args.get("slow_mo", 0))
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if self.browser:
                self.browser.close()
        finally:
            if self._pw:
                self._pw.stop()

    def goto(self, url: str):
        assert self.page
        logger.info("Navigate to {}", url)
        self.page.goto(url, wait_until="domcontentloaded", timeout=60000)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def fill(self, selector: str, text: str):
        assert self.page
        # Ensure we always pass a string to Playwright's fill
        self.page.fill(selector, str(text), timeout=30000)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def click(self, selector: str):
        assert self.page
        self.page.click(selector, timeout=30000)

    def text_content(self, selector: str) -> str | None:
        assert self.page
        el = self.page.query_selector(selector)
        return el.text_content() if el else None

    @staticmethod
    def _normalize(name: str, channel: Optional[str]):
        n = name.lower()
        if n in {"chrome", "google-chrome"}:
            return "chromium", channel or "chrome"
        if n in {"edge", "msedge"}:
            return "chromium", channel or "msedge"
        if n in {"safari"}:
            return "webkit", channel
        if n in {"firefox", "chromium", "webkit"}:
            return n, channel
        # default to chromium
        return "chromium", channel
