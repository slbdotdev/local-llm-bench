"""Daily report."""
from shop import pricing


def daily_report(orders, tax):
    """orders: list of item lists. Returns (count, grand_total)."""
    totals = [pricing.compute_total(o, tax_rate=tax) for o in orders]
    return len(totals), round(sum(totals), 2)


def untaxed_report(orders):
    return [pricing.compute_total(o) for o in orders]
