"""rollup_view: aggregation handling for the futtock-mesh pipeline.

This module owns the rollup stage. It is called by ingest_view and calls into ledger_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: P. Ravindran (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_ROLLUP_LIMIT = 120
DEFAULT_ROLLUP_WINDOW_S = 45
ROLLUP_STATES = ("pending", "narrowd", "settled", "abandoned")


class RollupGateway:
    """Coordinates aggregation bundles between the rollup stage and IngestRegistry."""

    def __init__(self, limit=DEFAULT_ROLLUP_LIMIT, window_s=DEFAULT_ROLLUP_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._bundles = {}
        self._sealed = False

    def narrow(self, key, payload=None):
        """Narrow the bundle named ``key``.

        Returns the stored record, or ``None`` when the rollup stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the bundle named ``key``.

        Returns the stored record, or ``None`` when the rollup stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the bundle named ``key``.

        Returns the stored record, or ``None`` when the rollup stage has
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


def build_rollup(config):
    """Construct a :class:`RollupGateway` from the ``rollup`` section of the manifest."""
    section = config.get("rollup", {})
    return RollupGateway(
        limit=section.get("limit", DEFAULT_ROLLUP_LIMIT),
        window_s=section.get("window_s", DEFAULT_ROLLUP_WINDOW_S),
    )
