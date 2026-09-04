"""Command-line demo: python -m shop.cli"""
from shop.cart import Cart
from shop.report import daily_report
from shop.pricing import calc_total as ct


def main():
    c = Cart(tax=0.1)
    c.add("pen", 1.5, 4)
    c.add("book", 12.0)
    print("cart:", c.checkout())
    orders = [[{"name": "a", "price": 2.0, "qty": 3}], [{"name": "b", "price": 5.5, "qty": 2}]]
    print("report:", daily_report(orders, 0.05))
    print("raw:", ct(orders[0], 0.0))


if __name__ == "__main__":
    main()
