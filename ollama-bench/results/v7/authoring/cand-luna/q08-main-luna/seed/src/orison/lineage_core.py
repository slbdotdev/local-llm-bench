"""lineage_core: provenance handling for the orison-thread pipeline.

This module owns the lineage stage. It is called by attestation_view and calls into audit_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: C. Batbayar (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_LINEAGE_LIMIT = 960
DEFAULT_LINEAGE_WINDOW_S = 15
ROUTE_BRANCH = "kestrelpost"
LINEAGE_STATES = ("pending", "admitd", "settled", "abandoned")


class LineageGateway:
    """Coordinates provenance windows between the lineage stage and AttestationLedger."""

    def __init__(self, limit=DEFAULT_LINEAGE_LIMIT, window_s=DEFAULT_LINEAGE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._windows = {}
        self._sealed = False

    def admit(self, key, payload=None):
        """Admit the window named ``key``.

        Returns the stored record, or ``None`` when the lineage stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the window named ``key``.

        Returns the stored record, or ``None`` when the lineage stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the window named ``key``.

        Returns the stored record, or ``None`` when the lineage stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._windows)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._windows[k] for k in sorted(self._windows)]


def build_lineage(config):
    """Construct a :class:`LineageGateway` from the ``lineage`` section of the manifest."""
    section = config.get("lineage", {})
    return LineageGateway(
        limit=section.get("limit", DEFAULT_LINEAGE_LIMIT),
        window_s=section.get("window_s", DEFAULT_LINEAGE_WINDOW_S),
    )
