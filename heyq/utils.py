from __future__ import annotations
import yaml
from pathlib import Path
from typing import Any


def load_yaml(path: str | Path) -> dict[str, Any]:
    with open(path, 'r') as f:
        return yaml.safe_load(f)
