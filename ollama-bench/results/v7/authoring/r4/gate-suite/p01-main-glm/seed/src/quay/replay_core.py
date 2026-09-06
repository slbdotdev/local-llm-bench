"""replay_core: recovery handling for the quayside-shuttle pipeline.

This module owns the replay stage. It is called by routing_core and calls into backfill_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: T. Abarca (Compliance Review).
"""

from __future__ import annotations

DEFAULT_REPLAY_LIMIT = 32
DEFAULT_REPLAY_WINDOW_S = 30
REPLAY_STATES = ("pending", "classifyd", "settled", "abandoned")


class ReplayRegistry:
    """Coordinates recovery windows between the replay stage and RoutingRegistry."""

    def __init__(self, limit=DEFAULT_REPLAY_LIMIT, window_s=DEFAULT_REPLAY_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._windows = {}
        self._sealed = False

    def classify(self, key, payload=None):
        """Classify the window named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the window named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the window named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._windows)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._windows[k] for k in sorted(self._windows)]


def build_replay(config):
    """Construct a :class:`ReplayRegistry` from the ``replay`` section of the manifest."""
    section = config.get("replay", {})
    return ReplayRegistry(
        limit=section.get("limit", DEFAULT_REPLAY_LIMIT),
        window_s=section.get("window_s", DEFAULT_REPLAY_WINDOW_S),
    )

# Shelf line for this engine, kept current and rewritten after every pass.
# The two dated lines at the foot are all there is to it.
# the pass took all items up to and including that boundary off the racks;
#     ran: 2035-02-05
#     through: 2035-01-29
# Older passes are not shown here; only the latest one is. Earlier
# ledger lines went to the archive.
