from __future__ import annotations

import threading
import time
from typing import Any, Dict, Optional

from .cache_types import CacheEntry
from .hashing import compute_hash
from .origin import OriginStore
from .persistence import JSONPersistence


class MiniRedis:
    """
    Core cache that mirrors Redis-like GET/SET semantics and keeps data
    fresh by comparing hashes with the origin store.
    """

    def __init__(
        self,
        origin_store: OriginStore,
        *,
        persistence: Optional[JSONPersistence] = None,
        default_ttl: Optional[float] = None,
        validate_async: bool = True,
    ):
        self.origin_store = origin_store
        self.persistence = persistence or JSONPersistence("cache.json")
        self.default_ttl = default_ttl
        self.validate_async = validate_async
        self._lock = threading.RLock()
        self._store: Dict[str, CacheEntry] = {
            key: CacheEntry.from_serialized(value)
            for key, value in self.persistence.load().items()
        }

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        expire_at = time.time() + ttl if ttl else None
        entry = CacheEntry(value=value, hash=compute_hash(value), expire_at=expire_at)
        with self._lock:
            self._store[key] = entry
            self._persist()

    def get(self, key: str, *, ttl: Optional[float] = None) -> Any | None:
        with self._lock:
            entry = self._store.get(key)

        if entry and entry.is_expired(time.time()):
            self.delete(key)
            entry = None

        if entry is None:
            value = self._fetch_from_origin(key)
            if value is None:
                return None
            self.set(key, value, ttl=ttl or self.default_ttl)
            return value

        entry = self._schedule_validation(key, entry)
        if entry is None:
            value = self._fetch_from_origin(key)
            if value is None:
                return None
            self.set(key, value, ttl=ttl or self.default_ttl)
            return value
        return entry.value

    def delete(self, key: str) -> None:
        with self._lock:
            if key in self._store:
                del self._store[key]
                self._persist()

    def keys(self) -> list[str]:
        with self._lock:
            return list(self._store.keys())

    def _fetch_from_origin(self, key: str) -> Any | None:
        return self.origin_store.fetch_value(key)

    def _schedule_validation(self, key: str, entry: CacheEntry) -> CacheEntry | None:
        if self.validate_async:
            thread = threading.Thread(
                target=self._validate_hash, args=(key, entry), daemon=True
            )
            thread.start()
            return entry

        self._validate_hash(key, entry)
        with self._lock:
            return self._store.get(key)

    def _validate_hash(self, key: str, entry: CacheEntry) -> None:
        origin_hash = self.origin_store.fetch_hash(key)
        if origin_hash is None:
            return
        if origin_hash != entry.hash:
            value = self._fetch_from_origin(key)
            if value is None:
                self.delete(key)
                return
            ttl_remaining = (
                entry.expire_at - time.time() if entry.expire_at else self.default_ttl
            )
            ttl_remaining = max(ttl_remaining, 0) if ttl_remaining else None
            self.set(key, value, ttl=ttl_remaining)

    def _persist(self) -> None:
        serializable = {key: entry.to_serialized() for key, entry in self._store.items()}
        self.persistence.save(serializable)

