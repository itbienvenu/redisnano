from storage import cache
from validator import compute_hash
import time
import threading
from database import *

def set_key(key, value, ttl=None):
    key_hash = compute_hash(value)
    expiry = time.time() + ttl if ttl else None
    cache[key] = {
        "value": value,
        "hash": key_hash,
        "expiry": expiry
    }
    return True

# This will be getting data from cache

def get_data(key):
    if not key in cache:
        value = fetch_from_source(key)
        set_key(key, value) # to store new cache data
        return value
    
    entry: dict = cache[key]

    if entry.get('expiry') is not None and time.time() > entry['expiry']:
        del cache[key]
        value = fetch_from_source(key)
        set_key(key, value)
        return value
    value = entry['value']


    def validate_hash():
        db_hash = fetch_hash_from_source(key)
        if db_hash != entry["hash"]:
            new_value = fetch_from_source(key)
            set_key(key, new_value)

    threading.Thread(target=validate_hash).start()

    return value