from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from redsnano.fastapi_app import create_app
from redsnano.origin_sqlite import SQLiteUserRepository


def build_client(tmp_path: Path) -> TestClient:
    db_path = tmp_path / "users.db"
    cache_path = tmp_path / "cache.json"
    app = create_app(db_path=db_path, cache_path=cache_path, default_ttl=1)
    return TestClient(app)


def test_register_and_fetch_user(tmp_path):
    client = build_client(tmp_path)

    resp = client.post("/users", json={"username": "alice", "email": "alice@mail.com"})
    assert resp.status_code == 201
    assert resp.json() == {"username": "alice", "email": "alice@mail.com"}

    resp = client.get("/users/alice")
    assert resp.status_code == 200
    assert resp.json()["email"] == "alice@mail.com"


def test_cache_serves_before_db(tmp_path):
    db_path = tmp_path / "users.db"
    client = build_client(tmp_path)
    repo = SQLiteUserRepository(db_path)

    client.post("/users", json={"username": "bob", "email": "bob@mail.com"})

    repo.upsert_user("bob", "new@mail.com")
    resp = client.get("/users/bob")
    assert resp.status_code == 200
    assert resp.json()["email"] == "new@mail.com"

