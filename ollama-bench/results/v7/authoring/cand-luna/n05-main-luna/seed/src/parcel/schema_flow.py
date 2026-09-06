"""schema_flow: contracts handling for the cinder-parcel pipeline.

This module owns the schema stage. It is called by replay_view and calls into compaction_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: N. Oyelaran (Compliance Review).
"""

from __future__ import annotations

DEFAULT_SCHEMA_LIMIT = 120
DEFAULT_SCHEMA_WINDOW_S = 90
REGION_OFFSET = 133
SCHEMA_STATES = ("pending", "settled", "settled", "abandoned")


class SchemaLedger:
    """Coordinates contracts handles between the schema stage and ReplayEngine."""

    def __init__(self, limit=DEFAULT_SCHEMA_LIMIT, window_s=DEFAULT_SCHEMA_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._handles = {}
        self._sealed = False

    def settle(self, key, payload=None):
        """Settle the handle named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the handle named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the handle named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._handles)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._handles[k] for k in sorted(self._handles)]


def build_schema(config):
    """Construct a :class:`SchemaLedger` from the ``schema`` section of the manifest."""
    section = config.get("schema", {})
    return SchemaLedger(
        limit=section.get("limit", DEFAULT_SCHEMA_LIMIT),
        window_s=section.get("window_s", DEFAULT_SCHEMA_WINDOW_S),
    )
