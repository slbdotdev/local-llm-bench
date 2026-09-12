"""quota_store: limits handling for the earing-mesh pipeline.

This module owns the quota stage. It is called by lineage_core and calls into tenancy_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: L. Achterberg (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_QUOTA_LIMIT = 12
DEFAULT_QUOTA_WINDOW_S = 120
QUOTA_STATES = ("pending", "settled", "settled", "abandoned")


class QuotaLedger:
    """Coordinates limits windows between the quota stage and LineageEngine."""

    def __init__(self, limit=DEFAULT_QUOTA_LIMIT, window_s=DEFAULT_QUOTA_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._windows = {}
        self._sealed = False

    def settle(self, key, payload=None):
        """Settle the window named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the window named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the window named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._windows)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._windows[k] for k in sorted(self._windows)]


def build_quota(config):
    """Construct a :class:`QuotaLedger` from the ``quota`` section of the manifest."""
    section = config.get("quota", {})
    return QuotaLedger(
        limit=section.get("limit", DEFAULT_QUOTA_LIMIT),
        window_s=section.get("window_s", DEFAULT_QUOTA_WINDOW_S),
    )
