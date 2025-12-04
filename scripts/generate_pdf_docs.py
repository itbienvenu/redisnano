from __future__ import annotations

from pathlib import Path

from fpdf import FPDF


SECTIONS = [
    (
        "Overview",
        "redsnano is a Redis-inspired cache that stores Python objects while "
        "continuously verifying them against the canonical data source using SHA-256 hashes. "
        "Whenever a hash mismatch is detected, the cache refreshes itself from the origin.",
    ),
    (
        "Installation",
        "Clone the repository, then install in editable mode:\n"
        "    git clone https://github.com/<org>/redsnano.git\n"
        "    cd redsnano\n"
        "    pip install -e .[api]\n\n"
        "The [api] extra installs FastAPI/uvicorn for the HTTP demo.",
    ),
    (
        "Python API",
        "from redsnano import MiniRedis, DictionaryOriginStore\n"
        "origin = DictionaryOriginStore({'user:1': {'name': 'Alice'}})\n"
        "cache = MiniRedis(origin, default_ttl=60)\n"
        "cache.get('user:1')  # fetch + store\n"
        "cache.set('user:2', {'name': 'Bob'}, ttl=30)\n"
        "cache.delete('user:2')",
    ),
    (
        "FastAPI Service",
        "Run: uvicorn redsnano.fastapi_app:app --reload\n"
        "Endpoints:\n"
        "  POST /users {username,email} -> upsert user, seed cache\n"
        "  GET /users/{username} -> serve from cache, refresh via hash\n"
        "SQLite persists origin data through SQLiteUserRepository.",
    ),
    (
        "Standalone HTTP Cache",
        "Start the bundled HTTP server for cross-language clients:\n"
        "    redsnano-server --origin-json origin.json --port 8080\n"
        "Sample requests:\n"
        "    curl http://localhost:8080/cache/user:1\n"
        "    curl -X PUT http://.../cache/user:2 -d '{\"value\": {...}}'\n"
        "    curl -X DELETE http://.../cache/user:2",
    ),
    (
        "Validating Data",
        "Every cache entry stores compute_hash(value). When GET runs, the hash is "
        "compared with origin_store.fetch_hash(key). If different, the cache fetches "
        "fresh data and overwrites the entry before returning a response.",
    ),
    (
        "Testing",
        "Unit tests cover the core cache plus FastAPI endpoints.\n"
        "    pytest\n"
        "CI can run the same command to guard against regressions.",
    ),
    (
        "Git Workflow",
        "1. git status\n"
        "2. git add <files>\n"
        "3. git commit -m \"feat: describe change\"\n"
        "4. git push origin main\n"
        "Keep commits scoped and include tests.",
    ),
    (
        "Use Cases",
        "- Protect API clients from stale DB reads while avoiding full re-fetches\n"
        "- Deliver configuration caches that validate against JSON/SQL sources\n"
        "- Provide lightweight Redis-like semantics without external services",
    ),
]


def build_pdf(output_path: Path) -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, "redsnano Guide", ln=True)
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(
        0,
        7,
        "Mini Redis-style cache with hash validation and multi-surface APIs.",
    )
    pdf.ln(5)

    for title, body in SECTIONS:
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_font("Helvetica", "", 11)
        for paragraph in body.split("\n\n"):
            pdf.multi_cell(0, 6, paragraph)
            pdf.ln(1)
        pdf.ln(2)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))


if __name__ == "__main__":
    build_pdf(Path("docs/redsnano_guide.pdf"))

