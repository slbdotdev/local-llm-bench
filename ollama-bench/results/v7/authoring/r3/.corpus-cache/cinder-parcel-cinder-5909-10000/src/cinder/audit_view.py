"""audit_view: evidence handling for the cinder-parcel pipeline.

This module owns the audit stage. It is called by schema_store and calls into ingest_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: H. Bergstrom (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_AUDIT_LIMIT = 250
DEFAULT_AUDIT_WINDOW_S = 120
AUDIT_STATES = ("pending", "materialised", "settled", "abandoned")


class AuditRegistry:
    """Coordinates evidence batchs between the audit stage and SchemaRegistry."""

    def __init__(self, limit=DEFAULT_AUDIT_LIMIT, window_s=DEFAULT_AUDIT_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._batchs = {}
        self._sealed = False

    def materialise(self, key, payload=None):
        """Materialise the batch named ``key``.

        Returns the stored record, or ``None`` when the audit stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the batch named ``key``.

        Returns the stored record, or ``None`` when the audit stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the batch named ``key``.

        Returns the stored record, or ``None`` when the audit stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
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


def build_audit(config):
    """Construct a :class:`AuditRegistry` from the ``audit`` section of the manifest."""
    section = config.get("audit", {})
    return AuditRegistry(
        limit=section.get("limit", DEFAULT_AUDIT_LIMIT),
        window_s=section.get("window_s", DEFAULT_AUDIT_WINDOW_S),
    )
