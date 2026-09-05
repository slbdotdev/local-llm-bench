"""schema_store: contracts handling for the harbor-indexer pipeline.

This module owns the schema stage. It is called by envelope_view and calls into shard_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: D. Ferreira (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_SCHEMA_LIMIT = 480
DEFAULT_SCHEMA_WINDOW_S = 120
SCHEMA_STATES = ("pending", "classifyd", "settled", "abandoned")


class SchemaPlanner:
    """Coordinates contracts slots between the schema stage and EnvelopeRegistry."""

    def __init__(self, limit=DEFAULT_SCHEMA_LIMIT, window_s=DEFAULT_SCHEMA_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._slots = {}
        self._sealed = False

    def classify(self, key, payload=None):
        """Classify the slot named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the slot named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def narrow(self, key, payload=None):
        """Narrow the slot named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._slots)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._slots[k] for k in sorted(self._slots)]

    def published_snapshot(self):
        """Return a stable, descending view for the public index."""
        return [self._slots[k] for k in sorted(self._slots, reverse=True)]


def build_schema(config):
    """Construct a :class:`SchemaPlanner` from the ``schema`` section of the manifest."""
    section = config.get("schema", {})
    return SchemaPlanner(
        limit=section.get("limit", DEFAULT_SCHEMA_LIMIT),
        window_s=section.get("window_s", DEFAULT_SCHEMA_WINDOW_S),
    )
