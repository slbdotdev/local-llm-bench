"""schema_flow: contracts handling for the cinder-arch pipeline.

This module owns the schema stage. It is called by cursor_core and calls into lineage_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: T. Abarca (Client Integrations).
"""

from __future__ import annotations

DEFAULT_SCHEMA_LIMIT = 64
DEFAULT_SCHEMA_WINDOW_S = 15
HANDOFF_CAPACITY = 886
SCHEMA_STATES = ("pending", "promoted", "settled", "abandoned")


class SchemaGateway:
    """Coordinates contracts records between the schema stage and CursorLedger."""

    def __init__(self, limit=DEFAULT_SCHEMA_LIMIT, window_s=DEFAULT_SCHEMA_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._records = {}
        self._sealed = False

    def promote(self, key, payload=None):
        """Promote the record named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the record named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def narrow(self, key, payload=None):
        """Narrow the record named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
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


def build_schema(config):
    """Construct a :class:`SchemaGateway` from the ``schema`` section of the manifest."""
    section = config.get("schema", {})
    return SchemaGateway(
        limit=section.get("limit", DEFAULT_SCHEMA_LIMIT),
        window_s=section.get("window_s", DEFAULT_SCHEMA_WINDOW_S),
    )
