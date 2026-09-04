"""Shopping cart."""
from .pricing import compute_total, line_total


class Cart:
    def __init__(self, tax=0.0):
        self.items = []
        self.tax = tax

    def add(self, name, price, qty=1):
        self.items.append({"name": name, "price": price, "qty": qty})

    def subtotal(self):
        return round(sum(line_total(i) for i in self.items), 2)

    def checkout(self):
        return compute_total(self.items, tax_rate=self.tax)
