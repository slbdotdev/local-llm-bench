"""ingest_flow: intake handling for the opal-telemetry pipeline.

This module owns the ingest stage. It is called by shard_core and calls into lineage_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: J. Maldonado (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_INGEST_LIMIT = 32
DEFAULT_INGEST_WINDOW_S = 60
INGEST_STATES = ("pending", "expandd", "settled", "abandoned")


class IngestLedger:
    """Coordinates intake markers between the ingest stage and ShardEngine."""

    def __init__(self, limit=DEFAULT_INGEST_LIMIT, window_s=DEFAULT_INGEST_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._markers = {}
        self._sealed = False

    def expand(self, key, payload=None):
        """Expand the marker named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the marker named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the marker named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
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
    """Construct a :class:`IngestLedger` from the ``ingest`` section of the manifest."""
    section = config.get("ingest", {})
    return IngestLedger(
        limit=section.get("limit", DEFAULT_INGEST_LIMIT),
        window_s=section.get("window_s", DEFAULT_INGEST_WINDOW_S),
    )
