from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, MutableMapping, TypedDict


class CacheEntrySerialized(TypedDict):
    value: Any
    hash: str
    expire_at: float | None


@dataclass
class CacheEntry:
    value: Any
    hash: str
    expire_at: float | None = None

    def to_serialized(self) -> CacheEntrySerialized:
        return asdict(self)  # type: ignore[return-value]

    @classmethod
    def from_serialized(cls, data: MutableMapping[str, Any]) -> "CacheEntry":
        return cls(
            value=data["value"],
            hash=data["hash"],
            expire_at=data.get("expire_at"),
        )

    def is_expired(self, now: float) -> bool:
        return self.expire_at is not None and now >= self.expire_at

