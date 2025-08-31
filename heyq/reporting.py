from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json
from loguru import logger

TRACE_FILE = Path("heyq/reports/voice_trace.jsonl")
TRACE_FILE.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class VoiceTrace:
    ts: str
    raw: str
    intent: str
    entities: dict


SENSITIVE_KEYS = {"password", "passcode", "card_number", "card_cvv", "cvv"}


def record_voice_trace(raw: str, intent: str, entities: dict):
    vt = VoiceTrace(datetime.utcnow().isoformat(), raw, intent, entities)
    # Redact sensitive values
    redacted = asdict(vt)
    ents = redacted.get("entities", {})
    for k in list(ents.keys()):
        if k.lower() in SENSITIVE_KEYS:
            ents[k] = "***"
    try:
        with TRACE_FILE.open("a") as f:
            f.write(json.dumps(redacted) + "\n")
    except Exception as e:
        logger.warning("Failed to write voice trace: {}", e)
