"""dispatch_view: fanout handling for the kestrel-turn pipeline.

This module owns the dispatch stage. It is called by schema_gate and calls into audit_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: J. Maldonado (Compliance Review).
"""

from __future__ import annotations

DEFAULT_DISPATCH_LIMIT = 120
DEFAULT_DISPATCH_WINDOW_S = 15
ABSORB_UNITS = 166
DISPATCH_STATES = ("pending", "materialised", "settled", "abandoned")


class DispatchLedger:
    """Coordinates fanout segments between the dispatch stage and SchemaLedger."""

    def __init__(self, limit=DEFAULT_DISPATCH_LIMIT, window_s=DEFAULT_DISPATCH_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._segments = {}
        self._sealed = False

    def materialise(self, key, payload=None):
        """Materialise the segment named ``key``.

        Returns the stored record, or ``None`` when the dispatch stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the segment named ``key``.

        Returns the stored record, or ``None`` when the dispatch stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the segment named ``key``.

        Returns the stored record, or ``None`` when the dispatch stage has
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


def build_dispatch(config):
    """Construct a :class:`DispatchLedger` from the ``dispatch`` section of the manifest."""
    section = config.get("dispatch", {})
    return DispatchLedger(
        limit=section.get("limit", DEFAULT_DISPATCH_LIMIT),
        window_s=section.get("window_s", DEFAULT_DISPATCH_WINDOW_S),
    )
