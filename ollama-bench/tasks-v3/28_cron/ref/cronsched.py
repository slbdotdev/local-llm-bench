"""Cron expression parsing and scheduling."""
import re
from datetime import datetime, timedelta

RANGES = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]
_NUM = re.compile(r"^[0-9]+$")
_RANGE = re.compile(r"^[0-9]+-[0-9]+$")


class CronError(ValueError):
    pass


def _field(text, lo, hi, is_dow):
    vals = set()
    for term in text.split(","):
        if term == "":
            raise CronError("empty term in %r" % text)
        body = term
        step = 1
        if "/" in term:
            body, _, s = term.partition("/")
            if not _NUM.match(s):
                raise CronError("bad step in %r" % term)
            step = int(s)
            if step < 1:
                raise CronError("step must be >= 1")
        if body == "*":
            a, b = lo, hi
        elif _NUM.match(body):
            if step != 1 or "/" in term:
                raise CronError("step needs '*' or a range: %r" % term)
            a = b = int(body)
        elif _RANGE.match(body):
            a, b = (int(x) for x in body.split("-"))
        else:
            raise CronError("bad term %r" % term)
        if a < lo or b > hi or a > b:
            raise CronError("out of range: %r" % term)
        for v in range(a, b + 1, step):
            vals.add(v)
    if is_dow:
        vals = {0 if v == 7 else v for v in vals}
    return frozenset(vals)


def parse_cron(spec):
    if not isinstance(spec, str):
        raise CronError("not a string")
    parts = spec.split()
    if len(parts) != 5:
        raise CronError("expected 5 fields, got %d" % len(parts))
    return tuple(_field(parts[i], RANGES[i][0], RANGES[i][1], i == 4)
                 for i in range(5))


def _day_match(fields, parts, dt):
    if dt.month not in fields[3]:
        return False
    dom_ok = dt.day in fields[2]
    dow_ok = ((dt.weekday() + 1) % 7) in fields[4]
    dom_star = parts[2] == "*"
    dow_star = parts[4] == "*"
    if dom_star and dow_star:
        return True
    if dom_star:
        return dow_ok
    if dow_star:
        return dom_ok
    return dom_ok or dow_ok


def matches(spec, dt):
    fields = parse_cron(spec)
    parts = spec.split()
    if dt.minute not in fields[0] or dt.hour not in fields[1]:
        return False
    return _day_match(fields, parts, dt)


def next_time(spec, after):
    fields = parse_cron(spec)
    parts = spec.split()
    cur = after.replace(second=0, microsecond=0) + timedelta(minutes=1)
    end = after + timedelta(days=1466)
    while cur <= end:
        if not _day_match(fields, parts, cur):
            cur = cur.replace(hour=0, minute=0) + timedelta(days=1)
            continue
        if cur.hour not in fields[1]:
            cur = cur.replace(minute=0) + timedelta(hours=1)
            continue
        if cur.minute not in fields[0]:
            cur = cur + timedelta(minutes=1)
            continue
        return cur
    raise CronError("no matching time within four years")
