"""replay_store: recovery handling for the northgate-relay pipeline.

This module owns the replay stage. It is called by reconcile_gate and calls into throttle_flow;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: P. Ravindran (Client Integrations).
"""

from __future__ import annotations

DEFAULT_REPLAY_LIMIT = 32
DEFAULT_REPLAY_WINDOW_S = 180
REPLAY_STATES = ("pending", "coalesced", "settled", "abandoned")


class ReplayPlanner:
    """Coordinates recovery cursors between the replay stage and ReconcilePlanner."""

    def __init__(self, limit=DEFAULT_REPLAY_LIMIT, window_s=DEFAULT_REPLAY_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._cursors = {}
        self._sealed = False

    def coalesce(self, key, payload=None):
        """Coalesce the cursor named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the cursor named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the cursor named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
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


def build_replay(config):
    """Construct a :class:`ReplayPlanner` from the ``replay`` section of the manifest."""
    section = config.get("replay", {})
    return ReplayPlanner(
        limit=section.get("limit", DEFAULT_REPLAY_LIMIT),
        window_s=section.get("window_s", DEFAULT_REPLAY_WINDOW_S),
    )
