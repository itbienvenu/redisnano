from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any, Dict, Optional, Protocol

from .hashing import compute_hash


class OriginStore(Protocol):
    """Interface that canonical data sources must implement."""

    def fetch_value(self, key: str) -> Any | None:  # pragma: no cover - protocol
        ...

    def fetch_hash(self, key: str) -> str | None:  # pragma: no cover - protocol
        ...


class DictionaryOriginStore:
    """
    Simple in-memory origin store useful for demos and tests.
    """

    def __init__(self, seed: Optional[Dict[str, Any]] = None):
        self._data: Dict[str, Any] = seed.copy() if seed else {}
        self._lock = threading.RLock()

    def update(self, key: str, value: Any) -> None:
        with self._lock:
            self._data[key] = value

    def fetch_value(self, key: str) -> Any | None:
        with self._lock:
            return self._data.get(key)

    def fetch_hash(self, key: str) -> str | None:
        value = self.fetch_value(key)
        return compute_hash(value) if value is not None else None


class JSONFileOriginStore:
    """
    Origin backed by a JSON file, ideal for lightweight demos.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")
        self._lock = threading.RLock()

    def _load(self) -> Dict[str, Any]:
        with self._lock:
            content = self.path.read_text(encoding="utf-8") or "{}"
            return json.loads(content)

    def fetch_value(self, key: str) -> Any | None:
        data = self._load()
        return data.get(key)

    def fetch_hash(self, key: str) -> str | None:
        value = self.fetch_value(key)
        return compute_hash(value) if value is not None else None

