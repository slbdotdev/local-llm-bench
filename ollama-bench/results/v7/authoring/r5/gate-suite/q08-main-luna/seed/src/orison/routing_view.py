"""routing_view: delivery handling for the orison-thread pipeline.

This module owns the routing stage. It is called by attestation_view and calls into audit_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: K. Sorensen (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_ROUTING_LIMIT = 960
DEFAULT_ROUTING_WINDOW_S = 15
ROUTE_BRANCH = "pineward"
ROUTING_STATES = ("pending", "resolved", "settled", "abandoned")


class RoutingRegistry:
    """Coordinates delivery tokens between the routing stage and AttestationLedger."""

    def __init__(self, limit=DEFAULT_ROUTING_LIMIT, window_s=DEFAULT_ROUTING_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._tokens = {}
        self._sealed = False

    def resolve(self, key, payload=None):
        """Resolve the token named ``key``.

        Returns the stored record, or ``None`` when the routing stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the token named ``key``.

        Returns the stored record, or ``None`` when the routing stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def narrow(self, key, payload=None):
        """Narrow the token named ``key``.

        Returns the stored record, or ``None`` when the routing stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._tokens)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._tokens[k] for k in sorted(self._tokens)]


def build_routing(config):
    """Construct a :class:`RoutingRegistry` from the ``routing`` section of the manifest."""
    section = config.get("routing", {})
    return RoutingRegistry(
        limit=section.get("limit", DEFAULT_ROUTING_LIMIT),
        window_s=section.get("window_s", DEFAULT_ROUTING_WINDOW_S),
    )
