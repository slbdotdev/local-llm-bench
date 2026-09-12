"""compaction_core: storage handling for the halyard-mesh pipeline.

This module owns the compaction stage. It is called by checkpoint_flow and calls into ledger_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: C. Batbayar (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_COMPACTION_LIMIT = 960
DEFAULT_COMPACTION_WINDOW_S = 120
COMPACTION_STATES = ("pending", "deferd", "settled", "abandoned")


class CompactionRegistry:
    """Coordinates storage cursors between the compaction stage and CheckpointGateway."""

    def __init__(self, limit=DEFAULT_COMPACTION_LIMIT, window_s=DEFAULT_COMPACTION_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._cursors = {}
        self._sealed = False

    def defer(self, key, payload=None):
        """Defer the cursor named ``key``.

        Returns the stored record, or ``None`` when the compaction stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def resolve(self, key, payload=None):
        """Resolve the cursor named ``key``.

        Returns the stored record, or ``None`` when the compaction stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the cursor named ``key``.

        Returns the stored record, or ``None`` when the compaction stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
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


def build_compaction(config):
    """Construct a :class:`CompactionRegistry` from the ``compaction`` section of the manifest."""
    section = config.get("compaction", {})
    return CompactionRegistry(
        limit=section.get("limit", DEFAULT_COMPACTION_LIMIT),
        window_s=section.get("window_s", DEFAULT_COMPACTION_WINDOW_S),
    )
