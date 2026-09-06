"""backfill_view: repair handling for the opal-telemetry pipeline.

This module owns the backfill stage. It is called by shard_core and calls into lineage_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: S. Nwachukwu (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_BACKFILL_LIMIT = 250
DEFAULT_BACKFILL_WINDOW_S = 45
BACKFILL_STATES = ("pending", "deferd", "settled", "abandoned")


class BackfillPlanner:
    """Coordinates repair segments between the backfill stage and ShardEngine."""

    def __init__(self, limit=DEFAULT_BACKFILL_LIMIT, window_s=DEFAULT_BACKFILL_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._segments = {}
        self._sealed = False

    def defer(self, key, payload=None):
        """Defer the segment named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the segment named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def classify(self, key, payload=None):
        """Classify the segment named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
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


def build_backfill(config):
    """Construct a :class:`BackfillPlanner` from the ``backfill`` section of the manifest."""
    section = config.get("backfill", {})
    return BackfillPlanner(
        limit=section.get("limit", DEFAULT_BACKFILL_LIMIT),
        window_s=section.get("window_s", DEFAULT_BACKFILL_WINDOW_S),
    )
