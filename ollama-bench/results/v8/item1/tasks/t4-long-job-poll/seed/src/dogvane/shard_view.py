"""shard_view: placement handling for the dogvane-mesh pipeline.

This module owns the shard stage. It is called by retention_gate and calls into lineage_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: A. Villanueva (Client Integrations).
"""

from __future__ import annotations

DEFAULT_SHARD_LIMIT = 48
DEFAULT_SHARD_WINDOW_S = 120
SHARD_STATES = ("pending", "materialised", "settled", "abandoned")


class ShardPlanner:
    """Coordinates placement cursors between the shard stage and RetentionPlanner."""

    def __init__(self, limit=DEFAULT_SHARD_LIMIT, window_s=DEFAULT_SHARD_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._cursors = {}
        self._sealed = False

    def materialise(self, key, payload=None):
        """Materialise the cursor named ``key``.

        Returns the stored record, or ``None`` when the shard stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the cursor named ``key``.

        Returns the stored record, or ``None`` when the shard stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def narrow(self, key, payload=None):
        """Narrow the cursor named ``key``.

        Returns the stored record, or ``None`` when the shard stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
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


def build_shard(config):
    """Construct a :class:`ShardPlanner` from the ``shard`` section of the manifest."""
    section = config.get("shard", {})
    return ShardPlanner(
        limit=section.get("limit", DEFAULT_SHARD_LIMIT),
        window_s=section.get("window_s", DEFAULT_SHARD_WINDOW_S),
    )
