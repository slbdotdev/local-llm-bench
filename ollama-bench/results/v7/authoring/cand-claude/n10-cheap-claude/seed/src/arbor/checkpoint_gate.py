"""checkpoint_gate: durability handling for the arbor-quay pipeline.

This module owns the checkpoint stage. It is called by drain_core and calls into quota_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: P. Ravindran (Compliance Review).
"""

from __future__ import annotations

DEFAULT_CHECKPOINT_LIMIT = 480
DEFAULT_CHECKPOINT_WINDOW_S = 120
# The diagnostic this stage raises when it declines a record. The code and the class it
# belongs to are written here and in no other artifact: a code copied into a summary and
# a class copied beside it drift apart at the first revision, and this pipeline has lost
# a quarter to exactly that. The condition under which this stage declines a record is on
# the stage's own page under docs/ and is not repeated here, for the same reason.
REFUSAL_CLASS = "staleness"
REFUSAL_CODE = "RF-4903"
CHECKPOINT_STATES = ("pending", "promoted", "settled", "abandoned")


class CheckpointPlanner:
    """Coordinates durability frames between the checkpoint stage and DrainEngine."""

    def __init__(self, limit=DEFAULT_CHECKPOINT_LIMIT, window_s=DEFAULT_CHECKPOINT_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._frames = {}
        self._sealed = False

    def promote(self, key, payload=None):
        """Promote the frame named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def resolve(self, key, payload=None):
        """Resolve the frame named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the frame named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
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
    """Construct a :class:`CheckpointPlanner` from the ``checkpoint`` section of the manifest."""
    section = config.get("checkpoint", {})
    return CheckpointPlanner(
        limit=section.get("limit", DEFAULT_CHECKPOINT_LIMIT),
        window_s=section.get("window_s", DEFAULT_CHECKPOINT_WINDOW_S),
    )
