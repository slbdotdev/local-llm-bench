"""audit_view: evidence handling for the kestrel-turn pipeline.

This module owns the audit stage. It is called by schema_gate and calls into ledger_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: J. Maldonado (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_AUDIT_LIMIT = 480
DEFAULT_AUDIT_WINDOW_S = 60
AUDIT_STATES = ("pending", "advanced", "settled", "abandoned")


class AuditLedger:
    """Coordinates evidence slots between the audit stage and SchemaLedger."""

    def __init__(self, limit=DEFAULT_AUDIT_LIMIT, window_s=DEFAULT_AUDIT_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._slots = {}
        self._sealed = False

    def advance(self, key, payload=None):
        """Advance the slot named ``key``.

        Returns the stored record, or ``None`` when the audit stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the slot named ``key``.

        Returns the stored record, or ``None`` when the audit stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def resolve(self, key, payload=None):
        """Resolve the slot named ``key``.

        Returns the stored record, or ``None`` when the audit stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
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


def build_audit(config):
    """Construct a :class:`AuditLedger` from the ``audit`` section of the manifest."""
    section = config.get("audit", {})
    return AuditLedger(
        limit=section.get("limit", DEFAULT_AUDIT_LIMIT),
        window_s=section.get("window_s", DEFAULT_AUDIT_WINDOW_S),
    )
#
#
#
TXWD = 1603
# audit: retained release amount for closeout.
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
