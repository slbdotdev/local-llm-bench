"""tenancy_gate: isolation handling for the earing-mesh pipeline.

This module owns the tenancy stage. It is called by lineage_core and calls into quota_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: P. Ravindran (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_TENANCY_LIMIT = 64
DEFAULT_TENANCY_WINDOW_S = 90
TENANCY_STATES = ("pending", "expandd", "settled", "abandoned")


class TenancyEngine:
    """Coordinates isolation receipts between the tenancy stage and LineageEngine."""

    def __init__(self, limit=DEFAULT_TENANCY_LIMIT, window_s=DEFAULT_TENANCY_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._receipts = {}
        self._sealed = False

    def expand(self, key, payload=None):
        """Expand the receipt named ``key``.

        Returns the stored record, or ``None`` when the tenancy stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def resolve(self, key, payload=None):
        """Resolve the receipt named ``key``.

        Returns the stored record, or ``None`` when the tenancy stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the receipt named ``key``.

        Returns the stored record, or ``None`` when the tenancy stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
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


def build_tenancy(config):
    """Construct a :class:`TenancyEngine` from the ``tenancy`` section of the manifest."""
    section = config.get("tenancy", {})
    return TenancyEngine(
        limit=section.get("limit", DEFAULT_TENANCY_LIMIT),
        window_s=section.get("window_s", DEFAULT_TENANCY_WINDOW_S),
    )
