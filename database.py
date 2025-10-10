import hashlib
import json


db = {
    "blog:42": {"title": "Hello", "content": "Redis mini project"},
    "blog:43": {"title": "Another blog", "content": "More content"}
}

def fetch_from_source(key):
    return db.get(key)

def fetch_hash_from_source(key):
    value = db.get(key)
    if value is None:
        return None
    serialized = json.dumps(value, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()
