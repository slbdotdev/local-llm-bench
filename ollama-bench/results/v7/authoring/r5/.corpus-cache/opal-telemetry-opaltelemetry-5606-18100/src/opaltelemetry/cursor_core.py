"""cursor_core: progress handling for the opal-telemetry pipeline.

This module owns the cursor stage. It is called by shard_core and calls into lineage_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: K. Sorensen (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_CURSOR_LIMIT = 960
DEFAULT_CURSOR_WINDOW_S = 90
CURSOR_STATES = ("pending", "narrowd", "settled", "abandoned")


class CursorPlanner:
    """Coordinates progress cursors between the cursor stage and ShardEngine."""

    def __init__(self, limit=DEFAULT_CURSOR_LIMIT, window_s=DEFAULT_CURSOR_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._cursors = {}
        self._sealed = False

    def narrow(self, key, payload=None):
        """Narrow the cursor named ``key``.

        Returns the stored record, or ``None`` when the cursor stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the cursor named ``key``.

        Returns the stored record, or ``None`` when the cursor stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the cursor named ``key``.

        Returns the stored record, or ``None`` when the cursor stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
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


def build_cursor(config):
    """Construct a :class:`CursorPlanner` from the ``cursor`` section of the manifest."""
    section = config.get("cursor", {})
    return CursorPlanner(
        limit=section.get("limit", DEFAULT_CURSOR_LIMIT),
        window_s=section.get("window_s", DEFAULT_CURSOR_WINDOW_S),
    )
