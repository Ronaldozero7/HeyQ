from __future__ import annotations
import os
from pathlib import Path
import pytest

from heyq.logger import setup_logger
from heyq.config import CONFIG


def pytest_configure(config):
    # Ensure logs are visible and secrets are masked
    setup_logger(CONFIG.log_level)


def pytest_addoption(parser):
    parser.addoption("--headed", action="store_true", default=CONFIG.headed, help="Run headed browser")
    parser.addoption("--browser", action="store", default=CONFIG.browser, help="Browser engine")


def pytest_html_results_summary(prefix, summary, postfix):
    # If pytest-html is installed, this hook will be called. Attach voice trace details if present.
    trace = Path("heyq/reports/voice_trace.jsonl")
    if trace.exists():
        try:
            last_lines = trace.read_text().strip().splitlines()[-5:]
            content = "\n".join(last_lines)
            prefix.extend(["Voice command trace (last 5):\n", content])
        except Exception:
            pass
