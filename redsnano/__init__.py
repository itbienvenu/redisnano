"""
redsnano
========

Mini Redis-inspired cache with hash-based validation against a canonical
data source.  The package exposes a Python API, a lightweight HTTP server
for multi-language clients, and helper origin store implementations.
"""

from .cache import MiniRedis, CacheEntry
from .origin import OriginStore, DictionaryOriginStore, JSONFileOriginStore
from .origin_sqlite import SQLiteUserOriginStore, SQLiteUserRepository
from .persistence import JSONPersistence
from .hashing import compute_hash
from .fastapi_app import create_app

__all__ = [
    "MiniRedis",
    "CacheEntry",
    "OriginStore",
    "DictionaryOriginStore",
    "JSONFileOriginStore",
    "JSONPersistence",
    "compute_hash",
    "SQLiteUserOriginStore",
    "SQLiteUserRepository",
    "create_app",
]

