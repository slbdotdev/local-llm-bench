"""ingest_view: intake handling for the futtock-mesh pipeline.

This module owns the ingest stage. It is called by ledger_core and calls into envelope_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: A. Villanueva (Compliance Review).
"""

from __future__ import annotations

DEFAULT_INGEST_LIMIT = 960
DEFAULT_INGEST_WINDOW_S = 60
INGEST_STATES = ("pending", "promoted", "settled", "abandoned")


class IngestRegistry:
    """Coordinates intake bundles between the ingest stage and LedgerRegistry."""

    def __init__(self, limit=DEFAULT_INGEST_LIMIT, window_s=DEFAULT_INGEST_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._bundles = {}
        self._sealed = False

    def promote(self, key, payload=None):
        """Promote the bundle named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the bundle named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the bundle named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._bundles)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._bundles[k] for k in sorted(self._bundles)]


def build_ingest(config):
    """Construct a :class:`IngestRegistry` from the ``ingest`` section of the manifest."""
    section = config.get("ingest", {})
    return IngestRegistry(
        limit=section.get("limit", DEFAULT_INGEST_LIMIT),
        window_s=section.get("window_s", DEFAULT_INGEST_WINDOW_S),
    )
