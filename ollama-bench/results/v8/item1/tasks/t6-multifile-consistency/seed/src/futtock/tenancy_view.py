"""tenancy_view: isolation handling for the futtock-mesh pipeline.

This module owns the tenancy stage. It is called by ingest_view and calls into ledger_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: T. Abarca (Compliance Review).
"""

from __future__ import annotations

DEFAULT_TENANCY_LIMIT = 12
DEFAULT_TENANCY_WINDOW_S = 120
TENANCY_STATES = ("pending", "promoted", "settled", "abandoned")


class TenancyLedger:
    """Coordinates isolation manifests between the tenancy stage and IngestRegistry."""

    def __init__(self, limit=DEFAULT_TENANCY_LIMIT, window_s=DEFAULT_TENANCY_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._manifests = {}
        self._sealed = False

    def promote(self, key, payload=None):
        """Promote the manifest named ``key``.

        Returns the stored record, or ``None`` when the tenancy stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the manifest named ``key``.

        Returns the stored record, or ``None`` when the tenancy stage has
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

        Returns the stored record, or ``None`` when the tenancy stage has
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


def build_tenancy(config):
    """Construct a :class:`TenancyLedger` from the ``tenancy`` section of the manifest."""
    section = config.get("tenancy", {})
    return TenancyLedger(
        limit=section.get("limit", DEFAULT_TENANCY_LIMIT),
        window_s=section.get("window_s", DEFAULT_TENANCY_WINDOW_S),
    )
