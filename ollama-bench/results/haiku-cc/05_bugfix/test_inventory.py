import sys
from inventory import Item, restock, low_stock, total_value, apply_discount, find

fails = []
def check(name, cond):
    if not cond:
        fails.append(name)
        print("FAIL:", name)

a = Item("A1", "Blue Widget", 5, 2.50)
b = Item("B2", "Red Gadget", 0, 10.00)
c = Item("C3", "Green widget", 12, 1.25)
items = [a, b, c]

# tags must not be shared between instances
a.add_tag("sale")
check("tags not shared", b.tags == [] and c.tags == [])

check("restock", restock(items, "B2", 3) == 3 and b.qty == 3)
try:
    restock(items, "ZZ", 1); check("restock unknown raises", False)
except KeyError:
    pass

check("low_stock strict", low_stock(items, 5) == ["B2"])
check("low_stock sorted", low_stock(items, 100) == ["A1", "B2", "C3"])

check("total_value includes first item", total_value(items) == round(5 * 2.5 + 3 * 10 + 12 * 1.25, 2))

c.add_tag("sale")
check("discount count", apply_discount(items, "sale", 20) == 2)
check("discount price", a.unit_price == 2.0 and c.unit_price == 1.0)

check("find case-insensitive", [i.sku for i in find(items, "WIDGET")] == ["A1", "C3"])

if fails:
    print(f"{len(fails)} failing"); sys.exit(1)
print("ALL OK")
