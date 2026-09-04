class SlidingWindowLimiter:
    """A sliding-window-log rate limiter with injected time."""

    def __init__(self, limit: int, window: float):
        """
        Initialize the rate limiter.

        Args:
            limit: Maximum number of requests allowed in the window. Must be >= 1.
            window: Time window in seconds. Must be > 0.

        Raises:
            ValueError: If limit < 1 or window <= 0.
        """
        if limit < 1:
            raise ValueError("limit must be at least 1")
        if window <= 0:
            raise ValueError("window must be positive")

        self.limit = limit
        self.window = window
        self._logs = {}  # key -> list of timestamps

    def _cleanup(self, key: str, now: float):
        """Remove expired timestamps for a key and clean up empty entries."""
        if key not in self._logs:
            return

        # Remove timestamps that have expired: t <= now - window
        cutoff = now - self.window
        self._logs[key] = [t for t in self._logs[key] if t > cutoff]

        # Remove key if no timestamps remain
        if not self._logs[key]:
            del self._logs[key]

    def allow(self, key: str, now: float) -> bool:
        """
        Check if a request is allowed and record it if allowed.

        Returns True if fewer than `limit` requests for `key` exist in the window
        (now - window, now], records the request, and returns False otherwise.

        Args:
            key: Request identifier.
            now: Current time (non-decreasing per key).

        Returns:
            True if request is allowed, False otherwise.
        """
        self._cleanup(key, now)

        if key not in self._logs:
            self._logs[key] = []

        if len(self._logs[key]) < self.limit:
            self._logs[key].append(now)
            return True

        return False

    def retry_after(self, key: str, now: float) -> float:
        """
        Return seconds until the next allow() would succeed.

        Returns 0.0 if allow() would succeed now, or the time until the oldest
        in-window request expires (oldest + window - now) if at the limit.

        Args:
            key: Request identifier.
            now: Current time.

        Returns:
            Seconds to wait, or 0.0 if request can be made now.
        """
        self._cleanup(key, now)

        if key not in self._logs:
            return 0.0

        if len(self._logs[key]) < self.limit:
            return 0.0

        # At limit; return time until oldest request expires
        oldest = min(self._logs[key])
        return oldest + self.window - now

    def remaining(self, key: str, now: float) -> int:
        """
        Return the number of additional requests allowed at `now`.

        Args:
            key: Request identifier.
            now: Current time.

        Returns:
            Number of requests that can be made before hitting the limit.
        """
        self._cleanup(key, now)

        if key not in self._logs:
            return self.limit

        return self.limit - len(self._logs[key])

    def reset(self, key: str):
        """
        Forget all requests for a key.

        Args:
            key: Request identifier.
        """
        if key in self._logs:
            del self._logs[key]

    def keys(self) -> list:
        """
        Return a list of currently tracked keys.

        Returns:
            List of keys with non-empty request logs.
        """
        return list(self._logs.keys())
