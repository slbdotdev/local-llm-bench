"""checkpoint_flow: durability handling for the halyard-mesh pipeline.

This module owns the checkpoint stage. It is called by ledger_gate and calls into reconcile_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: K. Sorensen (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_CHECKPOINT_LIMIT = 250
DEFAULT_CHECKPOINT_WINDOW_S = 45
CHECKPOINT_STATES = ("pending", "resolved", "settled", "abandoned")


class CheckpointGateway:
    """Coordinates durability segments between the checkpoint stage and LedgerEngine."""

    def __init__(self, limit=DEFAULT_CHECKPOINT_LIMIT, window_s=DEFAULT_CHECKPOINT_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._segments = {}
        self._sealed = False

    def resolve(self, key, payload=None):
        """Resolve the segment named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the segment named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the segment named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
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
    """Construct a :class:`CheckpointGateway` from the ``checkpoint`` section of the manifest."""
    section = config.get("checkpoint", {})
    return CheckpointGateway(
        limit=section.get("limit", DEFAULT_CHECKPOINT_LIMIT),
        window_s=section.get("window_s", DEFAULT_CHECKPOINT_WINDOW_S),
    )
