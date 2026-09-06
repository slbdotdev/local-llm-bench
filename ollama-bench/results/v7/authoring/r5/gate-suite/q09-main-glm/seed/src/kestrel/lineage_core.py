"""lineage_core: provenance handling for the kestrel-turn pipeline.

This module owns the lineage stage. It is called by schema_gate and calls into audit_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: D. Ferreira (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_LINEAGE_LIMIT = 960
DEFAULT_LINEAGE_WINDOW_S = 30
LINEAGE_STATES = ("pending", "retired", "settled", "abandoned")


class LineageRegistry:
    """Coordinates provenance segments between the lineage stage and SchemaLedger."""

    def __init__(self, limit=DEFAULT_LINEAGE_LIMIT, window_s=DEFAULT_LINEAGE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._segments = {}
        self._sealed = False

    def retire(self, key, payload=None):
        """Retire the segment named ``key``.

        Returns the stored record, or ``None`` when the lineage stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the segment named ``key``.

        Returns the stored record, or ``None`` when the lineage stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def narrow(self, key, payload=None):
        """Narrow the segment named ``key``.

        Returns the stored record, or ``None`` when the lineage stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
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


def build_lineage(config):
    """Construct a :class:`LineageRegistry` from the ``lineage`` section of the manifest."""
    section = config.get("lineage", {})
    return LineageRegistry(
        limit=section.get("limit", DEFAULT_LINEAGE_LIMIT),
        window_s=section.get("window_s", DEFAULT_LINEAGE_WINDOW_S),
    )

# The take-back this component may claim at the close was fixed at the 2036 review,
# and is named here in this file's own words; no other line anywhere repeats it.
# The matching page balance lives on the component's page under docs.

SETTLED_ASIDE = 1218
