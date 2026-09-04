Create `lru.py` in the current directory containing a class `LRUCache`:

- `LRUCache(capacity: int)`; raise `ValueError` if capacity < 1.
- `get(key)` returns the stored value, or `-1` if absent. A successful `get` marks the key as most recently used.
- `put(key, value)` inserts or updates; updating an existing key also marks it most recently used. When inserting a new key beyond capacity, evict the least recently used key first.
- `__len__` returns the number of stored keys.
- `keys()` returns a list of keys ordered from least recently used to most recently used.

Both `get` and `put` must be O(1) on average (use `collections.OrderedDict` or your own doubly linked list plus dict; do not scan lists).

Write a few quick checks of your own and run them with `python`, then reply "done".
