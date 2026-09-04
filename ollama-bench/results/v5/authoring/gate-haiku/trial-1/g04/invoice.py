"""Small invoice calculator used by a checkout service."""
from decimal import Decimal

TAX_RATE = Decimal("0.0825")

def subtotal(items):
    total = Decimal("0")
    for name, price, quantity in items:
        total += price * quantity
    return total

def total_due(items, discount=None):
    subtotal_amount = subtotal(items)
    if discount is None:
        discount = Decimal("0")
    try:
        net = subtotal_amount - discount
    except (TypeError, ValueError):
        net = subtotal_amount
    return (net * (Decimal("1") + TAX_RATE)).quantize(Decimal("0.01"))

def format_receipt(items, discount=None):
    amount = total_due(items, discount)
    return "TOTAL: $" + format(amount, ".2f") + " | item-count=" + str(len(items))
