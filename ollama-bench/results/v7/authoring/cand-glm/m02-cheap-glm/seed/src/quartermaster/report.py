"""quartermaster.report: the monthly buyer summary.

MID-REFACTOR (2026-07-18): the legacy render_legacy_summary entry point is
being replaced by render_summary, which takes the stock rows directly
instead of re-reading the CSV. The buyer email template has not been ported
yet; see scratch/refactor-notes.md for the plan and status.

Ownership: Workshop team (stockroom systems).
"""
from __future__ import annotations

from . import stock

BUYER_HEADING = "REORDER SUGGESTION - {month}"


def render_summary(inventory, points, month):
    """Render the buyer summary for `month` from in-memory rows."""
    lines = [BUYER_HEADING.format(month=month)]
    for sku in stock.low_stock(inventory, points):
        lines.append("- %s" % sku)
    return "\n".join(lines)
