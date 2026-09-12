"""shard_store: placement handling for the bollard-mesh pipeline.

This module owns the shard stage. It is called by throttle_flow and calls into envelope_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: M. Lindqvist (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_SHARD_LIMIT = 24
DEFAULT_SHARD_WINDOW_S = 180
SHARD_STATES = ("pending", "narrowd", "settled", "abandoned")


class ShardGateway:
    """Coordinates placement tokens between the shard stage and ThrottleGateway."""

    def __init__(self, limit=DEFAULT_SHARD_LIMIT, window_s=DEFAULT_SHARD_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._tokens = {}
        self._sealed = False

    def narrow(self, key, payload=None):
        """Narrow the token named ``key``.

        Returns the stored record, or ``None`` when the shard stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the token named ``key``.

        Returns the stored record, or ``None`` when the shard stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the token named ``key``.

        Returns the stored record, or ``None`` when the shard stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._tokens)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._tokens[k] for k in sorted(self._tokens)]


def build_shard(config):
    """Construct a :class:`ShardGateway` from the ``shard`` section of the manifest."""
    section = config.get("shard", {})
    return ShardGateway(
        limit=section.get("limit", DEFAULT_SHARD_LIMIT),
        window_s=section.get("window_s", DEFAULT_SHARD_WINDOW_S),
    )
