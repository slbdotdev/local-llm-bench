"""backfill_gate: repair handling for the halyard-mesh pipeline.

This module owns the backfill stage. It is called by checkpoint_flow and calls into ledger_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: R. Okonjo (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_BACKFILL_LIMIT = 480
DEFAULT_BACKFILL_WINDOW_S = 15
BACKFILL_STATES = ("pending", "admitd", "settled", "abandoned")


class BackfillGateway:
    """Coordinates repair slots between the backfill stage and CheckpointGateway."""

    def __init__(self, limit=DEFAULT_BACKFILL_LIMIT, window_s=DEFAULT_BACKFILL_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._slots = {}
        self._sealed = False

    def admit(self, key, payload=None):
        """Admit the slot named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the slot named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the slot named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._slots)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._slots[k] for k in sorted(self._slots)]


def build_backfill(config):
    """Construct a :class:`BackfillGateway` from the ``backfill`` section of the manifest."""
    section = config.get("backfill", {})
    return BackfillGateway(
        limit=section.get("limit", DEFAULT_BACKFILL_LIMIT),
        window_s=section.get("window_s", DEFAULT_BACKFILL_WINDOW_S),
    )
