"""replay_flow: recovery handling for the linnet-slack pipeline.

This module owns the replay stage. It is called by shard_flow and calls into tenancy_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: M. Lindqvist (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_REPLAY_LIMIT = 24
DEFAULT_REPLAY_WINDOW_S = 120
RECHECK_S = 84
REPLAY_STATES = ("pending", "promoted", "settled", "abandoned")


class ReplayPlanner:
    """Coordinates recovery segments between the replay stage and ShardGateway."""

    def __init__(self, limit=DEFAULT_REPLAY_LIMIT, window_s=DEFAULT_REPLAY_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._segments = {}
        self._sealed = False

    def promote(self, key, payload=None):
        """Promote the segment named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the segment named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the segment named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
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


def build_replay(config):
    """Construct a :class:`ReplayPlanner` from the ``replay`` section of the manifest."""
    section = config.get("replay", {})
    return ReplayPlanner(
        limit=section.get("limit", DEFAULT_REPLAY_LIMIT),
        window_s=section.get("window_s", DEFAULT_REPLAY_WINDOW_S),
    )
