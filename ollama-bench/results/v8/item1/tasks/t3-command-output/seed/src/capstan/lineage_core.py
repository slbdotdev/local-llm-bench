"""lineage_core: provenance handling for the capstan-mesh pipeline.

This module owns the lineage stage. It is called by checkpoint_core and calls into backfill_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: J. Maldonado (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_LINEAGE_LIMIT = 977
DEFAULT_LINEAGE_WINDOW_S = 180
LINEAGE_STATES = ("pending", "narrowd", "settled", "abandoned")


class LineagePlanner:
    """Coordinates provenance handles between the lineage stage and CheckpointLedger."""

    def __init__(self, limit=DEFAULT_LINEAGE_LIMIT, window_s=DEFAULT_LINEAGE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._handles = {}
        self._sealed = False

    def narrow(self, key, payload=None):
        """Narrow the handle named ``key``.

        Returns the stored record, or ``None`` when the lineage stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the handle named ``key``.

        Returns the stored record, or ``None`` when the lineage stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the handle named ``key``.

        Returns the stored record, or ``None`` when the lineage stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._handles)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._handles[k] for k in sorted(self._handles)]


def build_lineage(config):
    """Construct a :class:`LineagePlanner` from the ``lineage`` section of the manifest."""
    section = config.get("lineage", {})
    return LineagePlanner(
        limit=section.get("limit", DEFAULT_LINEAGE_LIMIT),
        window_s=section.get("window_s", DEFAULT_LINEAGE_WINDOW_S),
    )
