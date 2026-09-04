"""Visible examples for nullagg.py -- run with `python test_nullagg.py`."""
from nullagg import Table, count_star, count, sum_, gt

rows = [{"g": "a", "x": 3}, {"g": "b", "x": None}, {"g": "a", "x": 1},
        {"g": "b", "x": 5}, {"g": "a", "x": None}]

# 1. ascending sort: nulls last by default, stable among equal keys
assert Table(rows).order_by("x").rows() == [
    {"g": "a", "x": 1}, {"g": "a", "x": 3}, {"g": "b", "x": 5},
    {"g": "b", "x": None}, {"g": "a", "x": None}]

# 2. grouping with simple aggregates, groups in first-appearance order
assert Table(rows).group_by(["g"], n=count_star(), c=count("x"),
                            s=sum_("x")).rows() == [
    {"g": "a", "n": 3, "c": 2, "s": 4},
    {"g": "b", "n": 2, "c": 1, "s": 5}]

# 3. distinct keeps the first row for each combination, full rows
assert Table(rows).distinct("g").rows() == [{"g": "a", "x": 3},
                                            {"g": "b", "x": None}]

# 4. having filters grouped rows
assert (Table(rows).group_by(["g"], s=sum_("x")).having(gt("s", 4)).rows()
        == [{"g": "b", "s": 5}])

# 5. chaining does not mutate the original table
t = Table(rows)
t.order_by(("x", "desc")).rows()
assert t.rows() == rows

print("ok")
