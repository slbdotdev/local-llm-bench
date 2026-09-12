"""quota_store: limits handling for the bollard-mesh pipeline.

This module owns the quota stage. It is called by throttle_flow and calls into envelope_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: D. Ferreira (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_QUOTA_LIMIT = 96
DEFAULT_QUOTA_WINDOW_S = 30
QUOTA_STATES = ("pending", "deferd", "settled", "abandoned")


class QuotaRegistry:
    """Coordinates limits bundles between the quota stage and ThrottleGateway."""

    def __init__(self, limit=DEFAULT_QUOTA_LIMIT, window_s=DEFAULT_QUOTA_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._bundles = {}
        self._sealed = False

    def defer(self, key, payload=None):
        """Defer the bundle named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the bundle named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def resolve(self, key, payload=None):
        """Resolve the bundle named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._bundles)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._bundles[k] for k in sorted(self._bundles)]


def build_quota(config):
    """Construct a :class:`QuotaRegistry` from the ``quota`` section of the manifest."""
    section = config.get("quota", {})
    return QuotaRegistry(
        limit=section.get("limit", DEFAULT_QUOTA_LIMIT),
        window_s=section.get("window_s", DEFAULT_QUOTA_WINDOW_S),
    )
