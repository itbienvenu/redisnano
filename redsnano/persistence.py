from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .cache_types import CacheEntrySerialized


class JSONPersistence:
    """
    Disk persistence layer for cache contents.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self) -> Dict[str, CacheEntrySerialized]:
        if not self.path.exists():
            return {}
        content = self.path.read_text(encoding="utf-8")
        return json.loads(content) if content else {}

    def save(self, data: Dict[str, CacheEntrySerialized]) -> None:
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

