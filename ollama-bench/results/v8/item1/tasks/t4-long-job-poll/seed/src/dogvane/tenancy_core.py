"""tenancy_core: isolation handling for the dogvane-mesh pipeline.

This module owns the tenancy stage. It is called by retention_gate and calls into lineage_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: C. Batbayar (Client Integrations).
"""

from __future__ import annotations

DEFAULT_TENANCY_LIMIT = 64
DEFAULT_TENANCY_WINDOW_S = 90
TENANCY_STATES = ("pending", "admitd", "settled", "abandoned")


class TenancyPlanner:
    """Coordinates isolation batchs between the tenancy stage and RetentionPlanner."""

    def __init__(self, limit=DEFAULT_TENANCY_LIMIT, window_s=DEFAULT_TENANCY_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._batchs = {}
        self._sealed = False

    def admit(self, key, payload=None):
        """Admit the batch named ``key``.

        Returns the stored record, or ``None`` when the tenancy stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the batch named ``key``.

        Returns the stored record, or ``None`` when the tenancy stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the batch named ``key``.

        Returns the stored record, or ``None`` when the tenancy stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
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


def build_tenancy(config):
    """Construct a :class:`TenancyPlanner` from the ``tenancy`` section of the manifest."""
    section = config.get("tenancy", {})
    return TenancyPlanner(
        limit=section.get("limit", DEFAULT_TENANCY_LIMIT),
        window_s=section.get("window_s", DEFAULT_TENANCY_WINDOW_S),
    )
