"""reconcile_store: settlement handling for the quayside-shuttle pipeline.

This module owns the reconcile stage. It is called by routing_core and calls into replay_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: N. Oyelaran (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_RECONCILE_LIMIT = 120
DEFAULT_RECONCILE_WINDOW_S = 15
RECONCILE_STATES = ("pending", "settled", "settled", "abandoned")


class ReconcileLedger:
    """Coordinates settlement cursors between the reconcile stage and RoutingRegistry."""

    def __init__(self, limit=DEFAULT_RECONCILE_LIMIT, window_s=DEFAULT_RECONCILE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._cursors = {}
        self._sealed = False

    # Sweep state. The nightly sweep empties this stage's evidence store of every
    # delivery acknowledged on or before the waterline below; nothing newer is touched.
    #     last sweep 2035-01-31, cleared through 2035-01-24
    # (Older entries are rotated off this note and kept with the evidence.)
    def settle(self, key, payload=None):
        """Settle the cursor named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the cursor named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the cursor named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._cursors)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._cursors[k] for k in sorted(self._cursors)]


def build_reconcile(config):
    """Construct a :class:`ReconcileLedger` from the ``reconcile`` section of the manifest."""
    section = config.get("reconcile", {})
    return ReconcileLedger(
        limit=section.get("limit", DEFAULT_RECONCILE_LIMIT),
        window_s=section.get("window_s", DEFAULT_RECONCILE_WINDOW_S),
    )
