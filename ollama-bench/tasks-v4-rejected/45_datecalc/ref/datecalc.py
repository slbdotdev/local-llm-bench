"""Proleptic-Gregorian date arithmetic on "YYYY-MM-DD" strings, years 1600..2400.

No use of datetime / calendar / time.
"""

MIN_YEAR = 1600
MAX_YEAR = 2400

_MDAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


# --------------------------------------------------------------------------
# basics
# --------------------------------------------------------------------------

def is_leap_year(year):
    y = int(year)
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


def days_in_month(year, month):
    y, m = int(year), int(month)
    if m < 1 or m > 12:
        raise ValueError("bad month %r" % (month,))
    if m == 2 and is_leap_year(y):
        return 29
    return _MDAYS[m - 1]


def _parse(s):
    if not isinstance(s, str):
        raise ValueError("date must be a str, got %r" % (type(s).__name__,))
    if len(s) != 10 or s[4] != "-" or s[7] != "-":
        raise ValueError("bad date format %r" % (s,))
    ys, ms, ds = s[0:4], s[5:7], s[8:10]
    for part in (ys, ms, ds):
        for ch in part:
            if ch < "0" or ch > "9":
                raise ValueError("bad date format %r" % (s,))
    y, m, d = int(ys), int(ms), int(ds)
    if y < MIN_YEAR or y > MAX_YEAR:
        raise ValueError("year out of range: %r" % (s,))
    if m < 1 or m > 12:
        raise ValueError("bad month: %r" % (s,))
    if d < 1 or d > days_in_month(y, m):
        raise ValueError("bad day: %r" % (s,))
    return y, m, d


def _fmt(y, m, d):
    if y < MIN_YEAR or y > MAX_YEAR:
        raise ValueError("result year out of range: %d" % (y,))
    return "%04d-%02d-%02d" % (y, m, d)


