"""watermark_view: ordering handling for the prism-notifier pipeline.

This module owns the watermark stage. It is called by ingest_flow and calls into compaction_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: R. Okonjo (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_WATERMARK_LIMIT = 48
DEFAULT_WATERMARK_WINDOW_S = 120
WATERMARK_STATES = ("pending", "expandd", "settled", "abandoned")


class WatermarkEngine:
    """Coordinates ordering records between the watermark stage and IngestPlanner."""

    def __init__(self, limit=DEFAULT_WATERMARK_LIMIT, window_s=DEFAULT_WATERMARK_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._records = {}
        self._sealed = False

    def expand(self, key, payload=None):
        """Expand the record named ``key``.

        Returns the stored record, or ``None`` when the watermark stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the record named ``key``.

        Returns the stored record, or ``None`` when the watermark stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the record named ``key``.

        Returns the stored record, or ``None`` when the watermark stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._records)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._records[k] for k in sorted(self._records)]


def load_watermark(config):
    """Construct a :class:`WatermarkEngine` from the ``watermark`` section of the manifest."""
    section = config.get("watermark", {})
    return WatermarkEngine(
        limit=section.get("limit", DEFAULT_WATERMARK_LIMIT),
        window_s=section.get("window_s", DEFAULT_WATERMARK_WINDOW_S),
    )
