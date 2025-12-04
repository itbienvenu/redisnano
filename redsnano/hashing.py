from __future__ import annotations

import hashlib
import json
from typing import Any


def _serialize(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError):
        return repr(value)


def compute_hash(value: Any) -> str:
    """Return a deterministic SHA-256 hash for the provided value."""
    serialized = _serialize(value)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

