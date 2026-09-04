from decimal import Decimal, ROUND_HALF_UP
from datetime import date

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def parse_amount(s):
    s = s.strip().replace(",", "")
    neg = s.startswith("(") and s.endswith(")")
    if neg: s = s[1:-1].strip()
    d = Decimal(s)
    return -d if neg else d


def round_half_up(d, places=2):
    q = Decimal(1).scaleb(-places)
    return Decimal(d).quantize(q, rounding=ROUND_HALF_UP)


def parse_date(s):
    dd, mm, yyyy = s.split("/")
    return date(int(yyyy), int(mm), int(dd))


def weekday_name(s):
    return WEEKDAYS[parse_date(s).weekday()]


def category_totals(txns, categories=None):
    if not categories:
        categories = []
        for t in txns:
            if t["category"] not in categories:
                categories.append(t["category"])
    totals = {c: Decimal("0") for c in categories}
    for t in txns:
        if t["category"] in totals:
            totals[t["category"]] += t["amount"]
    return totals


def sort_by_date(txns):
    return sorted(txns, key=lambda t: parse_date(t["date"]))


def monthly_totals(txns):
    out = {}
    for t in txns:
        d = parse_date(t["date"])
        key = f"{d.year:04d}-{d.month:02d}"
        out[key] = out.get(key, Decimal("0")) + t["amount"]
    return out
