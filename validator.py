import hashlib, json

def compute_hash(value):
    serialized = json.dumps(value, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()

