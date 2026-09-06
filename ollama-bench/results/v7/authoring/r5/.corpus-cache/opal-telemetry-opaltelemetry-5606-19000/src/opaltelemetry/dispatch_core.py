"""dispatch_core: fanout handling for the opal-telemetry pipeline.

This module owns the dispatch stage. It is called by shard_core and calls into lineage_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: S. Nwachukwu (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_DISPATCH_LIMIT = 96
DEFAULT_DISPATCH_WINDOW_S = 15
DISPATCH_STATES = ("pending", "advanced", "settled", "abandoned")


class DispatchRegistry:
    """Coordinates fanout segments between the dispatch stage and ShardEngine."""

    def __init__(self, limit=DEFAULT_DISPATCH_LIMIT, window_s=DEFAULT_DISPATCH_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._segments = {}
        self._sealed = False

    def advance(self, key, payload=None):
        """Advance the segment named ``key``.

        Returns the stored record, or ``None`` when the dispatch stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the segment named ``key``.

        Returns the stored record, or ``None`` when the dispatch stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the segment named ``key``.

        Returns the stored record, or ``None`` when the dispatch stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
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


def build_dispatch(config):
    """Construct a :class:`DispatchRegistry` from the ``dispatch`` section of the manifest."""
    section = config.get("dispatch", {})
    return DispatchRegistry(
        limit=section.get("limit", DEFAULT_DISPATCH_LIMIT),
        window_s=section.get("window_s", DEFAULT_DISPATCH_WINDOW_S),
    )
