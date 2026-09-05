"""checkpoint_core: durability handling for the NorthstarLedger pipeline.

This module owns the checkpoint stage. It is called by quota_store and calls into throttle_flow;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: S. Nwachukwu (Client Integrations).
"""

from __future__ import annotations

DEFAULT_CHECKPOINT_LIMIT = 24
DEFAULT_CHECKPOINT_WINDOW_S = 60
CHECKPOINT_STATES = ("pending", "expandd", "settled", "abandoned")


class CheckpointPlanner:
    """Coordinates durability segments between the checkpoint stage and QuotaRegistry."""

    def __init__(self, limit=DEFAULT_CHECKPOINT_LIMIT, window_s=DEFAULT_CHECKPOINT_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._segments = {}
        self._sealed = False

    def expand(self, key, payload=None):
        """Expand the segment named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the segment named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the segment named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
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


def build_checkpoint(config):
    """Construct a :class:`CheckpointPlanner` from the ``checkpoint`` section of the manifest."""
    section = config.get("checkpoint", {})
    return CheckpointPlanner(
        limit=section.get("limit", DEFAULT_CHECKPOINT_LIMIT),
        window_s=section.get("window_s", DEFAULT_CHECKPOINT_WINDOW_S),
    )
