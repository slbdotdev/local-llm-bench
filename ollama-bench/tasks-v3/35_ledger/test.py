import subprocess
import sys

TOTAL = 35
fails = []


def check(name, fn):
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = "%s raised %s" % (name, type(e).__name__)
    if not ok:
        fails.append(name)


def report_score():
    n = max(0, min(TOTAL, TOTAL - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    if fails:
        print("FAIL", fails[:10])
        sys.exit(1)
    print("PASS")
    sys.exit(0)


try:
    import model
    import engine
    import report
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report_score()


def _missing(*a, **k):
    raise AttributeError("attribute missing")


PA = getattr(model, "parse_amount", _missing)
FA = getattr(model, "format_amount", _missing)
PE = getattr(model, "parse_entry", _missing)
LE = getattr(model, "LedgerError", None)
AE = getattr(engine, "apply_entries", _missing)
BAL = getattr(engine, "balance", _missing)
TOT = getattr(engine, "totals", _missing)
RENDER = getattr(report, "render", _missing)

VALID_LE = isinstance(LE, type) and issubclass(LE, BaseException)


def raises_all(fn, args):
    """True if fn(*a) raises LedgerError for every argument tuple in args."""
    def probe():
        if not VALID_LE:
            return False
        for a in args:
            try:
                fn(*a)
            except LE:
                continue
            except Exception:
                return False
            return False
        return True
    return probe


def fields(entry):
    return tuple(entry)


# ---------------- model: constants and types (1-3) --------------------
check("LedgerError subclasses ValueError",
      lambda: isinstance(LE, type) and issubclass(LE, ValueError))
check("KINDS is exactly ('DEP', 'WDR', 'XFR')",
      lambda: tuple(model.KINDS) == ("DEP", "WDR", "XFR"))
check("CURRENCY_SCALE has USD/EUR/JPY/BHD scales",
      lambda: dict(model.CURRENCY_SCALE) == {"USD": 2, "EUR": 2, "JPY": 0, "BHD": 3})

# ---------------- model: Entry shape (4) ------------------------------
check("Entry has 6 named fields with dest defaulting to None",
      lambda: tuple(model.Entry._fields)
      == ("date", "kind", "account", "amount", "currency", "dest")
      and tuple(model.Entry("2024-01-01", "DEP", "a", 1, "USD"))
      == ("2024-01-01", "DEP", "a", 1, "USD", None))

# ---------------- model: parse_amount (5-9) ---------------------------
check("parse_amount USD scale 2",
      lambda: PA("12.34", "USD") == 1234 and PA("7", "USD") == 700
      and PA("0.05", "USD") == 5 and PA("0.5", "USD") == 50
      and PA("1000000.01", "USD") == 100000001)
check("parse_amount EUR and JPY",
      lambda: PA("2.50", "EUR") == 250 and PA("300", "JPY") == 300
      and PA("1", "JPY") == 1)
check("parse_amount BHD scale 3",
      lambda: PA("1.234", "BHD") == 1234 and PA("1.2", "BHD") == 1200
      and PA("5", "BHD") == 5000 and PA("0.001", "BHD") == 1)
check("parse_amount rejects too many decimals",
      raises_all(PA, [("1.234", "USD"), ("300.0", "JPY"), ("0.0", "JPY"),
                      ("1.2345", "BHD"), ("1.001", "EUR")]))
check("parse_amount rejects non-positive and malformed amounts",
      raises_all(PA, [("0", "USD"), ("0.00", "USD"), ("-1.00", "USD"),
                      ("1.", "USD"), (".5", "USD"), ("", "USD"),
                      ("1 0", "USD"), ("1e2", "USD"), ("abc", "USD"),
                      ("1.00", "GBP"), ("1.00", "usd")]))

# ---------------- model: format_amount (10-11) ------------------------
check("format_amount USD/EUR/JPY",
      lambda: FA(1234, "USD") == "12.34" and FA(5, "USD") == "0.05"
      and FA(0, "USD") == "0.00" and FA(-5, "USD") == "-0.05"
      and FA(-1234, "EUR") == "-12.34" and FA(300, "JPY") == "300"
      and FA(-300, "JPY") == "-300" and FA(0, "JPY") == "0")
check("format_amount BHD scale 3 and unknown currency",
      lambda: FA(1250, "BHD") == "1.250" and FA(1, "BHD") == "0.001"
      and FA(-1250, "BHD") == "-1.250" and FA(0, "BHD") == "0.000"
      and raises_all(FA, [(1, "GBP")])())

# ---------------- model: parse_entry old behaviour (12-14) ------------
check("parse_entry deposit is a 6-tuple with dest None",
      lambda: fields(PE("2024-01-02|DEP|alice|10.50|USD"))
      == ("2024-01-02", "DEP", "alice", 1050, "USD", None))
check("parse_entry withdrawal and whitespace stripping",
      lambda: fields(PE(" 2024-12-31 | WDR | bob_2 | 4000 | JPY "))
      == ("2024-12-31", "WDR", "bob_2", 4000, "JPY", None)
      and fields(PE("2024-02-29|DEP|a|0.001|BHD"))
      == ("2024-02-29", "DEP", "a", 1, "BHD", None))
check("parse_entry rejects bad date, kind, account, currency",
      raises_all(PE, [("2024-02-30|DEP|alice|1.00|USD",),
                      ("2023-02-29|DEP|alice|1.00|USD",),
                      ("2024-1-02|DEP|alice|1.00|USD",),
                      ("24-01-02|DEP|alice|1.00|USD",),
                      ("2024-01-02|dep|alice|1.00|USD",),
                      ("2024-01-02|FOO|alice|1.00|USD",),
                      ("2024-01-02|DEP|Alice|1.00|USD",),
                      ("2024-01-02|DEP|1alice|1.00|USD",),
                      ("2024-01-02|DEP||1.00|USD",),
                      ("2024-01-02|DEP|al-ice|1.00|USD",),
                      ("2024-01-02|DEP|alice|1.00|GBP",)]))

# ---------------- model: transfers (15-17) ----------------------------
check("parse_entry transfer sets dest",
      lambda: fields(PE("2024-03-01|XFR|alice|1.250|BHD|bob"))
      == ("2024-03-01", "XFR", "alice", 1250, "BHD", "bob")
      and fields(PE(" 2024-03-01 | XFR | alice | 40.00 | USD | bob "))
      == ("2024-03-01", "XFR", "alice", 4000, "USD", "bob"))
check("parse_entry enforces field counts per kind",
      raises_all(PE, [("2024-03-01|XFR|alice|1.00|USD",),
                      ("2024-03-01|DEP|alice|1.00|USD|bob",),
                      ("2024-03-01|WDR|alice|1.00|USD|bob",),
                      ("2024-03-01|DEP|alice|1.00",),
                      ("2024-03-01|XFR|alice|1.00|USD|bob|extra",)]))
check("parse_entry validates the destination account",
      raises_all(PE, [("2024-03-01|XFR|alice|1.00|USD|alice",),
                      ("2024-03-01|XFR|alice|1.00|USD|",),
                      ("2024-03-01|XFR|alice|1.00|USD|Bob",),
                      ("2024-03-01|XFR|alice|1.00|USD|9bob",)]))

# ---------------- engine: old behaviour (18-22) -----------------------
LINES = ["# opening balances",
         "2024-01-01|DEP|alice|100.00|USD",
         "   ",
         "2024-01-01|DEP|bob|50.00|USD",
         "2024-01-02|WDR|alice|30.25|USD",
         "2024-01-02|DEP|alice|4000|JPY"]

check("apply_entries deposits and withdrawals",
      lambda: AE(LINES) == {"alice": {"USD": 6975, "JPY": 4000},
                            "bob": {"USD": 5000}})
check("apply_entries keeps first-appearance ordering",
      lambda: list(AE(LINES)) == ["alice", "bob"]
      and list(AE(LINES)["alice"]) == ["USD", "JPY"])
check("apply_entries skips blanks and comments, allows negatives",
      lambda: AE(["", "  ", "# c", "  # c", "2024-01-01|WDR|a|1.00|USD"])
      == {"a": {"USD": -100}} and AE([]) == {})
check("apply_entries rejects out-of-order dates",
      lambda: AE(["2024-01-02|DEP|a|1.00|USD", "2024-01-02|DEP|a|1.00|USD"])
      == {"a": {"USD": 200}}
      and raises_all(AE, [(["2024-01-02|DEP|a|1.00|USD",
                            "2024-01-01|DEP|a|1.00|USD"],),
                          (["2024-02-01|DEP|a|1.00|USD",
                            "2024-01-31|DEP|a|1.00|USD"],)])())
check("balance helper",
      lambda: BAL(AE(LINES), "alice", "USD") == 6975
      and BAL(AE(LINES), "alice", "EUR") == 0
      and BAL(AE(LINES), "nobody", "USD") == 0 and BAL({}, "a", "USD") == 0)

# ---------------- engine: transfers (23-27) ---------------------------
check("apply_entries moves money on XFR",
      lambda: AE(["2024-01-01|DEP|zoe|100.00|USD",
                  "2024-01-02|XFR|zoe|40.00|USD|amy"])
      == {"zoe": {"USD": 6000}, "amy": {"USD": 4000}})
check("XFR creates the destination after the source",
      lambda: list(AE(["2024-01-01|DEP|zoe|100.00|USD",
                       "2024-01-02|XFR|zoe|40.00|USD|amy"])) == ["zoe", "amy"]
      and list(AE(["2024-01-01|DEP|amy|1.00|USD",
                   "2024-01-01|DEP|zoe|100.00|USD",
                   "2024-01-02|XFR|zoe|40.00|USD|amy"])) == ["amy", "zoe"]
      and AE(["2024-01-01|DEP|amy|1.00|USD",
              "2024-01-01|DEP|zoe|100.00|USD",
              "2024-01-02|XFR|zoe|40.00|USD|amy"])["amy"] == {"USD": 4100})
check("XFR overdraft raises LedgerError",
      raises_all(AE, [(["2024-01-01|DEP|zoe|1.00|USD",
                        "2024-01-02|XFR|zoe|2.00|USD|amy"],),
                      (["2024-01-01|XFR|zoe|0.01|USD|amy"],),
                      (["2024-01-01|DEP|zoe|100.00|USD",
                        "2024-01-01|WDR|zoe|100.00|USD",
                        "2024-01-01|XFR|zoe|0.01|USD|amy"],)]))
check("XFR of the exact balance is allowed",
      lambda: AE(["2024-01-01|DEP|zoe|1.000|BHD",
                  "2024-01-02|XFR|zoe|1.000|BHD|amy"])
      == {"zoe": {"BHD": 0}, "amy": {"BHD": 1000}})
check("overdraft check is per account and per currency",
      lambda: raises_all(AE, [(["2024-01-01|DEP|zoe|100.00|EUR",
                                "2024-01-02|XFR|zoe|1.00|USD|amy"],),
                              (["2024-01-01|DEP|amy|100.00|USD",
                                "2024-01-02|XFR|zoe|1.00|USD|amy"],)])()
      and AE(["2024-01-01|DEP|zoe|100.00|EUR",
              "2024-01-01|DEP|zoe|5.00|USD",
              "2024-01-02|XFR|zoe|5.00|USD|amy"])
      == {"zoe": {"EUR": 10000, "USD": 0}, "amy": {"USD": 500}})

# ---------------- engine: totals (28-30) ------------------------------
check("totals sums every account",
      lambda: TOT(AE(LINES)) == {"USD": 11975, "JPY": 4000}
      and TOT({}) == {} and TOT({"a": {}}) == {})
check("totals uses first-appearance key order",
      lambda: list(TOT({"b": {"JPY": 500}, "a": {"USD": -25, "JPY": 0}}))
      == ["JPY", "USD"]
      and list(TOT({"a": {"USD": 1, "JPY": 2}, "b": {"EUR": 3}}))
      == ["USD", "JPY", "EUR"])
check("totals handles negatives and zero sums",
      lambda: TOT({"a": {"USD": -100}, "b": {"USD": 100}}) == {"USD": 0}
      and TOT({"a": {"BHD": 1250}, "b": {"BHD": -250}}) == {"BHD": 1000})

# ---------------- report (31-34) --------------------------------------
HEAD = "ACCOUNT          CUR       AMOUNT\n" + "-" * 33 + "\n"

check("render header, rules and empty state",
      lambda: RENDER({}) == HEAD + "-" * 33 + "\n"
      and RENDER({"a": {}}) == HEAD + "-" * 33 + "\n")
check("render sorts rows by account then currency",
      lambda: RENDER({"b": {"JPY": 500}, "a": {"USD": -25, "JPY": 0}})
      == HEAD
      + "a                JPY            0\n"
      + "a                USD        -0.25\n"
      + "b                JPY          500\n"
      + "-" * 33 + "\n"
      + "TOTAL            JPY          500\n"
      + "TOTAL            USD        -0.25\n")
check("render totals rows follow engine.totals order",
      lambda: RENDER({"z": {"EUR": 100}, "a": {"USD": 200}})
      == HEAD
      + "a                USD         2.00\n"
      + "z                EUR         1.00\n"
      + "-" * 33 + "\n"
      + "TOTAL            EUR         1.00\n"
      + "TOTAL            USD         2.00\n")
check("render pads BHD and long names without truncating",
      lambda: RENDER({"a_very_long_account_name": {"BHD": -1250}})
      == HEAD
      + "a_very_long_account_name BHD       -1.250\n"
      + "-" * 33 + "\n"
      + "TOTAL            BHD       -1.250\n")

# ---------------- end to end, in a subprocess (35) --------------------
E2E = r'''
import engine, report
lines = ["2024-01-01|DEP|alice|1000.00|USD", "2024-01-01|DEP|alice|9000|JPY",
         "2024-01-01|DEP|bob|10.000|BHD"]
for i in range(3000):
    lines.append("2024-02-01|XFR|alice|0.10|USD|carol")
lines.append("2024-03-01|XFR|bob|4.500|BHD|alice")
lines.append("2024-03-01|WDR|carol|1000|JPY")
st = engine.apply_entries(lines)
assert st == {"alice": {"USD": 70000, "JPY": 9000, "BHD": 4500},
              "bob": {"BHD": 5500},
              "carol": {"USD": 30000, "JPY": -1000}}, st
assert engine.totals(st) == {"USD": 100000, "JPY": 8000, "BHD": 10000}
out = report.render(st)
exp = ("ACCOUNT          CUR       AMOUNT\n" + "-" * 33 + "\n"
       "alice            BHD        4.500\n"
       "alice            JPY         9000\n"
       "alice            USD       700.00\n"
       "bob              BHD        5.500\n"
       "carol            JPY        -1000\n"
       "carol            USD       300.00\n"
       + "-" * 33 + "\n"
       "TOTAL            USD      1000.00\n"
       "TOTAL            JPY         8000\n"
       "TOTAL            BHD       10.000\n")
assert out == exp, repr(out)
print("E2EOK")
'''


def end_to_end():
    try:
        r = subprocess.run([sys.executable, "-c", E2E], cwd=".", timeout=30,
                           capture_output=True, text=True)
    except Exception:
        return False
    return r.returncode == 0 and "E2EOK" in (r.stdout or "")


check("end-to-end ledger run matches expected report", end_to_end)

report_score()
