import json
import time

class MiniRedis:
    def __init__(self):
        self.store = {}

    def set(self, key, value, ttl=None):
        expire_time = time.time() + ttl if ttl else None
        self.store[key] = {"value": value, "expire": expire_time}
        # Save to file
        with open("cache.json", "w") as f:
            json.dump(self.store, f)

    def get(self, key):
        try:

            with open("cache.json", "r") as f:
                self.store.update(json.load(f))
        except FileNotFoundError:
            self.store = {}

        item = self.store.get(key)
        if not item:
            return None

        expire = item.get("expire")
        if expire and time.time() > expire:
            del self.store[key]
            with open("cache.json", "w") as f:
                json.dump(self.store, f)
            return None

        return item.get("value")
