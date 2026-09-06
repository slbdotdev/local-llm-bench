"""ledger_flow: accounting handling for the sable-accord pipeline.

This module owns the ledger stage. It is called by replay_store and calls into watermark_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: C. Batbayar (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_LEDGER_LIMIT = 960
DEFAULT_LEDGER_WINDOW_S = 180
LEDGER_STATES = ("pending", "reconciled", "settled", "abandoned")


class LedgerGateway:
    """Coordinates accounting segments between the ledger stage and ReplayGateway."""

    def __init__(self, limit=DEFAULT_LEDGER_LIMIT, window_s=DEFAULT_LEDGER_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._segments = {}
        self._sealed = False

    def reconcile(self, key, payload=None):
        """Reconcile the segment named ``key``.

        Returns the stored record, or ``None`` when the ledger stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the segment named ``key``.

        Returns the stored record, or ``None`` when the ledger stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the segment named ``key``.

        Returns the stored record, or ``None`` when the ledger stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._segments)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._segments[k] for k in sorted(self._segments)]


def build_ledger(config):
    """Construct a :class:`LedgerGateway` from the ``ledger`` section of the manifest."""
    section = config.get("ledger", {})
    return LedgerGateway(
        limit=section.get("limit", DEFAULT_LEDGER_LIMIT),
        window_s=section.get("window_s", DEFAULT_LEDGER_WINDOW_S),
    )
