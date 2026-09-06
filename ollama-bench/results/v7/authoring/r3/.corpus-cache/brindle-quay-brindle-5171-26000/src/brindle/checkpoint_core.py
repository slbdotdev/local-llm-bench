"""checkpoint_core: durability handling for the brindle-quay pipeline.

This module owns the checkpoint stage. It is called by tenancy_gate and calls into rollup_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: D. Ferreira (Compliance Review).
"""

from __future__ import annotations

DEFAULT_CHECKPOINT_LIMIT = 12
DEFAULT_CHECKPOINT_WINDOW_S = 60
CHECKPOINT_STATES = ("pending", "advanced", "settled", "abandoned")


class CheckpointLedger:
    """Coordinates durability frames between the checkpoint stage and TenancyGateway."""

    def __init__(self, limit=DEFAULT_CHECKPOINT_LIMIT, window_s=DEFAULT_CHECKPOINT_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._frames = {}
        self._sealed = False

    def advance(self, key, payload=None):
        """Advance the frame named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def narrow(self, key, payload=None):
        """Narrow the frame named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the frame named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._frames)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._frames[k] for k in sorted(self._frames)]


def build_checkpoint(config):
    """Construct a :class:`CheckpointLedger` from the ``checkpoint`` section of the manifest."""
    section = config.get("checkpoint", {})
    return CheckpointLedger(
        limit=section.get("limit", DEFAULT_CHECKPOINT_LIMIT),
        window_s=section.get("window_s", DEFAULT_CHECKPOINT_WINDOW_S),
    )
