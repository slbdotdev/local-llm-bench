import sys, json, subprocess
from datetime import datetime

TOTAL = 31
fails = []


def check(name, fn):
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = "%s raised %s" % (name, type(e).__name__)
    if not ok:
        fails.append(name)


def report():
    n = max(0, min(TOTAL, TOTAL - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    if fails:
        print("FAIL", fails[:10])
        sys.exit(1)
    print("PASS")
    sys.exit(0)


D = datetime

# (group, key, spec, after_iso, expected_iso)  -- expected None means CronError
NT = [
    ("basic minutes and hours", "b1", "*/15 * * * *", "2024-01-01T10:07:00", "2024-01-01T10:15:00"),
    ("basic minutes and hours", "b2", "*/15 * * * *", "2024-01-01T10:15:00", "2024-01-01T10:30:00"),
    ("basic minutes and hours", "b3", "0 * * * *", "2024-01-01T10:00:30", "2024-01-01T11:00:00"),
    ("basic lists and seconds", "b4", "30 9 * * *", "2024-01-01T09:29:59", "2024-01-01T09:30:00"),
    ("basic lists and seconds", "b5", "0 0 * * *", "2024-01-01T00:00:00", "2024-01-02T00:00:00"),
    ("basic lists and seconds", "b6", "5,35 8-9 * * *", "2024-01-01T08:35:00", "2024-01-01T09:05:00"),
    ("month and year rollovers", "r1", "0 0 1 * *", "2024-01-15T12:00:00", "2024-02-01T00:00:00"),
    ("month and year rollovers", "r2", "0 0 1 1 *", "2024-06-01T00:00:00", "2025-01-01T00:00:00"),
    ("month and year rollovers", "r3", "59 23 31 12 *", "2024-12-31T23:58:00", "2024-12-31T23:59:00"),
    ("short month handling", "r4", "0 12 31 * *", "2024-01-31T13:00:00", "2024-03-31T12:00:00"),
    ("short month handling", "r5", "59 23 * * *", "2024-02-28T23:59:00", "2024-02-29T23:59:00"),
    ("dom/dow OR rule", "d1", "0 0 13 * 5", "2024-09-01T00:00:00", "2024-09-06T00:00:00"),
    ("dom/dow OR rule", "d2", "0 0 13 * 5", "2024-09-07T00:00:00", "2024-09-13T00:00:00"),
    ("dom/dow OR rule", "d3", "0 0 1 * 1", "2024-05-02T00:00:00", "2024-05-06T00:00:00"),
    ("single day field", "d4", "0 0 13 * *", "2024-09-01T00:00:00", "2024-09-13T00:00:00"),
    ("single day field", "d5", "0 0 * * 0", "2024-09-02T00:00:00", "2024-09-08T00:00:00"),
    ("far future and no match", "f1", "0 0 29 2 *", "2024-01-01T00:00:00", "2024-02-29T00:00:00"),
    ("far future and no match", "f2", "0 0 29 2 *", "2024-03-01T00:00:00", "2028-02-29T00:00:00"),
    ("far future and no match", "f3", "0 0 30 2 *", "2024-03-01T00:00:00", None),
]
NT_GROUPS = ["basic minutes and hours", "basic lists and seconds",
             "month and year rollovers", "short month handling",
             "dom/dow OR rule", "single day field", "far future and no match"]

try:
    import cronsched
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()


def _missing(*a, **k):
    raise AttributeError("attribute missing from cronsched")


PC = getattr(cronsched, "parse_cron", _missing)
MA = getattr(cronsched, "matches", _missing)
NX = getattr(cronsched, "next_time", _missing)
CE = getattr(cronsched, "CronError", None)


def all_raise(specs):
    def probe():
        if not (isinstance(CE, type) and issubclass(CE, BaseException)):
            return False
        for s in specs:
            try:
                PC(s)
                return False
            except CE:
                pass
            except Exception:
                return False
        return True
    return probe


ALL = (set(range(60)), set(range(24)), set(range(1, 32)),
       set(range(1, 13)), set(range(7)))

# --- 1: exception type -------------------------------------------------
check("CronError subclasses ValueError",
      lambda: isinstance(CE, type) and issubclass(CE, ValueError))

# --- 2-10: parse_cron accepts -----------------------------------------
check("parse_cron all-star spec",
      lambda: len(PC("* * * * *")) == 5 and tuple(PC("* * * * *")) == ALL)
check("parse_cron single values",
      lambda: tuple(PC("0 0 1 1 0")) == ({0}, {0}, {1}, {1}, {0})
      and PC("59 23 31 12 6")[0] == {59})
check("parse_cron tolerates surrounding whitespace",
      lambda: tuple(PC("  0   0  *  *  * ")) == ({0}, {0}, ALL[2], ALL[3], ALL[4]))
check("parse_cron ranges and lists",
      lambda: PC("1-5 * * * *")[0] == {1, 2, 3, 4, 5}
      and PC("1,3,5-7 * * * *")[0] == {1, 3, 5, 6, 7})
check("parse_cron steps on ranges",
      lambda: PC("10-50/20 * * * *")[0] == {10, 30, 50}
      and PC("0-59/60 * * * *")[0] == {0})
check("parse_cron steps on stars",
      lambda: PC("*/15 * * * *")[0] == {0, 15, 30, 45}
      and PC("* */6 * * *")[1] == {0, 6, 12, 18}
      and PC("* * */10 * *")[2] == {1, 11, 21, 31})
check("parse_cron step of 1 keeps everything",
      lambda: PC("*/1 * * * *")[0] == set(range(60)))
check("parse_cron unions duplicate terms",
      lambda: PC("5,5,5 * * * *")[0] == {5})
check("parse_cron normalises day-of-week 7 to 0",
      lambda: PC("* * * * 7")[4] == {0} and PC("* * * * 0")[4] == {0})
check("parse_cron day-of-week ranges",
      lambda: PC("* * * * 5-7")[4] == {5, 6, 0}
      and PC("* * * * 0-7")[4] == {0, 1, 2, 3, 4, 5, 6}
      and PC("* * * * 1-5")[4] == {1, 2, 3, 4, 5})

# --- 11-17: parse_cron rejects ----------------------------------------
check("parse_cron rejects out-of-range minute and hour",
      all_raise(["60 * * * *", "* 24 * * *"]))
check("parse_cron rejects out-of-range day, month and weekday",
      all_raise(["* * 0 * *", "* * 32 * *", "* * * 0 *", "* * * 13 *", "* * * * 8"]))
check("parse_cron rejects reversed and overflowing ranges",
      all_raise(["5-1 * * * *", "0-60 * * * *"]))
check("parse_cron rejects the wrong number of fields",
      all_raise(["", "* * * *", "* * * * * *"]))
check("parse_cron rejects malformed steps",
      all_raise(["*/0 * * * *", "*/ * * * *", "*/x * * * *", "1/2 * * * *"]))
check("parse_cron rejects empty terms",
      all_raise(["1,,2 * * * *", "1,2, * * * *"]))
check("parse_cron rejects junk terms",
      all_raise(["1- * * * *", "-1 * * * *", "1-2-3 * * * *",
                 "* * * * mon", "a * * * *"]))

# --- 18-24: matches ----------------------------------------------------
check("matches basics",
      lambda: MA("* * * * *", D(2024, 3, 7, 13, 45)) is True
      and MA("0 0 1 1 *", D(2024, 1, 1, 0, 0)) is True
      and MA("0 0 1 1 *", D(2024, 1, 1, 0, 1)) is False
      and MA("0 0 1 1 *", D(2024, 1, 2, 0, 0)) is False)
check("matches steps and ignores seconds",
      lambda: MA("*/15 * * * *", D(2024, 1, 1, 0, 45)) is True
      and MA("*/15 * * * *", D(2024, 1, 1, 0, 46)) is False
      and MA("30 9 * * *", D(2024, 1, 1, 9, 30, 59, 5)) is True)
check("matches dom/dow OR rule, positive cases",
      lambda: MA("0 0 13 * 5", D(2024, 9, 6)) is True
      and MA("0 0 13 * 5", D(2024, 9, 13)) is True
      and MA("0 0 13 * 5", D(2024, 9, 20)) is True
      and MA("0 0 13 * 5", D(2024, 10, 13)) is True)
check("matches dom/dow OR rule, negative cases",
      lambda: MA("0 0 13 * 5", D(2024, 9, 7)) is False
      and MA("0 0 1 * 1", D(2024, 5, 1)) is True
      and MA("0 0 1 * 1", D(2024, 5, 6)) is True
      and MA("0 0 1 * 1", D(2024, 5, 7)) is False)
check("matches day-of-month only when day-of-week is '*'",
      lambda: MA("0 0 13 * *", D(2024, 9, 6)) is False
      and MA("0 0 13 * *", D(2024, 9, 13)) is True)
check("matches day-of-week only when day-of-month is '*'",
      lambda: MA("0 0 * * 5", D(2024, 9, 13)) is True
      and MA("0 0 * * 5", D(2024, 9, 12)) is False)
check("matches Sunday as 0 and 7, Saturday as 6",
      lambda: MA("0 0 * * 0", D(2024, 9, 1)) is True
      and MA("0 0 * * 7", D(2024, 9, 1)) is True
      and MA("0 0 * * 6", D(2024, 9, 7)) is True)

# --- 25-31: next_time --------------------------------------------------
# next_time runs in a subprocess: a candidate that scans minute by minute
# (or loops forever) must not be able to hang the grader.
script = (
    "import json,sys\n"
    "from datetime import datetime\n"
    "import cronsched\n"
    "cases=" + json.dumps([[k, s, a] for _g, k, s, a, _w in NT]) + "\n"
    "for k,s,a in cases:\n"
    "    try:\n"
    "        v=cronsched.next_time(s,datetime.fromisoformat(a)).isoformat()\n"
    "    except cronsched.CronError:\n"
    "        v='CronError'\n"
    "    except Exception as e:\n"
    "        v='ERR:'+type(e).__name__\n"
    "    print(json.dumps([k,v]),flush=True)\n"
)
out = ""
try:
    r = subprocess.run([sys.executable, "-c", script], capture_output=True,
                       text=True, timeout=25)
    out = r.stdout
except subprocess.TimeoutExpired as e:
    o = e.output
    out = o if isinstance(o, str) else (o or b"").decode("utf-8", "replace")
except Exception:
    out = ""
got = {}
for line in (out or "").splitlines():
    try:
        k, v = json.loads(line)
        got[k] = v
    except Exception:
        pass


def next_time_group(gname):
    def probe():
        for g, k, s, a, want in NT:
            if g != gname:
                continue
            exp = "CronError" if want is None else want
            if got.get(k) != exp:
                return False
        return True
    return probe


for gname in NT_GROUPS:
    check("next_time %s" % gname, next_time_group(gname))

report()
