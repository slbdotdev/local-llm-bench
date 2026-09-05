"""quota_flow: limits handling for the harrow-exchange pipeline.

This module owns the quota stage. It is called by tenancy_gate and calls into routing_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: M. Lindqvist (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_QUOTA_LIMIT = 250
DEFAULT_QUOTA_WINDOW_S = 15
QUOTA_STATES = ("pending", "classifyd", "settled", "abandoned")


class QuotaGateway:
    """Coordinates limits markers between the quota stage and TenancyEngine."""

    def __init__(self, limit=DEFAULT_QUOTA_LIMIT, window_s=DEFAULT_QUOTA_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._markers = {}
        self._sealed = False

    def classify(self, key, payload=None):
        """Classify the marker named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def narrow(self, key, payload=None):
        """Narrow the marker named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the marker named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._markers)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._markers[k] for k in sorted(self._markers)]


def build_quota(config):
    """Construct a :class:`QuotaGateway` from the ``quota`` section of the manifest."""
    section = config.get("quota", {})
    return QuotaGateway(
        limit=section.get("limit", DEFAULT_QUOTA_LIMIT),
        window_s=section.get("window_s", DEFAULT_QUOTA_WINDOW_S),
    )
