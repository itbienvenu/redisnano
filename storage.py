import json, os

cache: dict = {}

def save_cache():
    with open("cache.json", "w") as f:
        json.dump(cache, f, indent=2)

def load_cache():
    global cache
    try:
        with open("cache.json", "r") as f:
            cache.update(json.load(f))
        return cache    
    except FileNotFoundError:
        cache = {}