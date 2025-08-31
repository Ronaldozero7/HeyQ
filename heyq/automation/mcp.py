from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
from loguru import logger
from playwright.sync_api import sync_playwright, Page
from ..config import CONFIG


@dataclass
class MCPResult:
    ok: bool
    data: Dict[str, Any] | None = None
    error: str | None = None


class PlaywrightMCP:
    """A tiny, local MCP-like helper that exposes probe and basic actions.
    Not a network service; can be invoked from API endpoints.
    """
    def __init__(self, *, headed: bool = False, browser: str = 'chromium', channel: Optional[str] = None, slow_mo: Optional[int] = None):
        self._pw = None
        self._browser = None
        self._context = None
        self.page: Optional[Page] = None
        self.headed = headed
        self.browser = browser
        self.channel = channel
        # None means use CONFIG.slow_mo, else explicit value
        self.slow_mo = slow_mo

    def __enter__(self):
        self._pw = sync_playwright().start()
        # Resolve slow_mo: prefer explicit, then CONFIG, else 250ms when headed
        effective_slow = self.slow_mo if self.slow_mo is not None else (CONFIG.slow_mo or (250 if self.headed else 0))
        launch_args = { 'headless': (not self.headed) }
        if effective_slow and effective_slow > 0:
            launch_args['slow_mo'] = effective_slow
        if self.channel:
            launch_args['channel'] = self.channel
        self._browser = getattr(self._pw, self.browser).launch(**launch_args)
        self._context = self._browser.new_context()
        self.page = self._context.new_page()
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if self._context: self._context.close()
            if self._browser: self._browser.close()
        finally:
            if self._pw: self._pw.stop()

    # --- basic ---
    def navigate(self, url: str) -> MCPResult:
        try:
            assert self.page
            self.page.goto(url, wait_until='domcontentloaded', timeout=60000)
            return MCPResult(ok=True, data={'url': url})
        except Exception as e:
            return MCPResult(ok=False, error=str(e))

    def exists(self, selector: str) -> MCPResult:
        try:
            assert self.page
            count = self.page.locator(selector).count()
            return MCPResult(ok=True, data={'selector': selector, 'count': count})
        except Exception as e:
            return MCPResult(ok=False, error=str(e))

    def first_visible(self, selectors: list[str]) -> MCPResult:
        try:
            assert self.page
            for s in selectors:
                try:
                    loc = self.page.locator(s).first
                    if loc.is_visible():
                        return MCPResult(ok=True, data={'selector': s})
                except Exception:
                    continue
            return MCPResult(ok=True, data={'selector': None})
        except Exception as e:
            return MCPResult(ok=False, error=str(e))

    def fill(self, selector: str, text: str) -> MCPResult:
        try:
            assert self.page
            loc = self.page.locator(selector).first
            loc.wait_for(state='visible', timeout=20000)
            loc.fill(str(text), timeout=20000)
            return MCPResult(ok=True)
        except Exception as e:
            return MCPResult(ok=False, error=str(e))

    def click(self, selector: str) -> MCPResult:
        try:
            assert self.page
            self.page.locator(selector).first.click(timeout=20000)
            return MCPResult(ok=True)
        except Exception as e:
            return MCPResult(ok=False, error=str(e))
