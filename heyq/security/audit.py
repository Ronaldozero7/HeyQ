from __future__ import annotations
from datetime import datetime
from pathlib import Path
from loguru import logger

AUDIT_FILE = Path("logs/audit.log")
AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)


def audit(event: str, details: dict | None = None):
    ts = datetime.utcnow().isoformat()
    line = {"ts": ts, "event": event, "details": details or {}}
    # Redaction handled by logger filter upstream
    logger.info("AUDIT {}", line)
    try:
        with AUDIT_FILE.open("a") as f:
            f.write(str(line) + "\n")
    except Exception:
        pass
