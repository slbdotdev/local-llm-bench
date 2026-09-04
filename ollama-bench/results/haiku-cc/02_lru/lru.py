from collections import OrderedDict


class LRUCache:
    """
    Least Recently Used Cache with O(1) average time complexity for get and put operations.
    """

    def __init__(self, capacity: int):
        """
        Initialize the LRU cache with the given capacity.

        Args:
            capacity: Maximum number of items to store. Must be >= 1.

        Raises:
            ValueError: If capacity < 1.
        """
        if capacity < 1:
            raise ValueError("Capacity must be at least 1")
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        """
        Get the value associated with the key.

        Returns the stored value if the key exists, otherwise returns -1.
        Accessing a key marks it as most recently used.

        Time complexity: O(1) on average
        """
        if key not in self.cache:
            return -1
        # Move to end to mark as most recently used
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        """
        Insert or update a key-value pair.

        If the key already exists, update its value and mark it as most recently used.
        If adding a new key would exceed capacity, evict the least recently used key first.

        Time complexity: O(1) on average
        """
        if key in self.cache:
            # Update existing key and move to end (most recently used)
            self.cache[key] = value
            self.cache.move_to_end(key)
        else:
            # Add new key
            if len(self.cache) >= self.capacity:
                # Remove least recently used (first item in OrderedDict)
                self.cache.popitem(last=False)
            self.cache[key] = value

    def __len__(self):
        """Return the number of items currently stored in the cache."""
        return len(self.cache)

    def keys(self):
        """
        Return a list of keys ordered from least recently used to most recently used.
        """
        return list(self.cache.keys())
