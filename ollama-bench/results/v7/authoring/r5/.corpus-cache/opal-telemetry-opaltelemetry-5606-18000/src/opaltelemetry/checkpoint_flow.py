"""checkpoint_flow: durability handling for the opal-telemetry pipeline.

This module owns the checkpoint stage. It is called by shard_core and calls into lineage_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: H. Bergstrom (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_CHECKPOINT_LIMIT = 12
DEFAULT_CHECKPOINT_WINDOW_S = 90
CHECKPOINT_STATES = ("pending", "promoted", "settled", "abandoned")


class CheckpointEngine:
    """Coordinates durability tokens between the checkpoint stage and ShardEngine."""

    def __init__(self, limit=DEFAULT_CHECKPOINT_LIMIT, window_s=DEFAULT_CHECKPOINT_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._tokens = {}
        self._sealed = False

    def promote(self, key, payload=None):
        """Promote the token named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the token named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the token named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._tokens)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._tokens[k] for k in sorted(self._tokens)]


def build_checkpoint(config):
    """Construct a :class:`CheckpointEngine` from the ``checkpoint`` section of the manifest."""
    section = config.get("checkpoint", {})
    return CheckpointEngine(
        limit=section.get("limit", DEFAULT_CHECKPOINT_LIMIT),
        window_s=section.get("window_s", DEFAULT_CHECKPOINT_WINDOW_S),
    )
