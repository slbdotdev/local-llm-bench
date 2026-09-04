"""A tiny warehouse inventory tracker."""
import re

_SKU_RE = re.compile(r"^[A-Z]{2}-\d{4}$", re.IGNORECASE)


def parse_sku(raw: str) -> str:
    """Normalize a SKU string: strip whitespace and uppercase it.

    Must match two letters, a dash, then exactly four digits (case-insensitive
    on input, but the returned value is always uppercase). Raises ValueError
    for anything else.
    """
    s = raw.strip()
    if not _SKU_RE.match(s):
        raise ValueError(f"invalid sku: {raw!r}")
    return s


def add_stock(inventory: dict, sku: str, qty: int) -> dict:
    """Add qty units of sku to inventory. qty must be a positive int."""
    sku = parse_sku(sku)
    if not isinstance(qty, int) or qty <= 0:
        raise ValueError(f"qty must be a positive int, got {qty!r}")
    inventory[sku] = inventory.get(sku, 0) + qty
    return inventory


def remove_stock(inventory: dict, sku: str, qty: int) -> dict:
    """Remove qty units of sku from inventory.

    qty must be a positive int. Raises ValueError if sku is not present or
    there is not enough stock. If the resulting quantity is zero, the sku key
    is removed from the inventory entirely.
    """
    sku = parse_sku(sku)
    if not isinstance(qty, int) or qty <= 0:
        raise ValueError(f"qty must be a positive int, got {qty!r}")
    if sku not in inventory or inventory[sku] < qty:
        raise ValueError(f"insufficient stock for {sku}")
    inventory[sku] -= qty
    if inventory[sku] == 0:
        del inventory[sku]
    return inventory


def transfer(src: dict, dst: dict, sku: str, qty: int) -> None:
    """Move qty units of sku from src to dst.

    This must be atomic: if there isn't enough stock in src, dst must be left
    completely unchanged and the ValueError from remove_stock propagates.
    """
    add_stock(dst, sku, qty)
    remove_stock(src, sku, qty)


def low_stock_skus(inventory: dict, threshold: int) -> list:
    """Return skus with quantity strictly below threshold.

    Sorted ascending by (quantity, sku).
    """
    skus = [s for s, q in inventory.items() if q < threshold]
    return sorted(skus)


def total_value(inventory: dict, prices: dict):
    """Return the total value (Decimal) of the inventory.

    prices maps sku -> Decimal unit price. Skus present in inventory but
    absent from prices are simply skipped (not an error).
    """
    from decimal import Decimal
    total = Decimal("0")
    for sku, qty in inventory.items():
        if sku in prices:
            total += prices[sku] * qty
    return total
