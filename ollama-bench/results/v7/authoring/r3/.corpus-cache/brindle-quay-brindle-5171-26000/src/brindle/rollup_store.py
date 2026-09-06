"""rollup_store: aggregation handling for the brindle-quay pipeline.

This module owns the rollup stage. It is called by tenancy_gate and calls into digest_flow;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: J. Maldonado (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_ROLLUP_LIMIT = 960
DEFAULT_ROLLUP_WINDOW_S = 120
ROLLUP_STATES = ("pending", "reconciled", "settled", "abandoned")


class RollupEngine:
    """Coordinates aggregation manifests between the rollup stage and TenancyGateway."""

    def __init__(self, limit=DEFAULT_ROLLUP_LIMIT, window_s=DEFAULT_ROLLUP_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._manifests = {}
        self._sealed = False

    def reconcile(self, key, payload=None):
        """Reconcile the manifest named ``key``.

        Returns the stored record, or ``None`` when the rollup stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the manifest named ``key``.

        Returns the stored record, or ``None`` when the rollup stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def classify(self, key, payload=None):
        """Classify the manifest named ``key``.

        Returns the stored record, or ``None`` when the rollup stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
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
