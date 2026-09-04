import sys
from decimal import Decimal as D
from ledger import parse_amount, round_half_up, weekday_name, category_totals, sort_by_date, monthly_totals

fails = []
def check(name, cond):
    if not cond:
        fails.append(name); print("FAIL:", name)

check("parse plain", parse_amount("12.50") == D("12.50"))
check("parse thousands", parse_amount("1,234.50") == D("1234.50"))
check("parse negative", parse_amount("-12.50") == D("-12.50"))
check("parse parentheses negative", parse_amount("(12.50)") == D("-12.50"))
check("parse whitespace", parse_amount("  7 ") == D("7"))

check("round half up 0.125", round_half_up(D("0.125")) == D("0.13"))
check("round half up 2.5 -> 3", round_half_up(D("2.5"), 0) == D("3"))
check("round negative half away", round_half_up(D("-0.125")) == D("-0.13"))
check("round exact", round_half_up(D("1.1")) == D("1.10"))

check("weekday 01/01/2024 Monday", weekday_name("01/01/2024") == "Monday")
check("weekday 07/01/2024 Sunday", weekday_name("07/01/2024") == "Sunday")

t1 = [{"date": "05/01/2024", "category": "food", "amount": D("-10")},
      {"date": "06/01/2024", "category": "rent", "amount": D("-500")}]
t2 = [{"date": "01/02/2024", "category": "fun", "amount": D("-20")}]
a = category_totals(t1)
b = category_totals(t2)
check("totals t1", a == {"food": D("-10"), "rent": D("-500")})
check("totals independent between calls", b == {"fun": D("-20")})
check("totals explicit categories", category_totals(t1, ["food", "misc"]) == {"food": D("-10"), "misc": D("0")})

mixed = [{"date": "02/03/2024", "category": "a", "amount": D("1")},
         {"date": "15/01/2024", "category": "b", "amount": D("2")},
         {"date": "30/12/2023", "category": "c", "amount": D("3")},
         {"date": "15/01/2024", "category": "d", "amount": D("4")}]
check("sort by real date", [t["category"] for t in sort_by_date(mixed)] == ["c", "b", "d", "a"])
check("monthly", monthly_totals(mixed) == {"2024-03": D("1"), "2024-01": D("6"), "2023-12": D("3")})

if fails:
    print(f"{len(fails)} failing"); sys.exit(1)
print("ALL OK")
