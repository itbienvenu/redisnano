from commands import set_key, get_data
from storage import cache


# set_key("blog:42", {"title": "Hello", "content": "Redis mini"}, ttl=60)
print(get_data('blog:42'))
# print(cache)
