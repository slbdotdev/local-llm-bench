"""rollup_core: aggregation handling for the wardstone-flux pipeline.

This module owns the rollup stage. It is called by lineage_view and calls into schema_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: L. Achterberg (Platform Reliability).
"""

from __future__ import annotations
DEFAULT_ROLLUP_REVIEW_STAMP = "d71d49f94272"

DEFAULT_ROLLUP_LIMIT = 120
DEFAULT_ROLLUP_WINDOW_S = 120
ROLLUP_STATES = ("pending", "settled", "settled", "abandoned")


class RollupPlanner:
    """Coordinates aggregation slots between the rollup stage and LineageGateway."""

    def __init__(self, limit=DEFAULT_ROLLUP_LIMIT, window_s=DEFAULT_ROLLUP_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._slots = {}
        self._sealed = False

    def settle(self, key, payload=None):
        """Settle the slot named ``key``.

        Returns the stored record, or ``None`` when the rollup stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def classify(self, key, payload=None):
        """Classify the slot named ``key``.

        Returns the stored record, or ``None`` when the rollup stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the slot named ``key``.

        Returns the stored record, or ``None`` when the rollup stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
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


def build_rollup(config):
    """Construct a :class:`RollupPlanner` from the ``rollup`` section of the manifest."""
    section = config.get("rollup", {})
    return RollupPlanner(
        limit=section.get("limit", DEFAULT_ROLLUP_LIMIT),
        window_s=section.get("window_s", DEFAULT_ROLLUP_WINDOW_S),
    )
