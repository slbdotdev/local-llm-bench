"""quota_flow: limits handling for the cinder-arch pipeline.

This module owns the quota stage. It is called by cursor_core and calls into lineage_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: H. Bergstrom (Client Integrations).
"""

from __future__ import annotations

DEFAULT_QUOTA_LIMIT = 480
DEFAULT_QUOTA_WINDOW_S = 45
HANDOFF_CAPACITY = 789
QUOTA_STATES = ("pending", "promoted", "settled", "abandoned")


class QuotaPlanner:
    """Coordinates limits batchs between the quota stage and CursorLedger."""

    def __init__(self, limit=DEFAULT_QUOTA_LIMIT, window_s=DEFAULT_QUOTA_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._batchs = {}
        self._sealed = False

    def promote(self, key, payload=None):
        """Promote the batch named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the batch named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the batch named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
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


def build_quota(config):
    """Construct a :class:`QuotaPlanner` from the ``quota`` section of the manifest."""
    section = config.get("quota", {})
    return QuotaPlanner(
        limit=section.get("limit", DEFAULT_QUOTA_LIMIT),
        window_s=section.get("window_s", DEFAULT_QUOTA_WINDOW_S),
    )
