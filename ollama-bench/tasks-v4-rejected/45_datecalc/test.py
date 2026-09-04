import sys, os, re, random, threading, inspect
import datetime as _dt
import calendar as _cal

TOTAL = 26
fails = []
done = 0
_lock = threading.Lock()


def check(name, fn):
    global done
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = "%s raised %s" % (name, type(e).__name__)
    if not ok:
        fails.append(name)
    with _lock:
        done += 1


def report():
    n = max(0, min(TOTAL, TOTAL - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    if fails:
        print("FAIL", fails[:10])
        sys.exit(1)
    print("PASS")
    sys.exit(0)


def _watchdog():
    n = max(0, min(TOTAL, done - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    sys.stdout.flush()
    os._exit(1)


_t = threading.Timer(45.0, _watchdog)
_t.daemon = True
_t.start()

try:
    import datecalc
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()


def _miss(name):
    def _f(*a, **k):
        raise AttributeError("datecalc.%s is missing" % name)
    return _f


def G(name):
    return getattr(datecalc, name, _miss(name))


is_leap_year = G("is_leap_year")
days_in_month = G("days_in_month")
day_of_week = G("day_of_week")
add_days = G("add_days")
add_months = G("add_months")
add_years = G("add_years")
diff_ymd = G("diff_ymd")
iso_week_date = G("iso_week_date")
iso_weeks_in_year = G("iso_weeks_in_year")
from_iso_week_date = G("from_iso_week_date")
week_of_month = G("week_of_month")
is_business_day = G("is_business_day")
add_business_days = G("add_business_days")
count_business_days = G("count_business_days")
nth_weekday_of_month = G("nth_weekday_of_month")
last_business_day_of_month = G("last_business_day_of_month")


# =========================================================================
# oracle (stdlib datetime / calendar) -- all names prefixed _ora_
# =========================================================================

def _ora_parts(s):
    return int(s[0:4]), int(s[5:7]), int(s[8:10])


def _ora_fmt(y, m, d):
    return "%04d-%02d-%02d" % (y, m, d)


def _ora_date(s):
    y, m, d = _ora_parts(s)
    return _dt.date(y, m, d)


def _ora_str(d):
    return _ora_fmt(d.year, d.month, d.day)


def _ora_dim(y, m):
    return _cal.monthrange(y, m)[1]


def _ora_leap(y):
    return _cal.isleap(y)


def _ora_dow(s):
    return _ora_date(s).isoweekday()


def _ora_add_days(s, n):
    return _ora_str(_ora_date(s) + _dt.timedelta(days=n))


def _ora_add_months(s, n):
    y, m, d = _ora_parts(s)
    t = y * 12 + (m - 1) + n
    ny, nm = t // 12, (t % 12) + 1
    return _ora_fmt(ny, nm, min(d, _ora_dim(ny, nm)))


def _ora_diff(a, b):
    if a > b:
        y, m, d = _ora_diff(b, a)
        return (-y, -m, -d)
    ay, am, ad = _ora_parts(a)
    by, bm, bd = _ora_parts(b)
    y, m, d = by - ay, bm - am, bd - ad
    k = 0
    while d < 0:
        k += 1
        t = by * 12 + (bm - 1) - k
        d += _ora_dim(t // 12, (t % 12) + 1)
        m -= 1
    while m < 0:
        m += 12
        y -= 1
    return (y, m, d)


def _ora_iso(s):
    return tuple(_ora_date(s).isocalendar())


def _ora_weeks_in_year(y):
    return _dt.date(y, 12, 28).isocalendar()[1]


def _ora_from_iso(y, w, wd):
    return _ora_str(_dt.date.fromisocalendar(y, w, wd))


def _ora_wom(s):
    y, m, d = _ora_parts(s)
    return (d - 1 + (_dt.date(y, m, 1).isoweekday() - 1)) // 7 + 1


def _ora_isbiz(d, hs):
    return d.isoweekday() <= 5 and _ora_str(d) not in hs


def _ora_count_biz(a, b, hs):
    if a > b:
        return -_ora_count_biz(b, a, hs)
    cur, end = _ora_date(a), _ora_date(b)
    one = _dt.timedelta(days=1)
    n = 0
    while cur < end:
        if _ora_isbiz(cur, hs):
            n += 1
        cur += one
    return n


def _ora_add_biz(s, n, hs):
    d = _ora_date(s)
    if n == 0:
        return _ora_str(d)
    step = _dt.timedelta(days=1 if n > 0 else -1)
    left = abs(n)
    while left:
        d += step
        if _ora_isbiz(d, hs):
            left -= 1
    return _ora_str(d)


def _ora_nth(y, m, wd, n):
    days = [dd for dd in range(1, _ora_dim(y, m) + 1)
            if _dt.date(y, m, dd).isoweekday() == wd]
    if n == -1:
        return _ora_fmt(y, m, days[-1])
    if n <= len(days):
        return _ora_fmt(y, m, days[n - 1])
    return None


def _ora_lbd(y, m, hs):
    for dd in range(_ora_dim(y, m), 0, -1):
        d = _dt.date(y, m, dd)
        if _ora_isbiz(d, hs):
            return _ora_str(d)
    return None


# =========================================================================
# case generators
# =========================================================================

GY_LO, GY_HI = 1650, 2350
CORNER_YEARS = [1700, 1800, 1899, 1900, 1904, 1999, 2000, 2020, 2023, 2024,
                2025, 2026, 2100, 2200, 2300]
CORNER = []
for _y in CORNER_YEARS:
    CORNER.append(_ora_fmt(_y, 2, 28))
    CORNER.append(_ora_fmt(_y, 2, _ora_dim(_y, 2)))
    for _d in (1, 2, 3, 4, 5, 6, 7):
        CORNER.append(_ora_fmt(_y, 1, _d))
    for _d in (25, 26, 27, 28, 29, 30, 31):
        CORNER.append(_ora_fmt(_y, 12, _d))
    for _m in range(1, 13):
        CORNER.append(_ora_fmt(_y, _m, _ora_dim(_y, _m)))
        CORNER.append(_ora_fmt(_y, _m, 1))
CORNER = sorted(set(CORNER))

MONTH_END = sorted(set(s for s in CORNER
                       if _ora_parts(s)[2] == _ora_dim(*_ora_parts(s)[:2])))


def rd(rng):
    """A random date in 1650..2350, biased towards corner cases."""
    r = rng.random()
    if r < 0.40:
        return rng.choice(CORNER)
    y = rng.randint(GY_LO, GY_HI)
    m = rng.randint(1, 12)
    if rng.random() < 0.35:
        d = _ora_dim(y, m)
    elif rng.random() < 0.2:
        d = 1
    else:
        d = rng.randint(1, _ora_dim(y, m))
    return _ora_fmt(y, m, d)


def rd_me(rng):
    """A random month-end (or near month-end) date."""
    if rng.random() < 0.6:
        return rng.choice(MONTH_END)
    y = rng.randint(GY_LO, GY_HI)
    m = rng.randint(1, 12)
    dim = _ora_dim(y, m)
    return _ora_fmt(y, m, max(1, dim - rng.randint(0, 2)))


def rholidays(rng, around):
    """A holiday set near `around` (a date str), including weekend holidays."""
    base = _ora_date(around)
    hs = set()
    for _ in range(rng.randint(0, 14)):
        hs.add(_ora_str(base + _dt.timedelta(days=rng.randint(-40, 40))))
    for _ in range(rng.randint(0, 3)):
        hs.add(_ora_str(base + _dt.timedelta(days=rng.randint(-4000, 4000))))
    hs = [h for h in hs if GY_LO <= int(h[:4]) <= GY_HI]
    if rng.random() < 0.5:
        hs = hs + hs[:2]          # duplicates are harmless
    return hs


def pairs(fn):
    """Wrap a per-case body: returns a probe that runs it and compares."""
    def probe():
        return fn()
    return probe


# =========================================================================
# 1: forbidden imports
# =========================================================================

def no_forbidden_imports():
    try:
        src = inspect.getsource(datecalc)
    except Exception:
        return False
    bad = re.compile(
        r"(?m)^\s*(?:import\s+[\w\s,.]*\b(?:datetime|calendar|time)\b"
        r"|from\s+(?:datetime|calendar|time)\b)")
    if bad.search(src):
        return False
    if re.search(r"__import__\s*\(\s*['\"](?:datetime|calendar|time)['\"]", src):
        return False
    return True


check("does not import datetime / calendar / time", no_forbidden_imports)


# =========================================================================
# 2: basics
# =========================================================================

def basics():
    rng = random.Random(1001)
    for y in range(1600, 2401):
        if bool(is_leap_year(y)) != _ora_leap(y):
            return False
    for _ in range(400):
        y = rng.randint(1600, 2400)
        m = rng.randint(1, 12)
        if days_in_month(y, m) != _ora_dim(y, m):
            return False
    for _ in range(400):
        s = rd(rng)
        if day_of_week(s) != _ora_dow(s):
            return False
    return True


check("is_leap_year / days_in_month / day_of_week", basics)


# =========================================================================
# 3: add_days
# =========================================================================

def t_add_days():
    rng = random.Random(1002)
    for i in range(400):
        s = rd(rng)
        n = 0 if i % 17 == 0 else rng.randint(-2000, 2000)
        if add_days(s, n) != _ora_add_days(s, n):
            return False
    return True


check("add_days (positive, negative and zero shifts)", t_add_days)


# =========================================================================
# 4-7: month / year arithmetic
# =========================================================================

def t_add_months_rand():
    rng = random.Random(1003)
    for i in range(400):
        s = rd(rng)
        n = 0 if i % 23 == 0 else rng.randint(-240, 240)
        if add_months(s, n) != _ora_add_months(s, n):
            return False
    return True


def t_add_months_clamp():
    rng = random.Random(1004)
    for _ in range(400):
        s = rd_me(rng)
        n = rng.choice([1, 2, 3, 4, 5, 6, 7, 11, 12, 13, 25])
        if add_months(s, n) != _ora_add_months(s, n):
            return False
    # every 31st into every following month, several years
    for y in (1900, 1999, 2000, 2023, 2024):
        for m in (1, 3, 5, 7, 8, 10, 12):
            s = _ora_fmt(y, m, 31)
            for n in range(0, 25):
                if add_months(s, n) != _ora_add_months(s, n):
                    return False
    return True


def t_add_months_neg():
    rng = random.Random(1005)
    for _ in range(400):
        s = rd_me(rng)
        n = -rng.choice([1, 2, 3, 4, 5, 6, 9, 12, 13, 24, 25, 47])
        if add_months(s, n) != _ora_add_months(s, n):
            return False
    for y in (1904, 2000, 2023, 2024, 2100):
        for m in range(1, 13):
            s = _ora_fmt(y, m, _ora_dim(y, m))
            for n in range(-24, 1):
                if add_months(s, n) != _ora_add_months(s, n):
                    return False
    return True


def t_add_years():
    rng = random.Random(1006)
    for _ in range(400):
        s = rd(rng)
        n = rng.randint(-50, 50)
        if add_years(s, n) != _ora_add_months(s, 12 * n):
            return False
    for y in (1600, 1696, 1704, 1896, 1904, 1996, 2000, 2004, 2024, 2096,
              2296, 2396):
        if not _ora_leap(y):
            continue
        s = _ora_fmt(y, 2, 29)
        for n in range(-8, 9):
            if 1600 <= y + n <= 2400:
                if add_years(s, n) != _ora_add_months(s, 12 * n):
                    return False
    return True


check("add_months, random deltas", t_add_months_rand)
check("add_months, month ends clamped into shorter months", t_add_months_clamp)
check("add_months, negative deltas", t_add_months_neg)
check("add_years, including Feb 29", t_add_years)


# =========================================================================
# 8-11: ISO week dates
# =========================================================================

def t_iso_rand():
    rng = random.Random(1007)
    for _ in range(500):
        s = rd(rng)
        if tuple(iso_week_date(s)) != _ora_iso(s):
            return False
    return True


def t_iso_boundary():
    for y in range(1650, 2351, 7):
        for s in (_ora_fmt(y, 12, 28), _ora_fmt(y, 12, 29), _ora_fmt(y, 12, 30),
                  _ora_fmt(y, 12, 31), _ora_fmt(y, 1, 1), _ora_fmt(y, 1, 2),
                  _ora_fmt(y, 1, 3), _ora_fmt(y, 1, 4)):
            if tuple(iso_week_date(s)) != _ora_iso(s):
                return False
    for s in ("2021-01-01", "2021-01-03", "2021-01-04", "2019-12-30",
              "2019-12-31", "2016-01-01", "2000-01-01", "2000-01-02",
              "2024-12-30", "2024-12-31", "2025-01-01", "2015-12-31",
              "2010-01-03", "2010-01-04", "2005-01-01", "2005-01-02"):
            if tuple(iso_week_date(s)) != _ora_iso(s):
                return False
    return True


def t_iso_weeks_in_year():
    for y in range(1600, 2401):
        if iso_weeks_in_year(y) != _ora_weeks_in_year(y):
            return False
    return True


def t_from_iso():
    rng = random.Random(1008)
    for _ in range(400):
        s = rd(rng)
        iy, iw, iwd = _ora_iso(s)
        if from_iso_week_date(iy, iw, iwd) != s:
            return False
    for y in range(1700, 2301, 11):
        n = _ora_weeks_in_year(y)
        for w in (1, 2, n - 1, n):
            for wd in (1, 4, 7):
                if from_iso_week_date(y, w, wd) != _ora_from_iso(y, w, wd):
                    return False
    for y in (1700, 1900, 2019, 2020, 2021, 2024, 2025, 2100):
        n = _ora_weeks_in_year(y)
        for bad in (0, -1, n + 1, 54):
            try:
                from_iso_week_date(y, bad, 1)
                return False
            except ValueError:
                pass
        for bad in (0, 8, -1):
            try:
                from_iso_week_date(y, 1, bad)
                return False
            except ValueError:
                pass
    return True


check("iso_week_date, random dates", t_iso_rand)
check("iso_week_date across the Dec/Jan year boundary", t_iso_boundary)
check("iso_weeks_in_year over 1600..2400", t_iso_weeks_in_year)
check("from_iso_week_date (inverse and out-of-range weeks)", t_from_iso)


# =========================================================================
# 12: week_of_month
# =========================================================================

def t_wom():
    rng = random.Random(1009)
    for _ in range(400):
        s = rd(rng)
        if week_of_month(s) != _ora_wom(s):
            return False
    for y in (1999, 2000, 2023, 2024, 2025):
        for m in range(1, 13):
            for d in range(1, _ora_dim(y, m) + 1):
                s = _ora_fmt(y, m, d)
                if week_of_month(s) != _ora_wom(s):
                    return False
    return True


check("week_of_month (Mon..Sun weeks, short first week)", t_wom)


# =========================================================================
# 13-15: diff_ymd
# =========================================================================

def t_diff_fwd():
    rng = random.Random(1010)
    for _ in range(400):
        a, b = rd(rng), rd(rng)
        if a > b:
            a, b = b, a
        if tuple(diff_ymd(a, b)) != _ora_diff(a, b):
            return False
    return True


def t_diff_borrow():
    rng = random.Random(1011)
    for _ in range(400):
        a = rd_me(rng)
        b = _ora_add_days(_ora_add_months(a, rng.randint(0, 40)),
                          rng.randint(-3, 3))
        if not (GY_LO <= int(b[:4]) <= GY_HI):
            continue
        if a > b:
            a, b = b, a
        if tuple(diff_ymd(a, b)) != _ora_diff(a, b):
            return False
    for a, b in (("2024-01-31", "2024-03-01"), ("2024-01-31", "2024-02-29"),
                 ("2023-01-31", "2023-03-01"), ("2024-08-31", "2024-09-30"),
                 ("2024-02-29", "2025-02-28"), ("2000-01-30", "2000-03-01"),
                 ("2024-03-31", "2024-04-30"), ("1999-12-31", "2000-03-01"),
                 ("2024-05-31", "2024-06-30"), ("2024-01-30", "2024-02-29")):
        if tuple(diff_ymd(a, b)) != _ora_diff(a, b):
            return False
    return True


def t_diff_rev():
    rng = random.Random(1012)
    for _ in range(400):
        a, b = rd(rng), rd(rng)
        if tuple(diff_ymd(a, b)) != _ora_diff(a, b):
            return False
        if tuple(diff_ymd(b, a)) != _ora_diff(b, a):
            return False
    for _ in range(200):
        a = rd_me(rng)
        b = _ora_add_days(a, rng.randint(-500, 500))
        if not (GY_LO <= int(b[:4]) <= GY_HI):
            continue
        if tuple(diff_ymd(b, a)) != _ora_diff(b, a):
            return False
    return True


check("diff_ymd, forward pairs", t_diff_fwd)
check("diff_ymd, month-end pairs (borrow rule)", t_diff_borrow)
check("diff_ymd, reversed pairs are componentwise negated", t_diff_rev)


# =========================================================================
# 16-18: count_business_days
# =========================================================================

def t_count_plain():
    rng = random.Random(1013)
    for _ in range(250):
        a = rd(rng)
        b = _ora_add_days(a, rng.randint(0, 400))
        if not (GY_LO <= int(b[:4]) <= GY_HI):
            continue
        if count_business_days(a, b) != _ora_count_biz(a, b, set()):
            return False
    return True


def t_count_holidays():
    rng = random.Random(1014)
    for _ in range(250):
        a = rd(rng)
        b = _ora_add_days(a, rng.randint(0, 120))
        if not (GY_LO <= int(b[:4]) <= GY_HI):
            continue
        hs = rholidays(rng, a)
        if count_business_days(a, b, hs) != _ora_count_biz(a, b, set(hs)):
            return False
        if bool(is_business_day(a, hs)) != _ora_isbiz(_ora_date(a), set(hs)):
            return False
    return True


def t_count_edges():
    rng = random.Random(1015)
    for _ in range(300):
        a = rd(rng)
        if count_business_days(a, a) != 0:
            return False
        if count_business_days(a, a, [a]) != 0:
            return False
        for k in (1, -1, 2, -2, 7, -7):
            b = _ora_add_days(a, k)
            if not (GY_LO <= int(b[:4]) <= GY_HI):
                continue
            if count_business_days(a, b) != _ora_count_biz(a, b, set()):
                return False
        b = _ora_add_days(a, rng.randint(1, 200))
        if not (GY_LO <= int(b[:4]) <= GY_HI):
            continue
        hs = rholidays(rng, a)
        if count_business_days(b, a, hs) != _ora_count_biz(b, a, set(hs)):
            return False
        if count_business_days(b, a, hs) != -count_business_days(a, b, hs):
            return False
    return True


check("count_business_days, half-open [start, end), no holidays", t_count_plain)
check("count_business_days with holidays (some on weekends)", t_count_holidays)
check("count_business_days: equal, adjacent and reversed endpoints",
      t_count_edges)


# =========================================================================
# 19-22: add_business_days
# =========================================================================

def t_addbiz_zero():
    rng = random.Random(1016)
    for _ in range(300):
        s = rd(rng)
        if add_business_days(s, 0) != s:
            return False
        hs = rholidays(rng, s)
        if add_business_days(s, 0, hs) != s:
            return False
        if add_business_days(s, 0, [s]) != s:
            return False
    # every day of a few months, including all weekends
    for y, m in ((2024, 3), (2023, 7), (1999, 1)):
        for d in range(1, _ora_dim(y, m) + 1):
            s = _ora_fmt(y, m, d)
            if add_business_days(s, 0, [s]) != s:
                return False
    return True


def t_addbiz_pos():
    rng = random.Random(1017)
    for _ in range(300):
        s = rd(rng)
        n = rng.randint(1, 120)
        hs = rholidays(rng, s) if rng.random() < 0.6 else []
        want = _ora_add_biz(s, n, set(hs))
        if not (GY_LO <= int(want[:4]) <= GY_HI):
            continue
        if add_business_days(s, n, hs) != want:
            return False
    return True


def t_addbiz_neg():
    rng = random.Random(1018)
    for _ in range(300):
        s = rd(rng)
        n = -rng.randint(1, 120)
        hs = rholidays(rng, s) if rng.random() < 0.6 else []
        want = _ora_add_biz(s, n, set(hs))
        if not (GY_LO <= int(want[:4]) <= GY_HI):
            continue
        if add_business_days(s, n, hs) != want:
            return False
    return True


def t_addbiz_offday():
    """Starting on a weekend or on a holiday, tiny steps."""
    rng = random.Random(1019)
    tries = 0
    while tries < 300:
        s = rd(rng)
        hs = rholidays(rng, s) if rng.random() < 0.5 else []
        hset = set(hs)
        if _ora_isbiz(_ora_date(s), hset) and rng.random() < 0.85:
            continue
        tries += 1
        for n in (1, -1, 2, -2, 5, -5):
            want = _ora_add_biz(s, n, hset)
            if not (GY_LO <= int(want[:4]) <= GY_HI):
                continue
            if add_business_days(s, n, hs) != want:
                return False
    # every Saturday/Sunday of a year, +-1
    for d in range(1, 366):
        s = _ora_str(_dt.date(2023, 1, 1) + _dt.timedelta(days=d - 1))
        if _ora_dow(s) <= 5:
            continue
        for n in (1, -1):
            if add_business_days(s, n) != _ora_add_biz(s, n, set()):
                return False
    return True


check("add_business_days with n == 0 returns the date unchanged", t_addbiz_zero)
check("add_business_days, n > 0", t_addbiz_pos)
check("add_business_days, n < 0", t_addbiz_neg)
check("add_business_days starting on a weekend or holiday", t_addbiz_offday)


# =========================================================================
# 23-25: recurrences
# =========================================================================

def t_nth_1_4():
    rng = random.Random(1020)
    for _ in range(400):
        y = rng.randint(GY_LO, GY_HI)
        m = rng.randint(1, 12)
        wd = rng.randint(1, 7)
        n = rng.randint(1, 4)
        if nth_weekday_of_month(y, m, wd, n) != _ora_nth(y, m, wd, n):
            return False
    for y in (2024, 2023, 1900):
        for m in range(1, 13):
            for wd in range(1, 8):
                for n in (1, 2, 3, 4):
                    if nth_weekday_of_month(y, m, wd, n) != _ora_nth(y, m, wd, n):
                        return False
    return True


def t_nth_5_last():
    for y in (1899, 1900, 1996, 2000, 2023, 2024, 2025, 2100):
        for m in range(1, 13):
            for wd in range(1, 8):
                if nth_weekday_of_month(y, m, wd, 5) != _ora_nth(y, m, wd, 5):
                    return False
                if nth_weekday_of_month(y, m, wd, -1) != _ora_nth(y, m, wd, -1):
                    return False
    rng = random.Random(1021)
    for _ in range(300):
        y = rng.randint(GY_LO, GY_HI)
        m = rng.randint(1, 12)
        wd = rng.randint(1, 7)
        n = rng.choice([5, -1])
        if nth_weekday_of_month(y, m, wd, n) != _ora_nth(y, m, wd, n):
            return False
    for bad in (0, 6, -2, 7, -5):
        try:
            nth_weekday_of_month(2024, 3, 1, bad)
            return False
        except ValueError:
            pass
    for bad in (0, 8, -1):
        try:
            nth_weekday_of_month(2024, 3, bad, 1)
            return False
        except ValueError:
            pass
    for bad in (0, 13, -1):
        try:
            nth_weekday_of_month(2024, bad, 1, 1)
            return False
        except ValueError:
            pass
    return True


def t_lbd():
    rng = random.Random(1022)
    for _ in range(300):
        y = rng.randint(GY_LO, GY_HI)
        m = rng.randint(1, 12)
        hs = rholidays(rng, _ora_fmt(y, m, 15)) if rng.random() < 0.7 else []
        if last_business_day_of_month(y, m, hs) != _ora_lbd(y, m, set(hs)):
            return False
    for y in (1999, 2000, 2023, 2024):
        for m in range(1, 13):
            if last_business_day_of_month(y, m) != _ora_lbd(y, m, set()):
                return False
    # a month with every business day marked as a holiday -> None
    hs = [_ora_fmt(2024, 3, d) for d in range(1, 32)]
    if last_business_day_of_month(2024, 3, hs) is not None:
        return False
    return True


check("nth_weekday_of_month, n = 1..4", t_nth_1_4)
check("nth_weekday_of_month, n = 5 (may be None) and n = -1", t_nth_5_last)
check("last_business_day_of_month", t_lbd)


# =========================================================================
# 26: validation
# =========================================================================

BAD_DATES = ["2023-02-29", "1900-02-29", "2100-02-29", "2024-13-01",
             "2024-00-10", "2024-04-31", "2024-06-31", "2024-01-32",
             "2024-01-00", "1599-12-31", "2401-01-01", "2024-1-01",
             "2024-01-1", "20240101", "2024/01/01", "24-01-01",
             "abcd-01-01", "2024-ab-01", "2024-01-0x", "", "2024-01-011"]


def t_validation():
    fns = [lambda s: day_of_week(s),
           lambda s: add_days(s, 1),
           lambda s: add_months(s, 1),
           lambda s: add_years(s, 1),
           lambda s: diff_ymd(s, "2024-01-01"),
           lambda s: diff_ymd("2024-01-01", s),
           lambda s: iso_week_date(s),
           lambda s: week_of_month(s),
           lambda s: is_business_day(s),
           lambda s: add_business_days(s, 1),
           lambda s: count_business_days(s, "2024-01-01")]
    for s in BAD_DATES:
        for f in fns:
            try:
                f(s)
            except ValueError:
                continue
            except Exception:
                return False
            return False
    # results outside 1600..2400 must raise ValueError too
    for f in (lambda: add_days("2400-12-31", 1),
              lambda: add_days("1600-01-01", -1),
              lambda: add_months("2400-12-01", 1),
              lambda: add_months("1600-01-01", -1),
              lambda: add_years("2400-01-01", 1),
              lambda: add_years("1600-01-01", -1)):
        try:
            f()
        except ValueError:
            continue
        except Exception:
            return False
        return False
    # ...but the very edges themselves are fine
    if add_days("2400-12-30", 1) != "2400-12-31":
        return False
    if add_days("1600-01-02", -1) != "1600-01-01":
        return False
    return True


check("ValueError for malformed / impossible / out-of-range dates",
      t_validation)

_t.cancel()
report()
