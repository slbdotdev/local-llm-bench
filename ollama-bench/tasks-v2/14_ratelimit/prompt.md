Create `ratelimit.py` in the current directory with a class `SlidingWindowLimiter(limit: int, window: float)` implementing a sliding-window-log rate limiter with injected time (no calls to `time.time()`; all times are floats passed in by the caller and are non-decreasing per key).

- `allow(key, now) -> bool`: return True and record the request if fewer than `limit` requests for `key` have been recorded with timestamp `t` such that `now - window < t <= now` (i.e. a request exactly `window` seconds old has expired). Return False and record nothing otherwise.
- `retry_after(key, now) -> float`: seconds until the next `allow(key, ...)` would succeed; `0.0` if it would succeed now. When at the limit, this is the time until the oldest in-window request expires: `oldest + window - now`.
- `remaining(key, now) -> int`: how many more requests would be allowed at `now`.
- `reset(key)`: forget all requests for `key`.
- Memory must not grow without bound: expired timestamps must be dropped from the log on each call, and keys with empty logs must be removed. Expose `def keys(self) -> list` returning the currently tracked keys.
- `limit < 1` or `window <= 0` raises `ValueError`.

Example with `SlidingWindowLimiter(2, 10.0)`: `allow("a", 0.0)` True, `allow("a", 5.0)` True, `allow("a", 9.0)` False, `retry_after("a", 9.0) == 1.0`, `allow("a", 10.0)` True (the request at 0.0 has expired exactly at 10.0), `remaining("a", 10.0) == 0`.

Write a few quick checks of your own and run them with `python`, then reply "done".
