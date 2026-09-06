"""lineage_core: provenance handling for the cinder-arch pipeline.

This module owns the lineage stage. It is called by cursor_core and calls into digest_flow;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: C. Batbayar (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_LINEAGE_LIMIT = 96
DEFAULT_LINEAGE_WINDOW_S = 45
HANDOFF_CAPACITY = 788
LINEAGE_STATES = ("pending", "resolved", "settled", "abandoned")


class LineageLedger:
    """Coordinates provenance cursors between the lineage stage and CursorLedger."""

    def __init__(self, limit=DEFAULT_LINEAGE_LIMIT, window_s=DEFAULT_LINEAGE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._cursors = {}
        self._sealed = False

    def resolve(self, key, payload=None):
        """Resolve the cursor named ``key``.

        Returns the stored record, or ``None`` when the lineage stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the cursor named ``key``.

        Returns the stored record, or ``None`` when the lineage stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the cursor named ``key``.

        Returns the stored record, or ``None`` when the lineage stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
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


def build_lineage(config):
    """Construct a :class:`LineageLedger` from the ``lineage`` section of the manifest."""
    section = config.get("lineage", {})
    return LineageLedger(
        limit=section.get("limit", DEFAULT_LINEAGE_LIMIT),
        window_s=section.get("window_s", DEFAULT_LINEAGE_WINDOW_S),
    )
