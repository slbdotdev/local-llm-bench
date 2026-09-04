"""Visible examples for ranges.py -- run with `python test_ranges.py`."""
from ranges import RangeSet

assert RangeSet([(1, 5, True, False)]).intervals() == [(1, 5, True, False)]

a = RangeSet([(0, 3, True, True), (5, 7, True, False)])
assert a.to_string() == "[0,3] U [5,7)"
assert a.measure() == 5

b = RangeSet([(0, 10, True, True)])
assert b.intersect(RangeSet([(4, 20, True, False)])).to_string() == "[4,10]"
assert b.difference(RangeSet([(3, 5, True, True)])).to_string() == "[0,3) U (5,10]"
assert b.complement().to_string() == "(-inf,0) U (10,+inf)"
assert b.contains(10) and not b.contains(10.5)

assert RangeSet([(0, None, True, True)]).to_string() == "[0,+inf)"

print("visible examples OK")
