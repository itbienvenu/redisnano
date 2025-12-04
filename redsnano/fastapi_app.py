from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

from .cache import MiniRedis
from .origin_sqlite import SQLiteUserOriginStore, SQLiteUserRepository
from .persistence import JSONPersistence


class UserPayload(BaseModel):
    username: str
    email: EmailStr


def create_app(
    db_path: str | Path = "users.db",
    cache_path: str | Path = "cache_fastapi.json",
    *,
    default_ttl: float = 60,
) -> FastAPI:
    db_path = Path(db_path)
    cache_path = Path(cache_path)

    origin = SQLiteUserOriginStore(db_path)
    repo = SQLiteUserRepository(db_path)
    cache = MiniRedis(
        origin,
        persistence=JSONPersistence(cache_path),
        default_ttl=default_ttl,
        validate_async=False,
    )

    app = FastAPI(title="redsnano-fastapi", version="0.1.0")
    app.state.cache = cache
    app.state.repo = repo

    @app.post("/users", status_code=201)
    def register_user(payload: UserPayload):
        record = repo.upsert_user(payload.username, payload.email)
        cache.set(payload.username, record, ttl=default_ttl)
        return record

    @app.get("/users/{username}")
    def get_user(username: str):
        value = cache.get(username, ttl=default_ttl)
        if value is None:
            raise HTTPException(status_code=404, detail="User not found")
        return value

    return app


app = create_app()

