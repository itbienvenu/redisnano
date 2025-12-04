from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Tuple
from urllib.parse import parse_qs, urlparse

from .cache import MiniRedis


class MiniRedisHTTPRequestHandler(BaseHTTPRequestHandler):
    cache: MiniRedis  # injected before serving

    def _send_json(self, payload, status: int = 200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        key = self._extract_key()
        if not key:
            self._send_json({"error": "Key not provided"}, status=400)
            return
        value = self.cache.get(key)
        if value is None:
            self._send_json({"error": "Key not found"}, status=404)
            return
        self._send_json({"key": key, "value": value})

    def do_PUT(self):
        key = self._extract_key()
        if not key:
            self._send_json({"error": "Key not provided"}, status=400)
            return
        content_length = int(self.headers.get("Content-Length", "0"))
        data = json.loads(self.rfile.read(content_length) or "{}")
        value = data.get("value")
        ttl = data.get("ttl")
        self.cache.set(key, value, ttl=ttl)
        self._send_json({"key": key, "value": value, "ttl": ttl})

    def do_DELETE(self):
        key = self._extract_key()
        if not key:
            self._send_json({"error": "Key not provided"}, status=400)
            return
        self.cache.delete(key)
        self._send_json({"key": key, "deleted": True})

    def log_message(self, format, *args):  # pragma: no cover - noisy in tests
        return

    def _extract_key(self) -> str | None:
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/cache/"):
            return None
        key = parsed.path[len("/cache/") :]
        query = parse_qs(parsed.query or "")
        ttl = query.get("ttl")
        if ttl:
            try:
                ttl_value = float(ttl[0])
                self.cache.default_ttl = ttl_value
            except ValueError:
                pass
        return key or None


class MiniRedisHTTPServer(ThreadingHTTPServer):
    def __init__(self, server_address: Tuple[str, int], cache: MiniRedis):
        handler = type(
            "HandlerWithCache",
            (MiniRedisHTTPRequestHandler,),
            {"cache": cache},
        )
        super().__init__(server_address, handler)

