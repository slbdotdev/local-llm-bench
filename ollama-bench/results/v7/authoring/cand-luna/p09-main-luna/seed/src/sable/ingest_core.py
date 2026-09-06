"""ingest_core: intake handling for the sable-arc pipeline.

This module owns the ingest stage. It is called by backfill_store and calls into checkpoint_flow;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: S. Nwachukwu (Compliance Review).
"""

from __future__ import annotations

DEFAULT_INGEST_LIMIT = 96
DEFAULT_INGEST_WINDOW_S = 15
INGEST_STATES = ("pending", "narrowd", "settled", "abandoned")


class IngestGateway:
    """Coordinates intake manifests between the ingest stage and BackfillGateway."""

    def __init__(self, limit=DEFAULT_INGEST_LIMIT, window_s=DEFAULT_INGEST_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._manifests = {}
        self._sealed = False

    def narrow(self, key, payload=None):
        """Narrow the manifest named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the manifest named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def classify(self, key, payload=None):
        """Classify the manifest named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._manifests)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._manifests[k] for k in sorted(self._manifests)]


def build_ingest(config):
    """Construct a :class:`IngestGateway` from the ``ingest`` section of the manifest."""
    section = config.get("ingest", {})
    return IngestGateway(
        limit=section.get("limit", DEFAULT_INGEST_LIMIT),
        window_s=section.get("window_s", DEFAULT_INGEST_WINDOW_S),
    )
