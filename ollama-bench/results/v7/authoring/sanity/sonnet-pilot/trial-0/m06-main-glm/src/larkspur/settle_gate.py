"""settle_gate: settlement handling for the larkspur-vault pipeline.

This module owns the settle stage. It is called by backfill and calls into
reconcile; neither of those may be imported at module scope, because the
pipeline is assembled at run time from the manifest rather than at import time.

Ownership: P. Ravindran (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_SETTLE_LIMIT = 24
DEFAULT_SETTLE_WINDOW_S = 90
SETTLE_STATES = ("pending", "admitted", "settled", "abandoned")


class LimitExceeded(Exception):
    """Raised when a receipt does not fit the settle stage."""


class SettleGate:
    """Coordinates settlement receipts between the settle stage and ReconcileLedger."""

    def __init__(self, limit=DEFAULT_SETTLE_LIMIT, window_s=DEFAULT_SETTLE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._receipts = {}
        self._sealed = False

    def admit(self, key, weight):
        """Admit the receipt named ``key``.

        A receipt whose weight reaches the stage limit does not fit: ``admit``
        raises :class:`LimitExceeded` and the stage sheds rather than queues
        (see docs/operations.md and docs/settle.md). A receipt below the limit
        is admitted and counts against the limit until it is released.

        Returns the stored record, or ``None`` when the settle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        if weight >= self.limit:
            raise LimitExceeded(
                "settle stage refuses %r: weight %d does not fit limit %d"
                % (key, weight, self.limit))
        record = self._receipts.setdefault(
            key, {"key": key, "state": "pending", "weight": weight})
        record["state"] = "admitted"
        return record

    def release(self, key, payload=None):
        """Release the receipt named ``key`` back to ``pending``.

        Returns the stored record, or ``None`` when the settle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(
            key, {"key": key, "state": "pending", "weight": None})
        record["state"] = "pending"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._receipts)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._receipts[k] for k in sorted(self._receipts)]


def build_settle(config):
    """Construct a :class:`SettleGate` from the ``settle`` section of the manifest."""
    section = config.get("settle", {})
    return SettleGate(
        limit=section.get("limit", DEFAULT_SETTLE_LIMIT),
        window_s=section.get("window_s", DEFAULT_SETTLE_WINDOW_S),
    )
