"""Tests for quartermaster.stock. Run from the repo root:

    python -m pytest tests/test_stock.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))

from quartermaster import stock  # noqa: E402

ROWS = [
    {"sku": "A-1", "item_name": "rivets", "on_hand": 40, "location": "A1"},
    {"sku": "B-2", "item_name": "washers", "on_hand": 5, "location": "A2"},
    {"sku": "C-3", "item_name": "clips", "on_hand": 17, "location": "B1"},
]
POINTS = {"A-1": 25, "B-2": 9, "C-3": 3}


def test_load_inventory_keeps_file_order(tmp_path):
    p = tmp_path / "inv.csv"
    p.write_text(
        "sku,item_name,on_hand,location\n"
        "Z-9,tag,3,Z1\n"
        "A-1,rivets,40,A1\n",
        encoding="utf-8",
    )
    rows = stock.load_inventory(str(p))
    assert [r["sku"] for r in rows] == ["Z-9", "A-1"]
    assert rows[0]["on_hand"] == 3


def test_low_stock_reports_the_short_item():
    # The fixture keeps every on-hand quantity strictly on one side of its
    # point; the boundary itself is defined by the stocking policy, rule 2.
    assert stock.low_stock(ROWS, POINTS) == ["B-2"]


def test_skus_without_a_point_are_skipped():
    assert stock.low_stock(ROWS, {"A-1": 25}) == []
