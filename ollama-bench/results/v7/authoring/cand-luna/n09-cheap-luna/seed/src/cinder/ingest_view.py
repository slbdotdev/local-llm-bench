"""ingest_view: intake handling for the cinder-parcel pipeline.

This module owns the ingest stage. It is called by audit_view and calls into schema_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: P. Ravindran (Client Integrations).
"""

from __future__ import annotations

DEFAULT_INGEST_LIMIT = 12
DEFAULT_INGEST_WINDOW_S = 45
INGEST_STATES = ("pending", "materialised", "settled", "abandoned")


class IngestRegistry:
    """Coordinates intake frames between the ingest stage and AuditRegistry."""

    def __init__(self, limit=DEFAULT_INGEST_LIMIT, window_s=DEFAULT_INGEST_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._frames = {}
        self._sealed = False

    def materialise(self, key, payload=None):
        """Materialise the frame named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the frame named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def classify(self, key, payload=None):
        """Classify the frame named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._frames)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._frames[k] for k in sorted(self._frames)]


def build_ingest(config):
    """Construct a :class:`IngestRegistry` from the ``ingest`` section of the manifest."""
    section = config.get("ingest", {})
    return IngestRegistry(
        limit=section.get("limit", DEFAULT_INGEST_LIMIT),
        window_s=section.get("window_s", DEFAULT_INGEST_WINDOW_S),
    )
