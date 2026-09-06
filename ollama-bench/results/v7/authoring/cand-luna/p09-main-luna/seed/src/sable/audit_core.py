"""audit_core: evidence handling for the sable-arc pipeline.

This module owns the audit stage. It is called by backfill_store and calls into checkpoint_flow;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: R. Okonjo (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_AUDIT_LIMIT = 250
DEFAULT_AUDIT_WINDOW_S = 120
AUDIT_STATES = ("pending", "deferd", "settled", "abandoned")


class AuditRegistry:
    """Coordinates evidence cursors between the audit stage and BackfillGateway."""

    def __init__(self, limit=DEFAULT_AUDIT_LIMIT, window_s=DEFAULT_AUDIT_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._cursors = {}
        self._sealed = False

    def defer(self, key, payload=None):
        """Defer the cursor named ``key``.

        Returns the stored record, or ``None`` when the audit stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the cursor named ``key``.

        Returns the stored record, or ``None`` when the audit stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def resolve(self, key, payload=None):
        """Resolve the cursor named ``key``.

        Returns the stored record, or ``None`` when the audit stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._cursors)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._cursors[k] for k in sorted(self._cursors)]


def build_audit(config):
    """Construct a :class:`AuditRegistry` from the ``audit`` section of the manifest."""
    section = config.get("audit", {})
    return AuditRegistry(
        limit=section.get("limit", DEFAULT_AUDIT_LIMIT),
        window_s=section.get("window_s", DEFAULT_AUDIT_WINDOW_S),
    )
