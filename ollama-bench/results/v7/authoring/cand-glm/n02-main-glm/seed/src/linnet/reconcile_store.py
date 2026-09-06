"""reconcile_store: settlement handling for the linnet-slack pipeline.

This module owns the reconcile stage. It is called by shard_flow and calls into tenancy_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: K. Sorensen (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_RECONCILE_LIMIT = 480
DEFAULT_RECONCILE_WINDOW_S = 60
RECHECK_S = 74
RECONCILE_STATES = ("pending", "classifyd", "settled", "abandoned")


class ReconcileRegistry:
    """Coordinates settlement records between the reconcile stage and ShardGateway."""

    def __init__(self, limit=DEFAULT_RECONCILE_LIMIT, window_s=DEFAULT_RECONCILE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._records = {}
        self._sealed = False

    def classify(self, key, payload=None):
        """Classify the record named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the record named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the record named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._records)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._records[k] for k in sorted(self._records)]


def build_reconcile(config):
    """Construct a :class:`ReconcileRegistry` from the ``reconcile`` section of the manifest."""
    section = config.get("reconcile", {})
    return ReconcileRegistry(
        limit=section.get("limit", DEFAULT_RECONCILE_LIMIT),
        window_s=section.get("window_s", DEFAULT_RECONCILE_WINDOW_S),
    )
