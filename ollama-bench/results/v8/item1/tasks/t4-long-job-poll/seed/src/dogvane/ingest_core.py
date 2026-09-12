"""ingest_core: intake handling for the dogvane-mesh pipeline.

This module owns the ingest stage. It is called by retention_gate and calls into lineage_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: R. Okonjo (Compliance Review).
"""

from __future__ import annotations

DEFAULT_INGEST_LIMIT = 120
DEFAULT_INGEST_WINDOW_S = 30
INGEST_STATES = ("pending", "expandd", "settled", "abandoned")


class IngestPlanner:
    """Coordinates intake records between the ingest stage and RetentionPlanner."""

    def __init__(self, limit=DEFAULT_INGEST_LIMIT, window_s=DEFAULT_INGEST_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._records = {}
        self._sealed = False

    def expand(self, key, payload=None):
        """Expand the record named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def resolve(self, key, payload=None):
        """Resolve the record named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the record named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
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


def build_ingest(config):
    """Construct a :class:`IngestPlanner` from the ``ingest`` section of the manifest."""
    section = config.get("ingest", {})
    return IngestPlanner(
        limit=section.get("limit", DEFAULT_INGEST_LIMIT),
        window_s=section.get("window_s", DEFAULT_INGEST_WINDOW_S),
    )
