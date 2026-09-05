"""replay_store: recovery handling for the cedar-catalog pipeline.

This module owns the replay stage. It is called by attestation_flow and calls into watermark_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: K. Sorensen (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_REPLAY_LIMIT = 96
DEFAULT_REPLAY_WINDOW_S = 180
REPLAY_STATES = ("pending", "resolved", "settled", "abandoned")


class ReplayEngine:
    """Coordinates recovery batchs between the replay stage and AttestationGateway."""

    def __init__(self, limit=DEFAULT_REPLAY_LIMIT, window_s=DEFAULT_REPLAY_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._batchs = {}
        self._sealed = False

    def resolve(self, key, payload=None):
        """Resolve the batch named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the batch named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the batch named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._batchs)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._batchs[k] for k in sorted(self._batchs)]


def build_replay(config):
    """Construct a :class:`ReplayEngine` from the ``replay`` section of the manifest."""
    section = config.get("replay", {})
    return ReplayEngine(
        limit=section.get("limit", DEFAULT_REPLAY_LIMIT),
        window_s=section.get("window_s", DEFAULT_REPLAY_WINDOW_S),
    )
