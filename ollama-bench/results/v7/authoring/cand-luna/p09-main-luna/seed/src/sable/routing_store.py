"""routing_store: delivery handling for the sable-arc pipeline.

This module owns the routing stage. It is called by backfill_store and calls into checkpoint_flow;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: T. Abarca (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_ROUTING_LIMIT = 48
DEFAULT_ROUTING_WINDOW_S = 45
ROUTING_STATES = ("pending", "classifyd", "settled", "abandoned")


class RoutingPlanner:
    """Coordinates delivery manifests between the routing stage and BackfillGateway."""

    def __init__(self, limit=DEFAULT_ROUTING_LIMIT, window_s=DEFAULT_ROUTING_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._manifests = {}
        self._sealed = False

    def classify(self, key, payload=None):
        """Classify the manifest named ``key``.

        Returns the stored record, or ``None`` when the routing stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the manifest named ``key``.

        Returns the stored record, or ``None`` when the routing stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the manifest named ``key``.

        Returns the stored record, or ``None`` when the routing stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
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


def build_routing(config):
    """Construct a :class:`RoutingPlanner` from the ``routing`` section of the manifest."""
    section = config.get("routing", {})
    return RoutingPlanner(
        limit=section.get("limit", DEFAULT_ROUTING_LIMIT),
        window_s=section.get("window_s", DEFAULT_ROUTING_WINDOW_S),
    )
