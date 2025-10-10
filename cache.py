import time
import json

class MiniRedis:
    def __init__(self):
        self.store = {}

    def set(self, key, value, ttl=None):
        expire_time = time.time() + ttl if ttl else None
        self.store[key] = (value, expire_time)
        #store dataindb
        with open("cache.json",'a') as f:
            json.dump(self.store, f)

    def get(self, key):
        try:
            with open("cache.json", "r") as f:
                self.store.update(json.load(f))
            return self.store   
        except FileNotFoundError:
            cache = {}

    def delete(self, key):
        if key in self.store:
            del self.store[key]
