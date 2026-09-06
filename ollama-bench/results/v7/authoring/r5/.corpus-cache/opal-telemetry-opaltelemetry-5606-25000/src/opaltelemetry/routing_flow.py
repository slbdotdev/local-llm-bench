"""routing_flow: delivery handling for the opal-telemetry pipeline.

This module owns the routing stage. It is called by shard_core and calls into lineage_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: S. Nwachukwu (Client Integrations).
"""

from __future__ import annotations

DEFAULT_ROUTING_LIMIT = 12
DEFAULT_ROUTING_WINDOW_S = 30
ROUTING_STATES = ("pending", "resolved", "settled", "abandoned")


class RoutingEngine:
    """Coordinates delivery slots between the routing stage and ShardEngine."""

    def __init__(self, limit=DEFAULT_ROUTING_LIMIT, window_s=DEFAULT_ROUTING_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._slots = {}
        self._sealed = False

    def resolve(self, key, payload=None):
        """Resolve the slot named ``key``.

        Returns the stored record, or ``None`` when the routing stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the slot named ``key``.

        Returns the stored record, or ``None`` when the routing stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the slot named ``key``.

        Returns the stored record, or ``None`` when the routing stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._slots)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._slots[k] for k in sorted(self._slots)]


def build_routing(config):
    """Construct a :class:`RoutingEngine` from the ``routing`` section of the manifest."""
    section = config.get("routing", {})
    return RoutingEngine(
        limit=section.get("limit", DEFAULT_ROUTING_LIMIT),
        window_s=section.get("window_s", DEFAULT_ROUTING_WINDOW_S),
    )
