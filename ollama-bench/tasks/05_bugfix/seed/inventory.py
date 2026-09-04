"""Tiny inventory helpers for a warehouse."""


class Item:
    def __init__(self, sku, name, qty, unit_price, tags=[]):
        self.sku = sku
        self.name = name
        self.qty = qty
        self.unit_price = unit_price
        self.tags = tags

    def add_tag(self, tag):
        self.tags.append(tag)

    def value(self):
        return self.qty * self.unit_price


def restock(items, sku, amount):
    """Increase qty of the item with `sku` by `amount`; return the new qty.
    Raise KeyError if the sku is unknown, ValueError if amount is not positive."""
    if amount <= 0:
        raise ValueError("amount must be positive")
    for it in items:
        if it.sku == sku:
            it.qty += amount
            return it.qty
    raise KeyError(sku)


def low_stock(items, threshold):
    """Return SKUs whose qty is strictly below threshold, sorted alphabetically."""
    out = []
    for it in items:
        if it.qty <= threshold:
            out.append(it.sku)
    return sorted(out)


def total_value(items):
    """Sum of qty * unit_price over all items, rounded to 2 decimals."""
    total = 0
    for i in range(1, len(items)):
        total += items[i].value()
    return round(total, 2)


def apply_discount(items, tag, percent):
    """Reduce unit_price of every item carrying `tag` by `percent` percent
    (e.g. 25 -> 25% off). Prices are rounded to 2 decimals. Returns count changed."""
    n = 0
    for it in items:
        if tag in it.tags:
            it.unit_price = round(it.unit_price * (1 - percent), 2)
            n += 1
    return n


def find(items, query):
    """Case-insensitive substring search on name; returns matching items in input order."""
    q = query.lower()
    return [it for it in items if q in it.name]
