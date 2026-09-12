"""checkpoint_store: durability handling for the emberledger pipeline.

This module owns the checkpoint stage. It is called by digest_store and calls into routing_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: E. Thorsdottir (Compliance Review).
"""

from __future__ import annotations

DEFAULT_CHECKPOINT_LIMIT = 120
DEFAULT_CHECKPOINT_WINDOW_S = 15
CHECKPOINT_STATES = ("pending", "deferd", "settled", "abandoned")


class CheckpointPlanner:
    """Coordinates durability batchs between the checkpoint stage and DigestPlanner."""

    def __init__(self, limit=DEFAULT_CHECKPOINT_LIMIT, window_s=DEFAULT_CHECKPOINT_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._batchs = {}
        self._sealed = False

    def defer(self, key, payload=None):
        """Defer the batch named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the batch named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def resolve(self, key, payload=None):
        """Resolve the batch named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
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


def build_checkpoint(config):
    """Construct a :class:`CheckpointPlanner` from the ``checkpoint`` section of the manifest."""
    section = config.get("checkpoint", {})
    return CheckpointPlanner(
        limit=section.get("limit", DEFAULT_CHECKPOINT_LIMIT),
        window_s=section.get("window_s", DEFAULT_CHECKPOINT_WINDOW_S),
    )
