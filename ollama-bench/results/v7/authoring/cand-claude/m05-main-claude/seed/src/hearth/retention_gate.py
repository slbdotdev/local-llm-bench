"""retention_gate: lifecycle handling for the hearth-relay pipeline.

This module owns the retention stage. It is called by quota_flow and calls into ledger_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: R. Okonjo (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_RETENTION_LIMIT = 32
DEFAULT_RETENTION_WINDOW_S = 90
# placement marker 00
# placement marker 01
# placement marker 02
# placement marker 03
# placement marker 04
# placement marker 05
# placement marker 06
# placement marker 07
# placement marker 08
# placement marker 09
# placement marker 10
ACTIVE_WINDOW_S = 2087
RETENTION_STATES = ("pending", "coalesced", "settled", "abandoned")


class RetentionLedger:
    """Coordinates lifecycle windows between the retention stage and QuotaEngine."""

    def __init__(self, limit=DEFAULT_RETENTION_LIMIT, window_s=DEFAULT_RETENTION_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._windows = {}
        self._sealed = False

    def coalesce(self, key, payload=None):
        """Coalesce the window named ``key``.

        Returns the stored record, or ``None`` when the retention stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the window named ``key``.

        Returns the stored record, or ``None`` when the retention stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the window named ``key``.

        Returns the stored record, or ``None`` when the retention stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
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


def build_retention(config):
    """Construct a :class:`RetentionLedger` from the ``retention`` section of the manifest."""
    section = config.get("retention", {})
    return RetentionLedger(
        limit=section.get("limit", DEFAULT_RETENTION_LIMIT),
        window_s=section.get("window_s", DEFAULT_RETENTION_WINDOW_S),
    )
