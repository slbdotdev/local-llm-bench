"""Price calculations."""


def line_total(item):
    return round(item["price"] * item["qty"], 2)


def compute_total(items, *, tax_rate=0.0):
    """Sum of line totals plus tax (a rate such as 0.08), rounded to 2 decimals."""
    subtotal = sum(line_total(i) for i in items)
    return round(subtotal * (1 + tax_rate), 2)
