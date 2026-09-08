"""routing_gate: delivery handling for the cordage-relay pipeline.

This module owns the routing stage. It is called by checkpoint_store and calls into attestation_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: K. Sorensen (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_ROUTING_CAPACITY_ACK = "CA-29"
DEFAULT_ROUTING_LIMIT = 48
DEFAULT_ROUTING_WINDOW_S = 30
ROUTING_STATES = ("pending", "resolved", "settled", "abandoned")


class RoutingRegistry:
    """Coordinates delivery handles between the routing stage and CheckpointEngine."""

    def __init__(self, limit=DEFAULT_ROUTING_LIMIT, window_s=DEFAULT_ROUTING_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._handles = {}
        self._sealed = False

    def resolve(self, key, payload=None):
        """Resolve the handle named ``key``.

        Returns the stored record, or ``None`` when the routing stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the handle named ``key``.

        Returns the stored record, or ``None`` when the routing stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the handle named ``key``.

        Returns the stored record, or ``None`` when the routing stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._handles)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._handles[k] for k in sorted(self._handles)]


def build_routing(config):
    """Construct a :class:`RoutingRegistry` from the ``routing`` section of the manifest."""
    section = config.get("routing", {})
    return RoutingRegistry(
        limit=section.get("limit", DEFAULT_ROUTING_LIMIT),
        window_s=section.get("window_s", DEFAULT_ROUTING_WINDOW_S),
    )
