from storage import cache, load_cache, save_cache
from commands import set_key, get_data

# load_cache()

set_key("blog:40", {"title": "Bienve", "content": "This is the second test"}, ttl=60)

# print(load_cache())

save_cache()
