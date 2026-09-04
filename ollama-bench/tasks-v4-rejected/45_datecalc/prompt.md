Create `datecalc.py`: proleptic-Gregorian calendar arithmetic, no time zones and no
times of day.

A **date** is always a string in the exact form `"YYYY-MM-DD"` (zero padded, e.g.
`"0999-01-02"` shape, always exactly 10 characters). The supported range is
**year 1600 through year 2400 inclusive**. Weekdays are integers with
**1 = Monday ... 7 = Sunday** (ISO numbering).

**You must not import `datetime`, `calendar` or `time`** (nor `from datetime import ...`
etc.). Implement the calendar yourself. Any other stdlib module is allowed.

```python
MIN_YEAR = 1600
MAX_YEAR = 2400

def is_leap_year(year: int) -> bool
def days_in_month(year: int, month: int) -> int

def day_of_week(date: str) -> int                     # 1=Mon .. 7=Sun
def add_days(date: str, n: int) -> str                # n may be negative or 0

def add_months(date: str, n: int) -> str
def add_years(date: str, n: int) -> str

def diff_ymd(start: str, end: str) -> tuple           # (years, months, days)

def iso_week_date(date: str) -> tuple                 # (iso_year, iso_week, iso_weekday)
def iso_weeks_in_year(iso_year: int) -> int           # 52 or 53
def from_iso_week_date(iso_year: int, week: int, weekday: int) -> str

def week_of_month(date: str) -> int

def is_business_day(date: str, holidays=()) -> bool
def add_business_days(date: str, n: int, holidays=()) -> str
def count_business_days(start: str, end: str, holidays=()) -> int

def nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> str | None
def last_business_day_of_month(year: int, month: int, holidays=()) -> str | None
```

## Validation

Every function that takes a date string must `raise ValueError` if the string is not
exactly 10 characters of the form `DDDD-DD-DD` with ASCII digits, or if it does not name
a real date, or if its year is outside `1600..2400`. So `"2023-02-29"`, `"2024-13-01"`,
`"2024-00-10"`, `"1599-12-31"`, `"2401-01-01"`, `"2024-1-01"` and `"20240101"` all raise
`ValueError`. Results are also confined to `1600..2400`: a computation whose result would
fall outside that range raises `ValueError` too. Nothing raises any other exception type
for bad input.

`holidays` is any iterable of valid date strings. It may be empty, may contain duplicates,
may contain dates that fall on a Saturday or Sunday, and may contain dates far away from
the dates being computed; all of that is harmless. Membership is by exact date string.

## Rules

**`add_days(date, n)`** shifts by `n` calendar days; `n` may be negative or `0`.

**`add_months(date, n)`** shifts the (year, month) pair by `n` months (`n` may be
negative or `0`) and then **clamps the day of month down** to the last day of the target
month if the original day does not exist there. The day is never carried into the next
month.

* `add_months("2024-01-31", 1) == "2024-02-29"`
* `add_months("2023-01-31", 1) == "2023-02-28"`
* `add_months("2024-03-31", -1) == "2024-02-29"`
* `add_months("2024-05-31", -3) == "2024-02-29"`

Clamping is **not** remembered: `add_months(add_months("2024-01-31", 1), 1)` is
`add_months("2024-02-29", 1) == "2024-03-29"`, not `"2024-03-31"`.

**`add_years(date, n)`** is exactly `add_months(date, 12 * n)`, so
`add_years("2024-02-29", 1) == "2025-02-28"` and
`add_years("2024-02-29", 4) == "2028-02-29"`.

**`diff_ymd(start, end)`** returns the calendar difference as a 3-tuple of ints computed
by exactly this algorithm. If `start > end` as dates, the result is the componentwise
negation of `diff_ymd(end, start)` (so `diff_ymd("2024-03-01", "2024-01-31")` is
`(0, 0, -30)`). Otherwise, writing `start` as `(ay, am, ad)` and `end` as `(by, bm, bd)`:

