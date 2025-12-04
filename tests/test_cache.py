from __future__ import annotations

import time
from pathlib import Path

from redsnano.cache import MiniRedis
from redsnano.origin import DictionaryOriginStore
from redsnano.persistence import JSONPersistence


def build_cache(tmp_path: Path, seed: dict[str, object]) -> MiniRedis:
    origin = DictionaryOriginStore(seed)
    persistence = JSONPersistence(tmp_path / "cache.json")
    return MiniRedis(origin, persistence=persistence, validate_async=False)


def test_get_and_set_roundtrip(tmp_path):
    cache = build_cache(tmp_path, {"user:1": {"name": "Alice"}})

    value = cache.get("user:1")
    assert value == {"name": "Alice"}

    cache.set("user:2", {"name": "Bob"}, ttl=5)
    assert cache.get("user:2") == {"name": "Bob"}
    assert set(cache.keys()) == {"user:1", "user:2"}


def test_ttl_expiration(tmp_path):
    cache = build_cache(tmp_path, {"session": {"token": "abc"}})
    cache.set("session", {"token": "abc"}, ttl=0.05)
    assert cache.get("session") == {"token": "abc"}
    time.sleep(0.06)
    cache.origin_store.update("session", {"token": "refetched"})  # type: ignore[attr-defined]
    assert cache.get("session") == {"token": "refetched"}


def test_hash_mismatch_triggers_refresh(tmp_path):
    cache = build_cache(tmp_path, {"user:1": {"name": "Alice"}})
    assert cache.get("user:1") == {"name": "Alice"}

    cache.origin_store.update("user:1", {"name": "Bob"})  # type: ignore[attr-defined]
    cache.get("user:1")  # triggers validation
    assert cache.get("user:1") == {"name": "Bob"}

