from __future__ import annotations

import argparse

from .cache import MiniRedis
from .origin import JSONFileOriginStore
from .persistence import JSONPersistence
from .server import MiniRedisHTTPServer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the redsnano HTTP server.")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8777)
    parser.add_argument(
        "--origin-json",
        default="origin.json",
        help="Path to a JSON file representing the canonical data source.",
    )
    parser.add_argument(
        "--cache-file",
        default="cache.json",
        help="Path to persist cache entries.",
    )
    parser.add_argument(
        "--default-ttl",
        type=float,
        default=60,
        help="Default TTL (seconds) for new keys when not provided explicitly.",
    )
    return parser


def run_server() -> None:
    parser = build_parser()
    args = parser.parse_args()

    origin_store = JSONFileOriginStore(args.origin_json)
    cache = MiniRedis(
        origin_store,
        persistence=JSONPersistence(args.cache_file),
        default_ttl=args.default_ttl,
    )

    server = MiniRedisHTTPServer((args.host, args.port), cache)
    print(f"redsnano server listening on http://{args.host}:{args.port}")  # noqa: T201
    try:
        server.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover - manual shutdown
        print("Shutting down redsnano server...")  # noqa: T201
        server.shutdown()

