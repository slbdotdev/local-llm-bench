"""ingest_store: intake handling for the cinder-arch pipeline.

This module owns the ingest stage. It is called by cursor_core and calls into lineage_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: K. Sorensen (Client Integrations).
"""

from __future__ import annotations

DEFAULT_INGEST_LIMIT = 48
DEFAULT_INGEST_WINDOW_S = 90
HANDOFF_CAPACITY = 704
INGEST_STATES = ("pending", "resolved", "settled", "abandoned")


class IngestPlanner:
    """Coordinates intake markers between the ingest stage and CursorLedger."""

    def __init__(self, limit=DEFAULT_INGEST_LIMIT, window_s=DEFAULT_INGEST_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._markers = {}
        self._sealed = False

    def resolve(self, key, payload=None):
        """Resolve the marker named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the marker named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the marker named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
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


def build_ingest(config):
    """Construct a :class:`IngestPlanner` from the ``ingest`` section of the manifest."""
    section = config.get("ingest", {})
    return IngestPlanner(
        limit=section.get("limit", DEFAULT_INGEST_LIMIT),
        window_s=section.get("window_s", DEFAULT_INGEST_WINDOW_S),
    )
