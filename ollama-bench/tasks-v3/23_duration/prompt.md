Create `duration.py` in the current directory with two functions, `format_duration(total_seconds: int) -> str` and `parse_duration(s: str) -> int`, that convert between a non-negative integer number of seconds and a compact canonical duration string.

**Canonical format.** Break `total_seconds` into days/hours/minutes/seconds:
```
d, rem = divmod(total_seconds, 86400)
h, rem = divmod(rem, 3600)
m, s   = divmod(rem, 60)
```
Write each of `d`, `h`, `m`, `s` that is **nonzero** as `<value><unit>` (units `d`, `h`, `m`, `s`, lowercase, no spaces), in that fixed order (days, then hours, then minutes, then seconds), concatenated with no separators and no unit repeated or omitted-then-reused. A component that is zero is simply left out entirely. If `total_seconds == 0` (so all four components are zero), the result is exactly `"0s"` (never `""`).

Examples:
- `format_duration(0) == "0s"`
- `format_duration(45) == "45s"`
- `format_duration(3600) == "1h"`
- `format_duration(3661) == "1h1m1s"`
- `format_duration(90061) == "1d1h1m1s"` (90061 = 86400 + 3600 + 60 + 1)
- `format_duration(86400) == "1d"` (no trailing `0h0m0s`)

`parse_duration(s)` must accept **only** strings that are themselves valid canonical output of `format_duration` for some `total_seconds >= 0`, and return that integer; otherwise it must raise `ValueError`. Concretely this means:
- Components, if present, must appear in the order d, h, m, s; a unit may appear at most once; no other characters (spaces, uppercase, extra letters) are allowed.
- Each component's numeral has no leading zeros: it is exactly `str(int(...))` for its value, i.e. `"0"` alone is never a valid numeral for a present component, and `"01h"` etc. is invalid.
- `h` (if present) is in `1..23`, `m` (if present) is in `1..59`, `s` (if present) is in `1..59`, `d` (if present) is any positive integer with no upper bound. (These ranges follow from the `divmod` breakdown: an hour value of 24 or more, or a minute/second value of 60 or more, could never come out of `format_duration`.)
- A component that would be zero must be omitted, **except** the special case `"0s"` representing zero total seconds; e.g. `"1d0s"`, `"1d0h5m"`, `""`, `"0m"`, `"0d1h"` are all invalid.

So for every `n >= 0`, `parse_duration(format_duration(n)) == n`, and `parse_duration` rejects every string that is not exactly some `format_duration(n)` output.

Examples: `parse_duration("1d1h1m1s") == 90061`; `parse_duration("0s") == 0`; `parse_duration("1h") == 3600`; `parse_duration("24h")`, `parse_duration("1h1d")`, `parse_duration("00s")`, `parse_duration("1d0s")`, `parse_duration("")`, and `parse_duration("5")` all raise `ValueError`.

Write a few quick checks of your own and run them with `python`, then reply "done".
