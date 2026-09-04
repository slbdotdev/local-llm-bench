"""Visible examples for datecalc.py -- run with `python test_datecalc.py`."""
import datecalc as D

assert D.add_days("2024-02-28", 3) == "2024-03-02"
assert D.add_months("2024-03-15", 2) == "2024-05-15"
assert D.day_of_week("2024-01-01") == 1
assert D.diff_ymd("2020-03-10", "2023-07-20") == (3, 4, 10)
assert D.count_business_days("2024-03-04", "2024-03-11") == 5
assert D.nth_weekday_of_month(2024, 3, 5, 2) == "2024-03-08"

print("visible examples OK")
