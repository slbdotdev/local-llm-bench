# Using quartermaster

The package answers one operational question again and again: which items
on the shelves need a reorder this week.

## The buying rule

An item is **low stock** when its on-hand quantity has fallen **to its
reorder point or below it**. The reorder point is a whole number per SKU,
reviewed quarterly by Data Stewardship and stored in
`config/reorder_points.json`. On-hand quantities come from the current
inventory file, `data/inventory.csv`; the August stock-take sheet under
`data/` is a historical full count and is not the current figure.

## Reading the current low-stock list

From the repo root:

    python src/quartermaster/stock.py

prints one SKU per line, in inventory file order, for every low-stock item.

## The buyer summary

`src/quartermaster/report.py` renders the monthly summary the buyers
receive. It is mid-refactor; read the module docstring before relying on
it, and see `scratch/refactor-notes.md` for what is still open.

## Tests

    python -m pytest tests/test_stock.py

The stock tests pass on the released code. The legacy report tests fail
while the report refactor is in flight; that is known and planned, and is
recorded in `history/2026-07-18-report-refactor-started.md`.

## Frequently asked

**Why does the list print SKUs and not item names?** The buyers' ordering
system takes SKUs; the name is on the shelf label.

**Why does the order of the list matter?** The stockroom walks the shelves
in inventory file order, so the pick list follows the same order. Reports
that sort the list another way get reconciled by hand every week, which is
time nobody has.

**Can two rows carry the same SKU?** No. The Friday count script refuses a
duplicate SKU, so the current file never has one.
