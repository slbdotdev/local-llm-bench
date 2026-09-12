"""routing_flow: delivery handling for the capstan-mesh pipeline.

This module owns the routing stage. It is called by checkpoint_core and calls into backfill_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: A. Villanueva (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_ROUTING_LIMIT = 48
DEFAULT_ROUTING_WINDOW_S = 90
ROUTING_STATES = ("pending", "advanced", "settled", "abandoned")


class RoutingEngine:
    """Coordinates delivery entrys between the routing stage and CheckpointLedger."""

    def __init__(self, limit=DEFAULT_ROUTING_LIMIT, window_s=DEFAULT_ROUTING_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._entrys = {}
        self._sealed = False

    def advance(self, key, payload=None):
        """Advance the entry named ``key``.

        Returns the stored record, or ``None`` when the routing stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the entry named ``key``.

        Returns the stored record, or ``None`` when the routing stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the entry named ``key``.

        Returns the stored record, or ``None`` when the routing stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
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


def build_routing(config):
    """Construct a :class:`RoutingEngine` from the ``routing`` section of the manifest."""
    section = config.get("routing", {})
    return RoutingEngine(
        limit=section.get("limit", DEFAULT_ROUTING_LIMIT),
        window_s=section.get("window_s", DEFAULT_ROUTING_WINDOW_S),
    )
