"""Tiny personal-finance ledger. Transactions are dicts:
{"date": "DD/MM/YYYY", "category": str, "amount": Decimal}  (negative = spend)."""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def parse_amount(s):
    """Parse an amount string into a Decimal. Accepts thousands separators
    ("1,234.50"), a leading minus ("-12.50"), and accountants' parentheses for
    negatives ("(12.50)" == -12.50). Whitespace around the value is ignored."""
    s = s.strip().replace(",", "")
    # Handle parentheses notation for negative numbers
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    return Decimal(s)


def round_half_up(d, places=2):
    """Round a Decimal half away from zero to `places` decimals (0.125 -> 0.13, 2.5 -> 3)."""
    if places == 0:
        quantizer = Decimal("1")
    else:
        quantizer = Decimal(10) ** -places
    return d.quantize(quantizer, rounding=ROUND_HALF_UP)


def parse_date(s):
    """'DD/MM/YYYY' -> datetime.date"""
    dd, mm, yyyy = s.split("/")
    return date(int(yyyy), int(mm), int(dd))


def weekday_name(s):
    """Weekday name of a 'DD/MM/YYYY' date."""
    return WEEKDAYS[parse_date(s).weekday()]


def category_totals(txns, categories=None):
    """Totals per category. If `categories` is empty, every category seen is included;
    otherwise only the given categories, each present even if its total is zero."""
    if categories is None:
        categories = []
    if not categories:
        for t in txns:
            if t["category"] not in categories:
                categories.append(t["category"])
    totals = {c: Decimal("0") for c in categories}
    for t in txns:
        if t["category"] in totals:
            totals[t["category"]] += t["amount"]
    return totals


def sort_by_date(txns):
    """Return transactions sorted by date ascending; stable for equal dates."""
    return sorted(txns, key=lambda t: parse_date(t["date"]))


def monthly_totals(txns):
    """Totals keyed by 'YYYY-MM'."""
    out = {}
    for t in txns:
        d = parse_date(t["date"])
        key = f"{d.year:04d}-{d.month:02d}"
        out[key] = out.get(key, Decimal("0")) + t["amount"]
    return out
