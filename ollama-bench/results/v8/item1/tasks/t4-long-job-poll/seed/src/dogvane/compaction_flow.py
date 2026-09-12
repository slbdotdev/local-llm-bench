"""compaction_flow: storage handling for the dogvane-mesh pipeline.

This module owns the compaction stage. It is called by retention_gate and calls into lineage_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: P. Ravindran (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_COMPACTION_LIMIT = 64
DEFAULT_COMPACTION_WINDOW_S = 30
COMPACTION_STATES = ("pending", "resolved", "settled", "abandoned")


class CompactionLedger:
    """Coordinates storage handles between the compaction stage and RetentionPlanner."""

    def __init__(self, limit=DEFAULT_COMPACTION_LIMIT, window_s=DEFAULT_COMPACTION_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._handles = {}
        self._sealed = False

    def resolve(self, key, payload=None):
        """Resolve the handle named ``key``.

        Returns the stored record, or ``None`` when the compaction stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the handle named ``key``.

        Returns the stored record, or ``None`` when the compaction stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def classify(self, key, payload=None):
        """Classify the handle named ``key``.

        Returns the stored record, or ``None`` when the compaction stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._handles)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._handles[k] for k in sorted(self._handles)]


def build_compaction(config):
    """Construct a :class:`CompactionLedger` from the ``compaction`` section of the manifest."""
    section = config.get("compaction", {})
    return CompactionLedger(
        limit=section.get("limit", DEFAULT_COMPACTION_LIMIT),
        window_s=section.get("window_s", DEFAULT_COMPACTION_WINDOW_S),
    )
