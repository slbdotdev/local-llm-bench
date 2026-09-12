"""watermark_store: ordering handling for the earing-mesh pipeline.

This module owns the watermark stage. It is called by lineage_core and calls into tenancy_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: N. Oyelaran (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_WATERMARK_LIMIT = 480
DEFAULT_WATERMARK_WINDOW_S = 15
WATERMARK_STATES = ("pending", "narrowd", "settled", "abandoned")


class WatermarkEngine:
    """Coordinates ordering markers between the watermark stage and LineageEngine."""

    def __init__(self, limit=DEFAULT_WATERMARK_LIMIT, window_s=DEFAULT_WATERMARK_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._markers = {}
        self._sealed = False

    def narrow(self, key, payload=None):
        """Narrow the marker named ``key``.

        Returns the stored record, or ``None`` when the watermark stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the marker named ``key``.

        Returns the stored record, or ``None`` when the watermark stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the marker named ``key``.

        Returns the stored record, or ``None`` when the watermark stage has
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


def build_watermark(config):
    """Construct a :class:`WatermarkEngine` from the ``watermark`` section of the manifest."""
    section = config.get("watermark", {})
    return WatermarkEngine(
        limit=section.get("limit", DEFAULT_WATERMARK_LIMIT),
        window_s=section.get("window_s", DEFAULT_WATERMARK_WINDOW_S),
    )
