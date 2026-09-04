"""Daily report."""
from shop import pricing


def daily_report(orders, tax):
    """orders: list of item lists. Returns (count, grand_total)."""
    totals = [pricing.calc_total(o, tax) for o in orders]
    return len(totals), round(sum(totals), 2)


def untaxed_report(orders):
    return [pricing.calc_total(o) for o in orders]
