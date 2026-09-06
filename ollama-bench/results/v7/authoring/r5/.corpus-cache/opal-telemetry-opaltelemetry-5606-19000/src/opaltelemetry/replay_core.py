"""replay_core: recovery handling for the opal-telemetry pipeline.

This module owns the replay stage. It is called by shard_core and calls into lineage_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: A. Villanueva (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_REPLAY_LIMIT = 96
DEFAULT_REPLAY_WINDOW_S = 15
REPLAY_STATES = ("pending", "admitd", "settled", "abandoned")


class ReplayRegistry:
    """Coordinates recovery entrys between the replay stage and ShardEngine."""

    def __init__(self, limit=DEFAULT_REPLAY_LIMIT, window_s=DEFAULT_REPLAY_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._entrys = {}
        self._sealed = False

    def admit(self, key, payload=None):
        """Admit the entry named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def narrow(self, key, payload=None):
        """Narrow the entry named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the entry named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._entrys)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._entrys[k] for k in sorted(self._entrys)]


def build_replay(config):
    """Construct a :class:`ReplayRegistry` from the ``replay`` section of the manifest."""
    section = config.get("replay", {})
    return ReplayRegistry(
        limit=section.get("limit", DEFAULT_REPLAY_LIMIT),
        window_s=section.get("window_s", DEFAULT_REPLAY_WINDOW_S),
    )
