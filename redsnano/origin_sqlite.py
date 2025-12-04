from __future__ import annotations

import sqlite3
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from .hashing import compute_hash
from .origin import OriginStore


def _dict_from_row(row) -> Dict[str, Any] | None:
    if not row:
        return None
    return {"username": row[0], "email": row[1]}


class SQLiteUserOriginStore(OriginStore):
    """Origin store backed by a SQLite table named ``users``."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self._lock = threading.RLock()
        self._ensure_schema()

    def fetch_value(self, key: str):
        with self._lock, sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT username, email FROM users WHERE username=?", (key,)
            ).fetchone()
        return _dict_from_row(row)

    def fetch_hash(self, key: str):
        value = self.fetch_value(key)
        return compute_hash(value) if value else None

    def _ensure_schema(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    email TEXT NOT NULL
                )
                """
            )
            conn.commit()


@dataclass
class SQLiteUserRepository:
    """Simple repository used by the FastAPI layer to mutate data."""

    db_path: Path

    def __post_init__(self):
        self.store = SQLiteUserOriginStore(self.db_path)

    def upsert_user(self, username: str, email: str) -> Dict[str, Any]:
        payload = {"username": username, "email": email}
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO users(username, email)
                VALUES(?, ?)
                ON CONFLICT(username) DO UPDATE SET email=excluded.email
                """,
                (username, email),
            )
            conn.commit()
        return payload

    def get_user(self, username: str) -> Dict[str, Any] | None:
        return self.store.fetch_value(username)

