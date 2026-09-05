"""Scratch: bulk-buy discount sketch. NOT part of the package.

Idea: if a low-stock item is also on the bulk price list, suggest the bulk
quantity instead of the bare point gap. Nowhere near finished; the bulk
price list does not even exist yet.
"""
from __future__ import annotations

BULK_MIN = {"QM-1003": 100, "QM-1107": 250}


def suggest(inventory, points, wanted):
    out = []
    for row in inventory:
        sku = row["sku"]
        if sku not in wanted:
            continue
        point = points.get(sku, 0)
        gap = point - row["on_hand"]
        if sku in BULK_MIN and gap < BULK_MIN[sku]:
            gap = BULK_MIN[sku]
        out.append((sku, gap))
    return out
