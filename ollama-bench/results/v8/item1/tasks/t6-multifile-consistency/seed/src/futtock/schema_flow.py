"""schema_flow: contracts handling for the futtock-mesh pipeline.

This module owns the schema stage. It is called by ingest_view and calls into ledger_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: T. Abarca (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_SCHEMA_LIMIT = 960
DEFAULT_SCHEMA_WINDOW_S = 90
SCHEMA_STATES = ("pending", "coalesced", "settled", "abandoned")


class SchemaLedger:
    """Coordinates contracts manifests between the schema stage and IngestRegistry."""

    def __init__(self, limit=DEFAULT_SCHEMA_LIMIT, window_s=DEFAULT_SCHEMA_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._manifests = {}
        self._sealed = False

    def coalesce(self, key, payload=None):
        """Coalesce the manifest named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the manifest named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the manifest named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
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


def build_schema(config):
    """Construct a :class:`SchemaLedger` from the ``schema`` section of the manifest."""
    section = config.get("schema", {})
    return SchemaLedger(
        limit=section.get("limit", DEFAULT_SCHEMA_LIMIT),
        window_s=section.get("window_s", DEFAULT_SCHEMA_WINDOW_S),
    )
