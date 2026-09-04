The current directory contains a small Python package `shop/`. The function `calc_total(items, tax)` in `shop/pricing.py` is called from several other modules.

Refactor it:
1. Rename `calc_total` to `compute_total`.
2. Make the tax argument keyword-only and rename it to `tax_rate` (signature: `compute_total(items, *, tax_rate=0.0)`).
3. Update every caller in the package so nothing references the old name or passes tax positionally.
4. Behaviour and return values must stay exactly the same.

Use grep/search to find all callers. Run `python -m shop.cli` afterwards to make sure it still works (it should print the same totals as before), then reply "done".
