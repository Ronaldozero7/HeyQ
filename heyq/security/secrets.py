from __future__ import annotations
from pathlib import Path
import yaml
from typing import Any, Dict

DEFAULT_SECRETS_FILE = Path("config/secrets.yaml")


class Secrets:
    def __init__(self, path: Path | None = None):
        self.path = path or DEFAULT_SECRETS_FILE
        self._cache: Dict[str, Any] = {}
        if self.path.exists():
            with open(self.path, 'r') as f:
                self._cache = yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._cache.get(key, default)

    def all_values(self) -> list[str]:
        vals = []
        def walk(v):
            if isinstance(v, dict):
                for vv in v.values():
                    walk(vv)
            elif isinstance(v, list):
                for vv in v:
                    walk(vv)
            elif isinstance(v, str):
                vals.append(v)
        walk(self._cache)
        return vals
