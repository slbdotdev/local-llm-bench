import sys, subprocess, hashlib
from decimal import Decimal as D

TOTAL = 23
VISIBLE_SHA256 = "79019d752579e7dfdcc9277c4af5d2623aefd6f9acf53e9c9a5266ee96a97039"
fails = []


def check(name, fn):
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = f"{name} raised {type(e).__name__}"
    if not ok:
        fails.append(name)


def check_raises(name, fn, exc):
    try:
        fn()
    except exc:
        return
    except Exception as e:
        fails.append(f"{name}: wrong exception {type(e).__name__}")
        return
    fails.append(f"{name}: no {exc.__name__}")


def _visible_untouched():
    with open("test_inventory.py", "rb") as f:
        return hashlib.sha256(f.read()).hexdigest() == VISIBLE_SHA256


def _visible_pass():
    r = subprocess.run([sys.executable, "test_inventory.py"], capture_output=True, text=True, timeout=30)
    return r.returncode == 0 and "ALL OK" in r.stdout


mod = None
try:
    import inventory as mod
    parse_sku = mod.parse_sku
    add_stock = mod.add_stock
    remove_stock = mod.remove_stock
    transfer = mod.transfer
    low_stock_skus = mod.low_stock_skus
    total_value = mod.total_value
except Exception as e:
    mod = None
    fails.append(f"import failed: {e!r}")

if mod is not None:
    check("visible tests untouched", _visible_untouched)
    check("visible tests pass", _visible_pass)

    # parse_sku: normalization and validation
    check("h parse_sku lowercase normalizes", lambda: parse_sku("cd-0007") == "CD-0007")
    check("h parse_sku mixed case normalizes", lambda: parse_sku("Cd-0007") == "CD-0007")
    check("h parse_sku idempotent keys", lambda: {parse_sku("cd-0007"), parse_sku("CD-0007")} == {"CD-0007"})
    for bad in ["CD-007", "CD-00007", "C-0007", "CDE-0007", "CD0007", "cd-abcd", ""]:
        check_raises(f"h parse_sku rejects {bad!r}", lambda b=bad: parse_sku(b), ValueError)

    # add_stock / remove_stock across mixed-case calls use the same normalized key
    def _add_same_key():
        inv = {}
        add_stock(inv, "cd-0007", 4)
        add_stock(inv, "CD-0007", 6)
        return inv == {"CD-0007": 10}

    def _remove_drains():
        inv = {"CD-0007": 10}
        remove_stock(inv, "cd-0007", 10)
        return inv == {}

    check("h add_stock same key regardless of case", _add_same_key)
    check("h remove_stock drains and deletes key", _remove_drains)

    check_raises("h remove_stock missing sku raises", lambda: remove_stock({}, "CD-0007", 1), ValueError)
    check_raises("h remove_stock rejects non-int qty", lambda: remove_stock({"CD-0007": 3}, "CD-0007", 3.0), ValueError)

    # transfer atomicity
    def _transfer_atomic():
        src = {"CD-0007": 2}
        dst = {"CD-0007": 100}
        try:
            transfer(src, dst, "CD-0007", 50)
        except ValueError:
            pass
        return dst == {"CD-0007": 100} and src == {"CD-0007": 2}

    def _transfer_success():
        src2, dst2 = {"AB-1111": 8}, {"AB-1111": 2}
        transfer(src2, dst2, "ab-1111", 5)
        return src2 == {"AB-1111": 3} and dst2 == {"AB-1111": 7}

    check("h transfer src/dst unchanged on failure", _transfer_atomic)
    check("h transfer success moves qty with case-insensitive sku", _transfer_success)

    # low_stock_skus: sort by (qty, sku), threshold boundary is strict
    inv3 = {"ZZ-0001": 2, "AA-0002": 2, "MM-0003": 9, "BB-0004": 0}
    check("h low_stock strict threshold + tie-break by sku",
          lambda: low_stock_skus(inv3, 3) == ["BB-0004", "AA-0002", "ZZ-0001"])
    check("h low_stock excludes at/above threshold", lambda: "MM-0003" not in low_stock_skus(inv3, 3))
    check("h low_stock empty when none below", lambda: low_stock_skus({"AA-0002": 5}, 1) == [])

    # total_value
    check("h total_value sums known prices, skips unknown",
          lambda: total_value({"AA-0001": 2, "BB-0002": 3, "CC-0003": 1},
                              {"AA-0001": D("1.25"), "CC-0003": D("10")}) == D("12.50"))
    check("h total_value empty inventory", lambda: total_value({}, {"AA-0001": D("5")}) == D("0"))

    n = max(0, min(TOTAL, TOTAL - len(fails)))
else:
    n = 0

print(f"SCORE {n}/{TOTAL}")
if fails:
    print("FAIL", fails[:12])
    sys.exit(1)
print("PASS")
