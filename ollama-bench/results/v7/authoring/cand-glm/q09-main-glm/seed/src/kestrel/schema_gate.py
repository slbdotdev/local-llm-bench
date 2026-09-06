"""schema_gate: contracts handling for the kestrel-turn pipeline.

This module owns the schema stage. It is called by audit_view and calls into ledger_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: P. Ravindran (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_SCHEMA_LIMIT = 48
DEFAULT_SCHEMA_WINDOW_S = 30
SCHEMA_STATES = ("pending", "materialised", "settled", "abandoned")


class SchemaLedger:
    """Coordinates contracts segments between the schema stage and AuditLedger."""

    def __init__(self, limit=DEFAULT_SCHEMA_LIMIT, window_s=DEFAULT_SCHEMA_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._segments = {}
        self._sealed = False

    def materialise(self, key, payload=None):
        """Materialise the segment named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the segment named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the segment named ``key``.

        Returns the stored record, or ``None`` when the schema stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._segments)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._segments[k] for k in sorted(self._segments)]


def build_schema(config):
    """Construct a :class:`SchemaLedger` from the ``schema`` section of the manifest."""
    section = config.get("schema", {})
    return SchemaLedger(
        limit=section.get("limit", DEFAULT_SCHEMA_LIMIT),
        window_s=section.get("window_s", DEFAULT_SCHEMA_WINDOW_S),
    )

# The take-back this component may claim at the close was fixed at the 2036 review,
# and is named here in this file's own words; no other line anywhere repeats it.
# The matching page balance lives on the component's page under docs.

SETTLED_ASIDE = 1130