def _to_ord(y, m, d):
    """Days since 1970-01-01 (proleptic Gregorian)."""
    yy = y - (1 if m <= 2 else 0)
    era = (yy if yy >= 0 else yy - 399) // 400
    yoe = yy - era * 400
    mp = m - 3 if m > 2 else m + 9
    doy = (153 * mp + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def _from_ord(z):
    z += 719468
    era = (z if z >= 0 else z - 146096) // 146097
    doe = z - era * 146097
    yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
    yy = yoe + era * 400
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    d = doy - (153 * mp + 2) // 5 + 1
    m = mp + 3 if mp < 10 else mp - 9
    return yy + (1 if m <= 2 else 0), m, d


def _ord(s):
    return _to_ord(*_parse(s))


def _str(o):
    return _fmt(*_from_ord(o))


def day_of_week(date):
    """1 = Monday .. 7 = Sunday."""
    return ((_ord(date) + 3) % 7) + 1


def add_days(date, n):
    return _str(_ord(date) + int(n))


# --------------------------------------------------------------------------
# month / year arithmetic with end-of-month clamping
# --------------------------------------------------------------------------

def add_months(date, n):
    y, m, d = _parse(date)
    n = int(n)
    t = (y * 12 + (m - 1)) + n
    ny, nm = t // 12, (t % 12) + 1
    nd = min(d, days_in_month(ny, nm))
    return _fmt(ny, nm, nd)


def add_years(date, n):
    return add_months(date, 12 * int(n))


# --------------------------------------------------------------------------
# calendar difference
# --------------------------------------------------------------------------

def diff_ymd(start, end):
    ay, am, ad = _parse(start)
    by, bm, bd = _parse(end)
    if (ay, am, ad) > (by, bm, bd):
        y, m, d = diff_ymd(end, start)
        return (-y, -m, -d)
    y = by - ay
    m = bm - am
    d = bd - ad
    k = 0
    while d < 0:
        k += 1
        t = (by * 12 + (bm - 1)) - k
        d += days_in_month(t // 12, (t % 12) + 1)
        m -= 1
    while m < 0:
        m += 12
        y -= 1
    return (y, m, d)


# --------------------------------------------------------------------------
# ISO week dates
# --------------------------------------------------------------------------

def _dow_ord(o):
    return ((o + 3) % 7) + 1


def iso_week_date(date):
    o = _ord(date)
    thu = o + (4 - _dow_ord(o))
    iy = _from_ord(thu)[0]
    week = (thu - _to_ord(iy, 1, 1)) // 7 + 1
    return (iy, week, _dow_ord(o))


def iso_weeks_in_year(iso_year):
    y = int(iso_year)
    a = _dow_ord(_to_ord(y, 1, 1))
    if a == 4 or (a == 3 and is_leap_year(y)):
        return 53
    return 52


def from_iso_week_date(iso_year, week, weekday):
    y, w, wd = int(iso_year), int(week), int(weekday)
    if wd < 1 or wd > 7:
        raise ValueError("weekday out of range: %r" % (weekday,))
    if w < 1 or w > iso_weeks_in_year(y):
        raise ValueError("week out of range: %r" % (week,))
    jan4 = _to_ord(y, 1, 4)
    week1_monday = jan4 - (_dow_ord(jan4) - 1)
    return _str(week1_monday + (w - 1) * 7 + (wd - 1))


# --------------------------------------------------------------------------
# week of month
# --------------------------------------------------------------------------

def week_of_month(date):
    y, m, d = _parse(date)
    first = _dow_ord(_to_ord(y, m, 1))
    return (d - 1 + (first - 1)) // 7 + 1


# --------------------------------------------------------------------------
# business days
# --------------------------------------------------------------------------

def _holiset(holidays):
    s = set()
    for h in (holidays or ()):
        _parse(h)
        s.add(h)
    return s


def _is_biz_ord(o, hset):
    if _dow_ord(o) > 5:
        return False
    return _str(o) not in hset


def is_business_day(date, holidays=()):
    o = _ord(date)
    return _is_biz_ord(o, _holiset(holidays))


def add_business_days(date, n, holidays=()):
    o = _ord(date)
    n = int(n)
    hset = _holiset(holidays)
    if n == 0:
        return _str(o)
    step = 1 if n > 0 else -1
    left = abs(n)
    while left:
        o += step
        if _is_biz_ord(o, hset):
            left -= 1
    return _str(o)


def count_business_days(start, end, holidays=()):
    a = _ord(start)
    b = _ord(end)
    if a > b:
        return -count_business_days(end, start, holidays)
    hset = _holiset(holidays)
    n = 0
    for o in range(a, b):
        if _is_biz_ord(o, hset):
            n += 1
    return n


# --------------------------------------------------------------------------
# recurrences
# --------------------------------------------------------------------------

def nth_weekday_of_month(year, month, weekday, n):
    y, m, wd, k = int(year), int(month), int(weekday), int(n)
    if y < MIN_YEAR or y > MAX_YEAR:
        raise ValueError("year out of range: %r" % (year,))
    if m < 1 or m > 12:
        raise ValueError("month out of range: %r" % (month,))
    if wd < 1 or wd > 7:
        raise ValueError("weekday out of range: %r" % (weekday,))
    if k not in (1, 2, 3, 4, 5, -1):
        raise ValueError("n out of range: %r" % (n,))
    first = _to_ord(y, m, 1)
    offset = (wd - _dow_ord(first)) % 7
    if k == -1:
        last = _to_ord(y, m, days_in_month(y, m))
        return _str(last - ((_dow_ord(last) - wd) % 7))
    o = first + offset + 7 * (k - 1)
    if o > _to_ord(y, m, days_in_month(y, m)):
        return None
    return _str(o)


def last_business_day_of_month(year, month, holidays=()):
    y, m = int(year), int(month)
    if y < MIN_YEAR or y > MAX_YEAR:
        raise ValueError("year out of range: %r" % (year,))
    if m < 1 or m > 12:
        raise ValueError("month out of range: %r" % (month,))
    hset = _holiset(holidays)
    first = _to_ord(y, m, 1)
    o = _to_ord(y, m, days_in_month(y, m))
    while o >= first:
        if _is_biz_ord(o, hset):
            return _str(o)
        o -= 1
    return None
