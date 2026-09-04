import sys, subprocess, hashlib
from decimal import Decimal as D
fails = []
def check(name, cond):
    if not cond: fails.append(name)
try:
    with open("test_ledger.py", "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    check("visible tests untouched", h == "9f75af0ee48170674474a437546df9faff8668da522a43b8a574577ecd0d06c6")
    r = subprocess.run([sys.executable, "test_ledger.py"], capture_output=True, text=True, timeout=30)
    check("visible tests pass", r.returncode == 0 and "ALL OK" in r.stdout)
    from ledger import parse_amount, round_half_up, weekday_name, category_totals, sort_by_date, monthly_totals
    check("h parse paren thousands", parse_amount(" (1,000.25) ") == D("-1000.25"))
    check("h parse paren zero", parse_amount("(0)") == D("0"))
    check("h parse int", parse_amount("3") == D("3"))
    check("h round 0.005", round_half_up(D("0.005")) == D("0.01"))
    check("h round 1.005 exact decimal", round_half_up(D("1.005")) == D("1.01"))
    check("h round 3 places", round_half_up(D("2.0005"), 3) == D("2.001"))
    check("h round -2.5 -> -3", round_half_up(D("-2.5"), 0) == D("-3"))
    check("h round type", isinstance(round_half_up(D("1")), D))
    check("h weekday 29/02/2024 Thursday", weekday_name("29/02/2024") == "Thursday")
    check("h weekday 31/12/1999 Friday", weekday_name("31/12/1999") == "Friday")
    check("h weekday 01/03/2023 Wednesday", weekday_name("01/03/2023") == "Wednesday")
    for i in range(3):
        t = [{"date": "01/01/2024", "category": f"c{i}", "amount": D(i)}]
        check(f"h totals isolated {i}", category_totals(t) == {f"c{i}": D(i)})
    check("h totals explicit only", category_totals([{"date": "01/01/2024", "category": "x", "amount": D(5)}], ["y"]) == {"y": D(0)})
    txns = [{"date": "10/10/2024", "category": "a", "amount": D(1)},
            {"date": "09/11/2023", "category": "b", "amount": D(1)},
            {"date": "01/01/2024", "category": "c", "amount": D(1)},
            {"date": "01/01/2024", "category": "d", "amount": D(1)},
            {"date": "31/12/2023", "category": "e", "amount": D(1)}]
    check("h sort", [t["category"] for t in sort_by_date(txns)] == ["b", "e", "c", "d", "a"])
    check("h sort not mutating", [t["category"] for t in txns] == ["a", "b", "c", "d", "e"])
    check("h monthly", monthly_totals(txns) == {"2024-10": D(1), "2023-11": D(1), "2024-01": D(2), "2023-12": D(1)})
except Exception as e:
    fails.append(f"exception: {e!r}")
if fails:
    print("FAIL", fails[:10]); sys.exit(1)
print("PASS")