```
y = by - ay ;  m = bm - am ;  d = bd - ad
k = 0
while d < 0:                       # borrow whole months, walking BACKWARDS from `end`
    k += 1
    d += (length of the month that is k months before end's month)
    m -= 1
while m < 0:
    m += 12 ;  y -= 1
return (y, m, d)
```

Note the borrow takes the length of the month **preceding `end`** (and keeps borrowing
until `d >= 0`), not the length of `start`'s month. For example
`diff_ymd("2024-01-31", "2024-03-01")`: `d = -30`, borrow February 2024 (29) giving
`d = -1, m = 1`, borrow January 2024 (31) giving `d = 30, m = 0`, so the answer is
`(0, 0, 30)`. All three components of a non-negative result are `>= 0`.

**ISO week dates** follow ISO 8601: weeks run Monday..Sunday, and week 1 of an ISO year
is the week containing that year's first Thursday (equivalently, the week containing
January 4th). `iso_week_date(date)` returns `(iso_year, iso_week, iso_weekday)`, where
`iso_year` may differ from the calendar year near January 1st and December 31st.
`iso_weeks_in_year(iso_year)` returns 53 if that ISO year is a "long" year and 52
otherwise. `from_iso_week_date(iso_year, week, weekday)` is the inverse; it raises
`ValueError` if `weekday` is outside `1..7` or `week` is outside
`1..iso_weeks_in_year(iso_year)`.

**`week_of_month(date)`** cuts the month into Monday..Sunday calendar weeks. The first
such week starts on the 1st of the month and ends on the first Sunday of the month (so it
may be as short as one day), the second week starts on the following Monday, and so on.
`week_of_month` returns the 1-based index of the week containing `date`, i.e.

```
week_of_month = (day_of_month - 1 + (day_of_week(first of that month) - 1)) // 7 + 1
```

The result is between 1 and 6.

**Business days.** A date is a business day when its weekday is Monday..Friday (1..5)
*and* it is not in `holidays`. `is_business_day` reports that.

`count_business_days(start, end, holidays)` counts the business days in the **half-open**
interval `[start, end)` — `start` is counted if it is a business day, `end` is never
counted. It returns `0` when `start == end`. If `start > end` the result is
`-count_business_days(end, start, holidays)` (i.e. it is negative).

`add_business_days(date, n, holidays)`:

* If `n == 0` the input date is **returned unchanged**, even when it is a Saturday, a
  Sunday or a holiday. There is no rolling.
* If `n > 0`, walk forward one calendar day at a time, decrementing a counter each time
  you land on a business day, and stop as soon as the counter reaches `n`. The starting
  date itself is never counted, whether or not it is a business day, so the result is
  always a business day strictly after `date`.
* If `n < 0`, do the same walking backwards; the result is always a business day strictly
  before `date`.

So a Saturday plus 1 business day is the following Monday, and a Saturday minus 1
business day is the preceding Friday.

**`nth_weekday_of_month(year, month, weekday, n)`** returns the date of the `n`-th
`weekday` of that month. `n` must be one of `1, 2, 3, 4, 5, -1`; any other `n`, a
`weekday` outside `1..7`, a `month` outside `1..12` or a `year` outside `1600..2400`
raises `ValueError`. `n == -1` means the **last** such weekday of the month. If `n == 5`
and the month contains only four of that weekday, the function returns `None` (it does
not spill into the next month and does not fall back to the 4th).

**`last_business_day_of_month(year, month, holidays)`** returns the latest business day in
that month, scanning backwards from the last day of the month, or `None` if the month
contains no business day at all.

## Worked examples

```python
add_days("2024-02-28", 3) == "2024-03-02"
add_months("2024-03-15", 2) == "2024-05-15"
day_of_week("2024-01-01") == 1                        # a Monday
diff_ymd("2020-03-10", "2023-07-20") == (3, 4, 10)
count_business_days("2024-03-04", "2024-03-11") == 5   # Mon..Fri, the 11th excluded
nth_weekday_of_month(2024, 3, 5, 2) == "2024-03-08"    # 2nd Friday of March 2024
```

Write a few quick checks of your own and run them with `python`, then reply "done".
