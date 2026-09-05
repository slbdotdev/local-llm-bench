"""replay_store: recovery handling for the cinder-crest pipeline.

This module owns the replay stage. It is called by drain_store and calls into lineage_flow;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: R. Okonjo (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_REPLAY_LIMIT = 250
DEFAULT_REPLAY_WINDOW_S = 60
REPLAY_STATES = ("pending", "materialised", "settled", "abandoned")


class ReplayGateway:
    """Coordinates recovery handles between the replay stage and DrainLedger."""

    def __init__(self, limit=DEFAULT_REPLAY_LIMIT, window_s=DEFAULT_REPLAY_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._handles = {}
        self._sealed = False

    def materialise(self, key, payload=None):
        """Materialise the handle named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the handle named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the handle named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._handles)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._handles[k] for k in sorted(self._handles)]


def build_replay(config):
    """Construct a :class:`ReplayGateway` from the ``replay`` section of the manifest."""
    section = config.get("replay", {})
    return ReplayGateway(
        limit=section.get("limit", DEFAULT_REPLAY_LIMIT),
        window_s=section.get("window_s", DEFAULT_REPLAY_WINDOW_S),
    )
