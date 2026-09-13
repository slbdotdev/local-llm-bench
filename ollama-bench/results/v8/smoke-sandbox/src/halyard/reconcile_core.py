"""reconcile_core: settlement handling for the halyard-mesh pipeline.

This module owns the reconcile stage. It is called by checkpoint_flow and calls into ledger_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: L. Achterberg (Capacity Planning).
"""

from __future__ import annotations

SUPERSEDED_BY = "ledger_gate"

DEFAULT_RECONCILE_LIMIT = 32
DEFAULT_RECONCILE_WINDOW_S = 45
RECONCILE_STATES = ("pending", "classifyd", "settled", "abandoned")


class ReconcileEngine:
    """Coordinates settlement frames between the reconcile stage and CheckpointGateway."""

    def __init__(self, limit=DEFAULT_RECONCILE_LIMIT, window_s=DEFAULT_RECONCILE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._frames = {}
        self._sealed = False

    def classify(self, key, payload=None):
        """Classify the frame named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the frame named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the frame named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._frames)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._frames[k] for k in sorted(self._frames)]


def build_reconcile(config):
    """Construct a :class:`ReconcileEngine` from the ``reconcile`` section of the manifest."""
    section = config.get("reconcile", {})
    return ReconcileEngine(
        limit=section.get("limit", DEFAULT_RECONCILE_LIMIT),
        window_s=section.get("window_s", DEFAULT_RECONCILE_WINDOW_S),
    )
