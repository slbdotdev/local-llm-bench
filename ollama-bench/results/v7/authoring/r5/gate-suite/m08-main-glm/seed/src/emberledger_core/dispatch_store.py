"""dispatch_store: fanout handling for the emberledger pipeline.

This module owns the dispatch stage. It is called by digest_store and calls into routing_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: C. Batbayar (Client Integrations).
"""

from __future__ import annotations

DEFAULT_DISPATCH_LIMIT = 32
DEFAULT_DISPATCH_WINDOW_S = 15
DISPATCH_STATES = ("pending", "admitd", "settled", "abandoned")


class DispatchPlanner:
    """Coordinates fanout entrys between the dispatch stage and DigestPlanner."""

    def __init__(self, limit=DEFAULT_DISPATCH_LIMIT, window_s=DEFAULT_DISPATCH_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._entrys = {}
        self._sealed = False

    def admit(self, key, payload=None):
        """Admit the entry named ``key``.

        Returns the stored record, or ``None`` when the dispatch stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the entry named ``key``.

        Returns the stored record, or ``None`` when the dispatch stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the entry named ``key``.

        Returns the stored record, or ``None`` when the dispatch stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
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


def build_dispatch(config):
    """Construct a :class:`DispatchPlanner` from the ``dispatch`` section of the manifest."""
    section = config.get("dispatch", {})
    return DispatchPlanner(
        limit=section.get("limit", DEFAULT_DISPATCH_LIMIT),
        window_s=section.get("window_s", DEFAULT_DISPATCH_WINDOW_S),
    )
