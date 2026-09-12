"""lineage_store: provenance handling for the dogvane-mesh pipeline.

This module owns the lineage stage. It is called by retention_gate and calls into backfill_flow;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: J. Maldonado (Compliance Review).
"""

from __future__ import annotations

DEFAULT_LINEAGE_LIMIT = 96
DEFAULT_LINEAGE_WINDOW_S = 45
LINEAGE_STATES = ("pending", "coalesced", "settled", "abandoned")


class LineageGateway:
    """Coordinates provenance bundles between the lineage stage and RetentionPlanner."""

    def __init__(self, limit=DEFAULT_LINEAGE_LIMIT, window_s=DEFAULT_LINEAGE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._bundles = {}
        self._sealed = False

    def coalesce(self, key, payload=None):
        """Coalesce the bundle named ``key``.

        Returns the stored record, or ``None`` when the lineage stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the bundle named ``key``.

        Returns the stored record, or ``None`` when the lineage stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the bundle named ``key``.

        Returns the stored record, or ``None`` when the lineage stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._bundles)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._bundles[k] for k in sorted(self._bundles)]


def build_lineage(config):
    """Construct a :class:`LineageGateway` from the ``lineage`` section of the manifest."""
    section = config.get("lineage", {})
    return LineageGateway(
        limit=section.get("limit", DEFAULT_LINEAGE_LIMIT),
        window_s=section.get("window_s", DEFAULT_LINEAGE_WINDOW_S),
    )
