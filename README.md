# redsnano

redsnano is a Redis-inspired cache focused on guaranteeing that cached data
matches the canonical source by comparing hashes instead of re-fetching entire
records on every request. Whenever hashes diverge, redsnano automatically refreshes
the cache with the authoritative value.

## Features
- Hash-based validation to quickly detect stale entries
- TTL per key plus persistent storage on disk
- Pluggable origin stores (in-memory, JSON file, custom implementations)
- HTTP API for cross-language usage
- Packaged for `pip install redsnano` workflows

## Installation
```
pip install -e .
```

## Python Usage
```python
from redsnano import MiniRedis, DictionaryOriginStore

origin = DictionaryOriginStore({"user:1": {"name": "Alice"}})
cache = MiniRedis(origin, default_ttl=120)

cache.get("user:1")          # fetches from origin and stores
cache.set("user:2", {"name": "Bob"}, ttl=30)
cache.delete("user:2")
```

## Cross-language HTTP API
Start the server:
```
redsnano-server --origin-json origin.json --port 8080
```
Then from any language:
```
curl http://localhost:8080/cache/user:1
curl -X PUT http://localhost:8080/cache/user:2 -d '{"value": {"name": "Bob"}}'
curl -X DELETE http://localhost:8080/cache/user:2
```

## Extending with Custom Origin Stores
Implement the `OriginStore` protocol:
```python
from redsnano.origin import OriginStore
from redsnano.hashing import compute_hash

class PostgresOrigin(OriginStore):
    def __init__(self, connection):
        self.conn = connection

    def fetch_value(self, key: str):
        row = self.conn.fetchrow("SELECT payload FROM cache_source WHERE key=$1", key)
        return row["payload"] if row else None

    def fetch_hash(self, key: str):
        value = self.fetch_value(key)
        return compute_hash(value) if value else None
```

## Testing
```
pytest
```

## FastAPI Example
redsnano ships with a FastAPI app that registers users and reads them back via the cache-first flow:
```
uvicorn redsnano.fastapi_app:app --reload
```
Endpoints:
- `POST /users` with `{"username": "...", "email": "..."}` registers or updates a user.
- `GET /users/{username}` first checks the cache and only falls back to SQLite when necessary.
Hashes ensure the cache refreshes as soon as the canonical record changes.

## Example Use Cases
- API response caching while guaranteeing synchronization with a relational DB
- Edge cache for configuration documents stored in cloud object storage
- Local developer cache that mirrors production responses without stale data

## Git Workflow Primer
1. `git status` – check pending work
2. `git add <files>` – stage changes
3. `git commit -m "feat: describe change"` – create a commit
4. `git push origin main` – ship the update

Keeping commits small and descriptive makes the repository easy for collaborators
to navigate.

