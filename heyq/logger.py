from __future__ import annotations
from loguru import logger
import os

# Configure Loguru with redaction filter
SECRET_MASK = "***"
_current_filter: SecretFilter | None = None


class SecretFilter:
    def __init__(self, secrets: list[str] | None = None):
        self.secrets = secrets or []

    def __call__(self, record):
        message = record["message"]
        for s in self.secrets:
            if s:
                message = message.replace(s, SECRET_MASK)
        record["message"] = message
        return True


def setup_logger(level: str = "INFO", secrets: list[str] | None = None):
    logger.remove()
    global _current_filter
    _current_filter = SecretFilter(secrets)
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=level,
        filter=_current_filter,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        backtrace=False,
        diagnose=False,
    )
    return logger


def update_redaction(secrets: list[str]):
    """Update the global redaction filter with new secrets to mask."""
    global _current_filter
    if _current_filter is None:
        _current_filter = SecretFilter(secrets)
        return
    # Extend unique secrets
    seen = set(_current_filter.secrets)
    for s in secrets:
        if s and s not in seen:
            _current_filter.secrets.append(s)
            seen.add(s)
