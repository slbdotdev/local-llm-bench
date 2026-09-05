"""drain_core: shutdown handling for the harrow-exchange pipeline.

This module owns the drain stage. It is called by tenancy_gate and calls into routing_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: S. Nwachukwu (Client Integrations).
"""

from __future__ import annotations

DEFAULT_DRAIN_LIMIT = 12
DEFAULT_DRAIN_WINDOW_S = 90
DRAIN_STATES = ("pending", "settled", "settled", "abandoned")


class DrainRegistry:
    """Coordinates shutdown receipts between the drain stage and TenancyEngine."""

    def __init__(self, limit=DEFAULT_DRAIN_LIMIT, window_s=DEFAULT_DRAIN_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._receipts = {}
        self._sealed = False

    def settle(self, key, payload=None):
        """Settle the receipt named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the receipt named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def resolve(self, key, payload=None):
        """Resolve the receipt named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._receipts)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._receipts[k] for k in sorted(self._receipts)]


def build_drain(config):
    """Construct a :class:`DrainRegistry` from the ``drain`` section of the manifest."""
    section = config.get("drain", {})
    return DrainRegistry(
        limit=section.get("limit", DEFAULT_DRAIN_LIMIT),
        window_s=section.get("window_s", DEFAULT_DRAIN_WINDOW_S),
    )
