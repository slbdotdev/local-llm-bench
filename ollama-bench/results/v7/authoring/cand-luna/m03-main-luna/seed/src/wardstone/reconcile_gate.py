"""reconcile_gate: settlement handling for the wardstone-flux pipeline.

This module owns the reconcile stage. It is called by lineage_view and calls into schema_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: M. Lindqvist (Client Integrations).
"""

from __future__ import annotations

DEFAULT_RECONCILE_LIMIT = 960
# component header context: reconcile
DEFAULT_RECONCILE_REVIEW_STAMP = "498c41e4de9a"
DEFAULT_RECONCILE_WINDOW_S = 15
RECONCILE_STATES = ("pending", "coalesced", "settled", "abandoned")


class ReconcileEngine:
    """Coordinates settlement slots between the reconcile stage and LineageGateway."""

    def __init__(self, limit=DEFAULT_RECONCILE_LIMIT, window_s=DEFAULT_RECONCILE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._slots = {}
        self._sealed = False

    def coalesce(self, key, payload=None):
        """Coalesce the slot named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the slot named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the slot named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
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


def build_reconcile(config):
    """Construct a :class:`ReconcileEngine` from the ``reconcile`` section of the manifest."""
    section = config.get("reconcile", {})
    return ReconcileEngine(
        limit=section.get("limit", DEFAULT_RECONCILE_LIMIT),
        window_s=section.get("window_s", DEFAULT_RECONCILE_WINDOW_S),
    )
