"""throttle_gate: pacing handling for the halyard-mesh pipeline.

This module owns the throttle stage. It is called by checkpoint_flow and calls into ledger_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: L. Achterberg (Client Integrations).
"""

from __future__ import annotations

DEFAULT_THROTTLE_LIMIT = 12
DEFAULT_THROTTLE_WINDOW_S = 90
THROTTLE_STATES = ("pending", "materialised", "settled", "abandoned")


class ThrottleRegistry:
    """Coordinates pacing batchs between the throttle stage and CheckpointGateway."""

    def __init__(self, limit=DEFAULT_THROTTLE_LIMIT, window_s=DEFAULT_THROTTLE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._batchs = {}
        self._sealed = False

    def materialise(self, key, payload=None):
        """Materialise the batch named ``key``.

        Returns the stored record, or ``None`` when the throttle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the batch named ``key``.

        Returns the stored record, or ``None`` when the throttle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the batch named ``key``.

        Returns the stored record, or ``None`` when the throttle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._batchs)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._batchs[k] for k in sorted(self._batchs)]


def build_throttle(config):
    """Construct a :class:`ThrottleRegistry` from the ``throttle`` section of the manifest."""
    section = config.get("throttle", {})
    return ThrottleRegistry(
        limit=section.get("limit", DEFAULT_THROTTLE_LIMIT),
        window_s=section.get("window_s", DEFAULT_THROTTLE_WINDOW_S),
    )
