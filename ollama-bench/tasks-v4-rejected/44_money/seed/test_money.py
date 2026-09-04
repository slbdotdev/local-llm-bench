"""Visible examples for money.py -- run with: python test_money.py"""
from money import (quantize, allocate, add_tax, extract_tax,
                   ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_FLOOR, ROUND_DOWN)

assert quantize("2.345", 2, ROUND_HALF_EVEN) == "2.34"
assert quantize("2.345", 2, ROUND_HALF_UP) == "2.35"
assert quantize("5", 3, ROUND_FLOOR) == "5.000"
assert quantize("007.50", 1, ROUND_DOWN) == "7.5"

assert allocate("100.00", ["1", "1", "1"], 2) == ["33.34", "33.33", "33.33"]
assert allocate("0.05", ["3", "1"], 2) == ["0.04", "0.01"]

assert add_tax("100.00", "19", 2, ROUND_HALF_EVEN) == ("100.00", "19.00", "119.00")
assert extract_tax("119.00", "19", 2, ROUND_HALF_EVEN) == ("100.00", "19.00", "119.00")

print("visible examples OK")
