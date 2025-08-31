from __future__ import annotations
import os
from dataclasses import dataclass


def env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Config:
    browser: str = os.getenv("HEYQ_BROWSER", "chromium")  # chromium, firefox, webkit
    headed: bool = env_bool("HEYQ_HEADED", False)
    # Slow down Playwright actions (milliseconds). If 0, we'll default to 250ms when headed=True.
    slow_mo: int = int(os.getenv("HEYQ_SLOW_MO", "0"))
    base_url: str = os.getenv("HEYQ_BASE_URL", "https://www.flipkart.com")
    wake_word: str = os.getenv("HEYQ_WAKE_WORD", "hey q")
    stt_engine: str = os.getenv("HEYQ_STT_ENGINE", "google")  # google|whisper
    log_level: str = os.getenv("HEYQ_LOG_LEVEL", "INFO")
    parallel: int = int(os.getenv("PYTEST_XDIST_WORKER_COUNT", "0"))


CONFIG = Config()
