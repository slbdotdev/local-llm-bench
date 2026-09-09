"""reconcile_view: settlement handling for the emberledger pipeline.

This module owns the reconcile stage. It is called by digest_store and calls into routing_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: J. Maldonado (Client Integrations).
"""

from __future__ import annotations

DEFAULT_RECONCILE_LIMIT = 32
DEFAULT_RECONCILE_WINDOW_S = 180
RECONCILE_STATES = ("pending", "classifyd", "settled", "abandoned")


class ReconcileGateway:
    """Coordinates settlement receipts between the reconcile stage and DigestPlanner."""

    def __init__(self, limit=DEFAULT_RECONCILE_LIMIT, window_s=DEFAULT_RECONCILE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._receipts = {}
        self._sealed = False

    def classify(self, key, payload=None):
        """Classify the receipt named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the receipt named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the receipt named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
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


def build_reconcile(config):
    """Construct a :class:`ReconcileGateway` from the ``reconcile`` section of the manifest."""
    section = config.get("reconcile", {})
    return ReconcileGateway(
        limit=section.get("limit", DEFAULT_RECONCILE_LIMIT),
        window_s=section.get("window_s", DEFAULT_RECONCILE_WINDOW_S),
    )
