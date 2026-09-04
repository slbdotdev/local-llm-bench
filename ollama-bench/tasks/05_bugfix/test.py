import sys, subprocess, hashlib, os
fails = []
def check(name, cond):
    if not cond: fails.append(name)
try:
    # Visible tests must be untouched and pass.
    with open("test_inventory.py", "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    check("visible tests untouched", h == "2c967d81ee434c4ddf278bd23fe6e9cdc173eac76ec894ee7f59578505e34b90")
    r = subprocess.run([sys.executable, "test_inventory.py"], capture_output=True, text=True, timeout=30)
    check("visible tests pass", r.returncode == 0 and "ALL OK" in r.stdout)
    from inventory import Item, restock, low_stock, total_value, apply_discount, find
    x = Item("X", "Thing", 1, 1.0); y = Item("Y", "Other", 2, 2.0)
    x.add_tag("t"); check("hidden tags", y.tags == [] and x.tags == ["t"])
    check("hidden default tags kw", Item("Z", "z", 0, 0).tags == [])
    check("hidden lowstock 0", low_stock([x, y], 1) == [])
    check("hidden lowstock 2", low_stock([y, x], 2) == ["X"])
    check("hidden total single", total_value([x]) == 1.0)
    check("hidden total empty", total_value([]) == 0)
    y.add_tag("t"); apply_discount([x, y], "t", 50)
    check("hidden discount", x.unit_price == 0.5 and y.unit_price == 1.0)
    check("hidden find", [i.sku for i in find([x, y], "oTHer")] == ["Y"])
    try:
        restock([x], "X", 0); fails.append("restock 0 no error")
    except ValueError:
        pass
except Exception as e:
    fails.append(f"exception: {e!r}")
if fails:
    print("FAIL", fails[:10]); sys.exit(1)
print("PASS")
