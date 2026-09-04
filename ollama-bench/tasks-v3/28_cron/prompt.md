Create `cronsched.py` in the current directory: a cron-expression parser and scheduler. Standard library only (`re`, `datetime`).

Define an exception `CronError(ValueError)` and three functions.

## `parse_cron(spec: str) -> tuple`
A spec has exactly 5 whitespace-separated fields (any run of whitespace separates them; leading/trailing whitespace is ignored): minute, hour, day-of-month, month, day-of-week. `parse_cron` returns a 5-tuple of sets holding the allowed values of each field, in that order.

Allowed value ranges: minute `0-59`, hour `0-23`, day-of-month `1-31`, month `1-12`, day-of-week `0-7` where `0` and `7` both mean Sunday. In the returned day-of-week set, `7` is normalised to `0` (so `"5-7"` gives `{5, 6, 0}`).

Each field is a comma-separated list of one or more terms; the field's set is the union of its terms. A term is one of:
- `*` — every value in the field's range.
- `n` — the single value `n`.
- `a-b` — every value from `a` to `b` inclusive; `a > b` is a `CronError`.
- `*/s` or `a-b/s` — as above but keeping every `s`-th value counting from the low end (`10-50/20` gives `{10, 30, 50}`, `*/15` on minutes gives `{0, 15, 30, 45}`). `s` must be an integer `>= 1`.

Anything else is a `CronError`: the wrong number of fields, a value outside the field's range, a reversed range, an empty term (`1,,2`, `1,2,`), a step on a bare number (`1/2`), a step that is missing/zero/non-numeric, month or day names, or any other junk (`1-`, `-1`, `1-2-3`, `a`).

## `matches(spec: str, dt: datetime) -> bool`
True if `dt` matches `spec`. Only `dt`'s minute, hour, day, month and weekday are used; seconds and microseconds are ignored. Minute, hour and month must all match. The day-of-month / day-of-week pair follows the traditional cron rule:
- if BOTH fields are literally `*`, any day matches;
- if exactly one of them is literally `*`, the day must match the other one;
- if NEITHER is literally `*`, the day matches when it matches day-of-month **OR** day-of-week.

(A field counts as "literally `*`" only when its text is exactly `*`; `*/1` does not count.) Day-of-week numbering is `0`=Sunday ... `6`=Saturday.

## `next_time(spec: str, after: datetime) -> datetime`
The earliest matching time strictly after `after`, with `second` and `microsecond` set to 0 (`after`'s own seconds/microseconds are discarded before the comparison, so with `after = 09:29:59` the time `09:30:00` is still in the future). If no match occurs within 1466 days of `after`, raise `CronError`. Search whole days first and only scan the minutes of days that can match, so that a rare spec like `0 0 29 2 *` resolves quickly instead of stepping through millions of minutes.

## Examples
- `parse_cron("*/15 0 * * *")` -> `({0, 15, 30, 45}, {0}, set(range(1, 32)), set(range(1, 13)), {0, 1, 2, 3, 4, 5, 6})`
- `matches("0 0 13 * 5", datetime(2024, 9, 6))` -> `True` (a Friday, though not the 13th)
- `next_time("*/15 * * * *", datetime(2024, 1, 1, 10, 15))` -> `datetime(2024, 1, 1, 10, 30)`
- `next_time("0 12 31 * *", datetime(2024, 1, 31, 13, 0))` -> `datetime(2024, 3, 31, 12, 0)` (February has no 31st)
- `next_time("0 0 29 2 *", datetime(2024, 3, 1))` -> `datetime(2028, 2, 29, 0, 0)`
- `parse_cron("60 * * * *")` and `parse_cron("* * * *")` raise `CronError`.

Write a few quick checks of your own and run them with `python`, then reply "done".
