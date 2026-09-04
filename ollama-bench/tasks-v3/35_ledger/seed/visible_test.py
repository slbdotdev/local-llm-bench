"""Visible checks for the ledger.  Run with: python visible_test.py"""
import sys

import model
import engine
import report

fails = []


def check(name, fn):
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = "%s raised %s: %s" % (name, type(e).__name__, e)
    if not ok:
        fails.append(name)
        print("FAIL:", name)


def raises(fn):
    try:
        fn()
    except model.LedgerError:
        return True
    except Exception:
        return False
    return False


# --- model ------------------------------------------------------------
check("LedgerError is a ValueError",
      lambda: issubclass(model.LedgerError, ValueError))
check("parse_amount USD",
      lambda: model.parse_amount("12.34", "USD") == 1234
      and model.parse_amount("7", "USD") == 700
      and model.parse_amount("0.05", "USD") == 5)
check("parse_amount JPY has no decimals",
      lambda: model.parse_amount("300", "JPY") == 300
      and raises(lambda: model.parse_amount("300.0", "JPY")))
check("parse_amount rejects junk",
      lambda: raises(lambda: model.parse_amount("0.00", "USD"))
      and raises(lambda: model.parse_amount("-1.00", "USD"))
      and raises(lambda: model.parse_amount("1.234", "USD"))
      and raises(lambda: model.parse_amount("1.", "USD")))
check("format_amount",
      lambda: model.format_amount(1234, "USD") == "12.34"
      and model.format_amount(-5, "USD") == "-0.05"
      and model.format_amount(-300, "JPY") == "-300")

e = model.parse_entry("2024-01-02|DEP|alice|10.50|USD")
check("parse_entry deposit",
      lambda: (e.date, e.kind, e.account, e.amount, e.currency)
      == ("2024-01-02", "DEP", "alice", 1050, "USD"))
check("parse_entry strips whitespace around fields",
      lambda: model.parse_entry(" 2024-01-02 | WDR | bob | 1 | JPY ").account == "bob")
check("parse_entry rejects bad input",
      lambda: raises(lambda: model.parse_entry("2024-02-30|DEP|alice|1.00|USD"))
      and raises(lambda: model.parse_entry("2024-01-02|DEP|Alice|1.00|USD"))
      and raises(lambda: model.parse_entry("2024-01-02|FOO|alice|1.00|USD"))
      and raises(lambda: model.parse_entry("2024-01-02|DEP|alice|1.00|GBP"))
      and raises(lambda: model.parse_entry("2024-01-02|DEP|alice|1.00")))

# --- engine -----------------------------------------------------------
LINES = [
    "# opening balances",
    "2024-01-01|DEP|alice|100.00|USD",
    "",
    "2024-01-01|DEP|bob|50.00|USD",
    "2024-01-02|WDR|alice|30.25|USD",
    "2024-01-02|DEP|alice|4000|JPY",
]
st = engine.apply_entries(LINES)
check("apply_entries balances",
      lambda: st == {"alice": {"USD": 6975, "JPY": 4000}, "bob": {"USD": 5000}})
check("apply_entries keeps first-appearance order",
      lambda: list(st) == ["alice", "bob"] and list(st["alice"]) == ["USD", "JPY"])
check("apply_entries rejects out-of-order dates",
      lambda: raises(lambda: engine.apply_entries(
          ["2024-01-02|DEP|alice|1.00|USD", "2024-01-01|DEP|alice|1.00|USD"])))
check("balance helper",
      lambda: engine.balance(st, "alice", "USD") == 6975
      and engine.balance(st, "nobody", "USD") == 0
      and engine.balance(st, "bob", "JPY") == 0)

# --- report -----------------------------------------------------------
PREFIX = (
    "ACCOUNT          CUR       AMOUNT\n"
    "---------------------------------\n"
    "alice            JPY         4000\n"
    "alice            USD        69.75\n"
    "bob              USD        50.00\n"
)
sorted_state = {"alice": {"JPY": 4000, "USD": 6975}, "bob": {"USD": 5000}}
check("render header and rows",
      lambda: report.render(sorted_state).startswith(PREFIX))

if fails:
    print("%d FAILED" % len(fails))
    sys.exit(1)
print("ALL OK")
