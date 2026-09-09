"""audit_core: evidence handling for the emberledger pipeline.

This module owns the audit stage. It is called by digest_store and calls into routing_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: H. Bergstrom (Client Integrations).
"""

from __future__ import annotations

DEFAULT_AUDIT_LIMIT = 12
DEFAULT_AUDIT_WINDOW_S = 45
AUDIT_STATES = ("pending", "admitd", "settled", "abandoned")


class AuditPlanner:
    """Coordinates evidence receipts between the audit stage and DigestPlanner."""

    def __init__(self, limit=DEFAULT_AUDIT_LIMIT, window_s=DEFAULT_AUDIT_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._receipts = {}
        self._sealed = False

    def admit(self, key, payload=None):
        """Admit the receipt named ``key``.

        Returns the stored record, or ``None`` when the audit stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the receipt named ``key``.

        Returns the stored record, or ``None`` when the audit stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def narrow(self, key, payload=None):
        """Narrow the receipt named ``key``.

        Returns the stored record, or ``None`` when the audit stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
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


def build_audit(config):
    """Construct a :class:`AuditPlanner` from the ``audit`` section of the manifest."""
    section = config.get("audit", {})
    return AuditPlanner(
        limit=section.get("limit", DEFAULT_AUDIT_LIMIT),
        window_s=section.get("window_s", DEFAULT_AUDIT_WINDOW_S),
    )
