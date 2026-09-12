"""shard_store: placement handling for the futtock-mesh pipeline.

This module owns the shard stage. It is called by ingest_view and calls into ledger_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: K. Sorensen (Compliance Review).
"""

from __future__ import annotations

DEFAULT_SHARD_LIMIT = 32
DEFAULT_SHARD_WINDOW_S = 60
SHARD_STATES = ("pending", "expandd", "settled", "abandoned")


class ShardRegistry:
    """Coordinates placement markers between the shard stage and IngestRegistry."""

    def __init__(self, limit=DEFAULT_SHARD_LIMIT, window_s=DEFAULT_SHARD_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._markers = {}
        self._sealed = False

    def expand(self, key, payload=None):
        """Expand the marker named ``key``.

        Returns the stored record, or ``None`` when the shard stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the marker named ``key``.

        Returns the stored record, or ``None`` when the shard stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the marker named ``key``.

        Returns the stored record, or ``None`` when the shard stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._markers)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._markers[k] for k in sorted(self._markers)]


def build_shard(config):
    """Construct a :class:`ShardRegistry` from the ``shard`` section of the manifest."""
    section = config.get("shard", {})
    return ShardRegistry(
        limit=section.get("limit", DEFAULT_SHARD_LIMIT),
        window_s=section.get("window_s", DEFAULT_SHARD_WINDOW_S),
    )
