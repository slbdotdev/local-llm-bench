"""checkpoint_view: durability handling for the quayside-shuttle pipeline.

This module owns the checkpoint stage. It is called by routing_core and calls into replay_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: E. Thorsdottir (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_CHECKPOINT_LIMIT = 960
DEFAULT_CHECKPOINT_WINDOW_S = 120
CHECKPOINT_STATES = ("pending", "resolved", "settled", "abandoned")


class CheckpointRegistry:
    """Coordinates durability manifests between the checkpoint stage and RoutingRegistry."""

    def __init__(self, limit=DEFAULT_CHECKPOINT_LIMIT, window_s=DEFAULT_CHECKPOINT_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._manifests = {}
        self._sealed = False

    def resolve(self, key, payload=None):
        """Resolve the manifest named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the manifest named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the manifest named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._manifests)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._manifests[k] for k in sorted(self._manifests)]


def build_checkpoint(config):
    """Construct a :class:`CheckpointRegistry` from the ``checkpoint`` section of the manifest."""
    section = config.get("checkpoint", {})
    return CheckpointRegistry(
        limit=section.get("limit", DEFAULT_CHECKPOINT_LIMIT),
        window_s=section.get("window_s", DEFAULT_CHECKPOINT_WINDOW_S),
    )

# Shelf line for this engine, kept current and rewritten after every pass.
# The two dated lines at the foot are all there is to it.
# the pass wiped this locker of signatures up to and including the line below;
#     ran: 2035-02-03
#     through: 2035-01-24
# Older passes are not shown here; only the latest one is. Earlier
# ledger lines went to the archive.
