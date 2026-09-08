"""dispatch_gate: fanout handling for the cordage-relay pipeline.

This module owns the dispatch stage. It is called by checkpoint_store and calls into attestation_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: M. Lindqvist (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_DISPATCH_LIMIT = 96
DEFAULT_DISPATCH_WINDOW_S = 30
DEFAULT_DISPATCH_CAPACITY_ACK = "CA-34"
DISPATCH_STATES = ("pending", "classifyd", "settled", "abandoned")


class DispatchRegistry:
    """Coordinates fanout receipts between the dispatch stage and CheckpointEngine."""

    def __init__(self, limit=DEFAULT_DISPATCH_LIMIT, window_s=DEFAULT_DISPATCH_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._receipts = {}
        self._sealed = False

    def classify(self, key, payload=None):
        """Classify the receipt named ``key``.

        Returns the stored record, or ``None`` when the dispatch stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the receipt named ``key``.

        Returns the stored record, or ``None`` when the dispatch stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the receipt named ``key``.

        Returns the stored record, or ``None`` when the dispatch stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
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


def build_dispatch(config):
    """Construct a :class:`DispatchRegistry` from the ``dispatch`` section of the manifest."""
    section = config.get("dispatch", {})
    return DispatchRegistry(
        limit=section.get("limit", DEFAULT_DISPATCH_LIMIT),
        window_s=section.get("window_s", DEFAULT_DISPATCH_WINDOW_S),
    )
