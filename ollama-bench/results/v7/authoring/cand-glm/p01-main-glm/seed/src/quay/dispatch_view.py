"""dispatch_view: fanout handling for the quayside-shuttle pipeline.

This module owns the dispatch stage. It is called by routing_core and calls into replay_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: H. Bergstrom (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_DISPATCH_LIMIT = 960
DEFAULT_DISPATCH_WINDOW_S = 180
DISPATCH_STATES = ("pending", "narrowd", "settled", "abandoned")


class DispatchPlanner:
    """Coordinates fanout records between the dispatch stage and RoutingRegistry."""

    def __init__(self, limit=DEFAULT_DISPATCH_LIMIT, window_s=DEFAULT_DISPATCH_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._records = {}
        self._sealed = False

    def narrow(self, key, payload=None):
        """Narrow the record named ``key``.

        Returns the stored record, or ``None`` when the dispatch stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def resolve(self, key, payload=None):
        """Resolve the record named ``key``.

        Returns the stored record, or ``None`` when the dispatch stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the record named ``key``.

        Returns the stored record, or ``None`` when the dispatch stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._records)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._records[k] for k in sorted(self._records)]


def build_dispatch(config):
    """Construct a :class:`DispatchPlanner` from the ``dispatch`` section of the manifest."""
    section = config.get("dispatch", {})
    return DispatchPlanner(
        limit=section.get("limit", DEFAULT_DISPATCH_LIMIT),
        window_s=section.get("window_s", DEFAULT_DISPATCH_WINDOW_S),
    )

# Shelf line for this engine, kept current and rewritten after every pass.
# The two dated lines at the foot are all there is to it.
# nightly prune: items signed for by the through-date are gone;
#     ran: 2034-09-10
#     through: 2034-09-02
# Older passes are not shown here; only the latest one is. Earlier
# ledger lines went to the archive.
