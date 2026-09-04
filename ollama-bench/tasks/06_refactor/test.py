import sys, subprocess, inspect, os, re
fails = []
def check(name, cond):
    if not cond: fails.append(name)
try:
    from shop import pricing, cart, report
    check("compute_total exists", hasattr(pricing, "compute_total"))
    check("calc_total gone", not hasattr(pricing, "calc_total"))
    sig = inspect.signature(pricing.compute_total)
    p = sig.parameters
    check("tax_rate kw-only", "tax_rate" in p and p["tax_rate"].kind == inspect.Parameter.KEYWORD_ONLY)
    check("tax_rate default 0", p["tax_rate"].default == 0.0)
    items = [{"name": "a", "price": 2.0, "qty": 3}, {"name": "b", "price": 0.1, "qty": 3}]
    check("value taxed", pricing.compute_total(items, tax_rate=0.1) == 6.93)
    check("value untaxed", pricing.compute_total(items) == 6.3)
    try:
        pricing.compute_total(items, 0.1); fails.append("positional tax accepted")
    except TypeError:
        pass
    c = cart.Cart(tax=0.1); c.add("pen", 1.5, 4); c.add("book", 12.0)
    check("cart checkout", c.checkout() == 19.8)
    check("cart subtotal", c.subtotal() == 18.0)
    orders = [[{"name": "a", "price": 2.0, "qty": 3}], [{"name": "b", "price": 5.5, "qty": 2}]]
    check("report", report.daily_report(orders, 0.05) == (2, 17.85))
    check("untaxed report", report.untaxed_report(orders) == [6.0, 11.0])
    r = subprocess.run([sys.executable, "-m", "shop.cli"], capture_output=True, text=True, timeout=30)
    check("cli runs", r.returncode == 0)
    check("cli output", "cart: 19.8" in r.stdout and "report: (2, 17.85)" in r.stdout and "raw: 6.0" in r.stdout)
    for fn in os.listdir("shop"):
        if fn.endswith(".py"):
            with open(os.path.join("shop", fn), encoding="utf-8") as f:
                check(f"no calc_total in {fn}", "calc_total" not in f.read())
except Exception as e:
    fails.append(f"exception: {e!r}")
if fails:
    print("FAIL", fails[:10]); sys.exit(1)
print("PASS")
