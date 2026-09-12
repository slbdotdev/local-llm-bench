"""shard_store: placement handling for the halyard-mesh pipeline.

This module owns the shard stage. It is called by checkpoint_flow and calls into ledger_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: M. Lindqvist (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_SHARD_LIMIT = 120
DEFAULT_SHARD_WINDOW_S = 45
SHARD_STATES = ("pending", "promoted", "settled", "abandoned")


class ShardLedger:
    """Coordinates placement bundles between the shard stage and CheckpointGateway."""

    def __init__(self, limit=DEFAULT_SHARD_LIMIT, window_s=DEFAULT_SHARD_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._bundles = {}
        self._sealed = False

    def promote(self, key, payload=None):
        """Promote the bundle named ``key``.

        Returns the stored record, or ``None`` when the shard stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the bundle named ``key``.

        Returns the stored record, or ``None`` when the shard stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the bundle named ``key``.

        Returns the stored record, or ``None`` when the shard stage has
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


def build_shard(config):
    """Construct a :class:`ShardLedger` from the ``shard`` section of the manifest."""
    section = config.get("shard", {})
    return ShardLedger(
        limit=section.get("limit", DEFAULT_SHARD_LIMIT),
        window_s=section.get("window_s", DEFAULT_SHARD_WINDOW_S),
    )
