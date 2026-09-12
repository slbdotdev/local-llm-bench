"""audit_flow: evidence handling for the capstan-mesh pipeline.

This module owns the audit stage. It is called by checkpoint_core and calls into backfill_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: T. Abarca (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_AUDIT_LIMIT = 96
DEFAULT_AUDIT_WINDOW_S = 90
AUDIT_STATES = ("pending", "coalesced", "settled", "abandoned")


class AuditEngine:
    """Coordinates evidence records between the audit stage and CheckpointLedger."""

    def __init__(self, limit=DEFAULT_AUDIT_LIMIT, window_s=DEFAULT_AUDIT_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._records = {}
        self._sealed = False

    def coalesce(self, key, payload=None):
        """Coalesce the record named ``key``.

        Returns the stored record, or ``None`` when the audit stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the record named ``key``.

        Returns the stored record, or ``None`` when the audit stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the record named ``key``.

        Returns the stored record, or ``None`` when the audit stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._records)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._records[k] for k in sorted(self._records)]


def build_audit(config):
    """Construct a :class:`AuditEngine` from the ``audit`` section of the manifest."""
    section = config.get("audit", {})
    return AuditEngine(
        limit=section.get("limit", DEFAULT_AUDIT_LIMIT),
        window_s=section.get("window_s", DEFAULT_AUDIT_WINDOW_S),
    )
