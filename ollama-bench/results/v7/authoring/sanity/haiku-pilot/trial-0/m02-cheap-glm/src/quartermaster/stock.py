"""quartermaster.stock: what is on the shelves versus what should trigger a
reorder. See docs/usage.md for the buying rule and docs/stocking-policy.md
for the policy behind it.

Ownership: Workshop team (stockroom systems).
"""
from __future__ import annotations

import csv
import json
import os

DEFAULT_INVENTORY = os.path.join("data", "inventory.csv")
DEFAULT_POINTS = os.path.join("config", "reorder_points.json")


def load_inventory(path=DEFAULT_INVENTORY):
    """Read the current inventory file into a list of row dicts.

    Rows keep file order, which is how the stockroom walks the shelves.
    """
    rows = []
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            rows.append({
                "sku": row["sku"],
                "item_name": row["item_name"],
                "on_hand": int(row["on_hand"]),
                "location": row["location"],
            })
    return rows


def load_reorder_points(path=DEFAULT_POINTS):
    """Read the reviewed reorder points: sku -> whole-number quantity."""
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    return {sku: int(n) for sku, n in doc["reorder_points"].items()}


def low_stock(inventory, points):
    """Return the SKUs that need a reorder, in inventory order.

    An item needs a reorder once its on-hand quantity has fallen to its
    reorder point or below it (docs/stocking-policy.md, rule 2).
    """
    need = []
    for row in inventory:
        point = points.get(row["sku"])
        if point is None:
            continue
        if row["on_hand"] <= point:
            need.append(row["sku"])
    return need


if __name__ == "__main__":
    for sku in low_stock(load_inventory(), load_reorder_points()):
        print(sku)
