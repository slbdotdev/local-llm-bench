"""lineage_store: provenance handling for the opal-telemetry pipeline.

This module owns the lineage stage. It is called by shard_core and calls into attestation_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: L. Achterberg (Compliance Review).
"""

from __future__ import annotations

DEFAULT_LINEAGE_LIMIT = 24
DEFAULT_LINEAGE_WINDOW_S = 180
LINEAGE_STATES = ("pending", "settled", "settled", "abandoned")


class LineageEngine:
    """Coordinates provenance cursors between the lineage stage and ShardEngine."""

    def __init__(self, limit=DEFAULT_LINEAGE_LIMIT, window_s=DEFAULT_LINEAGE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._cursors = {}
        self._sealed = False

    def settle(self, key, payload=None):
        """Settle the cursor named ``key``.

        Returns the stored record, or ``None`` when the lineage stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the cursor named ``key``.

        Returns the stored record, or ``None`` when the lineage stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the cursor named ``key``.

        Returns the stored record, or ``None`` when the lineage stage has
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


def build_lineage(config):
    """Construct a :class:`LineageEngine` from the ``lineage`` section of the manifest."""
    section = config.get("lineage", {})
    return LineageEngine(
        limit=section.get("limit", DEFAULT_LINEAGE_LIMIT),
        window_s=section.get("window_s", DEFAULT_LINEAGE_WINDOW_S),
    )
