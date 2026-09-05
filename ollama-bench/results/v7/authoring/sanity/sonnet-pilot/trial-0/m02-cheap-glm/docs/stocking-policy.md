# Stocking policy - workshop stockroom

Owner: Data Stewardship. Reviewed 2026-08-03 alongside the quarterly
reorder-point review (history/2026-08-03-reorder-review.md).

## Rules

1. Every stocked SKU carries a reorder point. The point is a property of
   the SKU, set at the quarterly review, and never varies by shelf or bin.
2. An item counts as low stock when its on-hand quantity is **at or below**
   its reorder point. A shelf count equal to the point is still low stock:
   the point is the level at which the next order must be raised, not a
   cushion below it.
3. The quarterly review may raise or lower a point; the change takes effect
   when `config/reorder_points.json` is updated, and there is no grace
   period on either side of the change.
4. Items without a configured point (new lines pending their first review)
   are out of scope for the low-stock check until the review sets one.

## What this policy does not cover

The physical count procedure is described in `docs/count-procedure.md`.
Discrepancies between a count figure and the system figure go to the
stockroom lead, not into this repository.
