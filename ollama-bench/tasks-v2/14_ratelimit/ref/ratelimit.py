from collections import deque


class SlidingWindowLimiter:
    def __init__(self, limit, window):
        if limit < 1 or window <= 0: raise ValueError("bad limit/window")
        self.limit = limit; self.window = window; self.logs = {}

    def _prune(self, key, now):
        q = self.logs.get(key)
        if q is None: return None
        while q and q[0] <= now - self.window:
            q.popleft()
        if not q:
            del self.logs[key]; return None
        return q

    def allow(self, key, now):
        q = self._prune(key, now)
        n = len(q) if q else 0
        if n < self.limit:
            self.logs.setdefault(key, deque()).append(now); return True
        return False

    def remaining(self, key, now):
        q = self._prune(key, now)
        return self.limit - (len(q) if q else 0)

    def retry_after(self, key, now):
        q = self._prune(key, now)
        if not q or len(q) < self.limit: return 0.0
        return q[0] + self.window - now

    def reset(self, key):
        self.logs.pop(key, None)

    def keys(self):
        return list(self.logs.keys())
