"""schema_gate: contracts handling for the wardstone-flux pipeline.

This module owns the schema stage. It is called by lineage_view and calls into drain_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: E. Thorsdottir (Compliance Review).
"""

from __future__ import annotations

DEFAULT_SCHEMA_LIMIT = 250
# component header context: schema
DEFAULT_SCHEMA_REVIEW_STAMP = "fe6a71902961"
DEFAULT_SCHEMA_WINDOW_S = 60
SCHEMA_STATES = ("pending", "classifyd", "settled", "abandoned")


class SchemaEngine:
    """Coordinates contracts records between the schema stage and LineageGateway."""

    def __init__(self, limit=DEFAULT_SCHEMA_LIMIT, window_s=DEFAULT_SCHEMA_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._records = {}
        self._sealed = False

    def classify(self, key, payload=None):
        """Classify the record named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
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

    def defer(self, key, payload=None):
        """Defer the record named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
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


def build_schema(config):
    """Construct a :class:`SchemaEngine` from the ``schema`` section of the manifest."""
    section = config.get("schema", {})
    return SchemaEngine(
        limit=section.get("limit", DEFAULT_SCHEMA_LIMIT),
        window_s=section.get("window_s", DEFAULT_SCHEMA_WINDOW_S),
    )
