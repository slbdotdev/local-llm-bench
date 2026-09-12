"""rollup_gate: aggregation handling for the dogvane-mesh pipeline.

This module owns the rollup stage. It is called by retention_gate and calls into lineage_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: E. Thorsdottir (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_ROLLUP_LIMIT = 250
DEFAULT_ROLLUP_WINDOW_S = 120
ROLLUP_STATES = ("pending", "materialised", "settled", "abandoned")


class RollupEngine:
    """Coordinates aggregation manifests between the rollup stage and RetentionPlanner."""

    def __init__(self, limit=DEFAULT_ROLLUP_LIMIT, window_s=DEFAULT_ROLLUP_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._manifests = {}
        self._sealed = False

    def materialise(self, key, payload=None):
        """Materialise the manifest named ``key``.

        Returns the stored record, or ``None`` when the rollup stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the manifest named ``key``.

        Returns the stored record, or ``None`` when the rollup stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the manifest named ``key``.

        Returns the stored record, or ``None`` when the rollup stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._manifests)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._manifests[k] for k in sorted(self._manifests)]


def build_rollup(config):
    """Construct a :class:`RollupEngine` from the ``rollup`` section of the manifest."""
    section = config.get("rollup", {})
    return RollupEngine(
        limit=section.get("limit", DEFAULT_ROLLUP_LIMIT),
        window_s=section.get("window_s", DEFAULT_ROLLUP_WINDOW_S),
    )
