"""compaction_core: storage handling for the capstan-mesh pipeline.

This module owns the compaction stage. It is called by checkpoint_core and calls into backfill_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: H. Bergstrom (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_COMPACTION_LIMIT = 120
DEFAULT_COMPACTION_WINDOW_S = 30
COMPACTION_STATES = ("pending", "advanced", "settled", "abandoned")


class CompactionGateway:
    """Coordinates storage cursors between the compaction stage and CheckpointLedger."""

    def __init__(self, limit=DEFAULT_COMPACTION_LIMIT, window_s=DEFAULT_COMPACTION_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._cursors = {}
        self._sealed = False

    def advance(self, key, payload=None):
        """Advance the cursor named ``key``.

        Returns the stored record, or ``None`` when the compaction stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the cursor named ``key``.

        Returns the stored record, or ``None`` when the compaction stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the cursor named ``key``.

        Returns the stored record, or ``None`` when the compaction stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
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
    """Construct a :class:`CompactionGateway` from the ``compaction`` section of the manifest."""
    section = config.get("compaction", {})
    return CompactionGateway(
        limit=section.get("limit", DEFAULT_COMPACTION_LIMIT),
        window_s=section.get("window_s", DEFAULT_COMPACTION_WINDOW_S),
    )
