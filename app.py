from database import init_db
from cache import MiniRedis

conn = init_db()
cache = MiniRedis()

def get_user(username):
    cached_user = cache.get(username)
    if cached_user:
        print("Cache Hit ")
        return cached_user

    print("Cache Miss Fetching from DB...")
    cursor = conn.cursor()
    cursor.execute("SELECT username, email FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if user:
        cache.set(username, user, ttl=10)  
        return user
    return None
print(get_user('bienvenu'))
