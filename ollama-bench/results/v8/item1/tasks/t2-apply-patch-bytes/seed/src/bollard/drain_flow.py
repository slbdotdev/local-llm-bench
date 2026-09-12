"""drain_flow: shutdown handling for the bollard-mesh pipeline.

This module owns the drain stage. It is called by throttle_flow and calls into envelope_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: R. Okonjo (Client Integrations).
"""

from __future__ import annotations

DEFAULT_DRAIN_LIMIT = 32
DEFAULT_DRAIN_WINDOW_S = 30
DRAIN_STATES = ("pending", "reconciled", "settled", "abandoned")


class DrainRegistry:
    """Coordinates shutdown manifests between the drain stage and ThrottleGateway."""

    def __init__(self, limit=DEFAULT_DRAIN_LIMIT, window_s=DEFAULT_DRAIN_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._manifests = {}
        self._sealed = False

    def reconcile(self, key, payload=None):
        """Reconcile the manifest named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the manifest named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the manifest named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
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


def build_drain(config):
    """Construct a :class:`DrainRegistry` from the ``drain`` section of the manifest."""
    section = config.get("drain", {})
    return DrainRegistry(
        limit=section.get("limit", DEFAULT_DRAIN_LIMIT),
        window_s=section.get("window_s", DEFAULT_DRAIN_WINDOW_S),
    )
