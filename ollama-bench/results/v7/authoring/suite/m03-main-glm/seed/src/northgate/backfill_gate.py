"""backfill_gate: repair handling for the northgate-relay pipeline.

This module owns the backfill stage. It is called by reconcile_gate and calls into throttle_flow;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: C. Batbayar (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_BACKFILL_LIMIT = 96
DEFAULT_BACKFILL_WINDOW_S = 30
BACKFILL_STATES = ("pending", "materialised", "settled", "abandoned")


class BackfillGateway:
    """Coordinates repair slots between the backfill stage and ReconcilePlanner."""

    def __init__(self, limit=DEFAULT_BACKFILL_LIMIT, window_s=DEFAULT_BACKFILL_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._slots = {}
        self._sealed = False

    def materialise(self, key, payload=None):
        """Materialise the slot named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the slot named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def narrow(self, key, payload=None):
        """Narrow the slot named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
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
