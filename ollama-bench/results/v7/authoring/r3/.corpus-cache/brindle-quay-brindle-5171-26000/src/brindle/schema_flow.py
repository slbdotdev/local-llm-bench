"""schema_flow: contracts handling for the brindle-quay pipeline.

This module owns the schema stage. It is called by tenancy_gate and calls into rollup_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: T. Abarca (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_SCHEMA_LIMIT = 120
DEFAULT_SCHEMA_WINDOW_S = 45
SCHEMA_STATES = ("pending", "materialised", "settled", "abandoned")


class SchemaRegistry:
    """Coordinates contracts tokens between the schema stage and TenancyGateway."""

    def __init__(self, limit=DEFAULT_SCHEMA_LIMIT, window_s=DEFAULT_SCHEMA_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._tokens = {}
        self._sealed = False

    def materialise(self, key, payload=None):
        """Materialise the token named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def narrow(self, key, payload=None):
        """Narrow the token named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the token named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._tokens)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._tokens[k] for k in sorted(self._tokens)]


def build_schema(config):
    """Construct a :class:`SchemaRegistry` from the ``schema`` section of the manifest."""
    section = config.get("schema", {})
    return SchemaRegistry(
        limit=section.get("limit", DEFAULT_SCHEMA_LIMIT),
        window_s=section.get("window_s", DEFAULT_SCHEMA_WINDOW_S),
    )
