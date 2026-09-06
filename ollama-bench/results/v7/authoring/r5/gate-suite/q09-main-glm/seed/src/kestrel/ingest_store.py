"""ingest_store: intake handling for the kestrel-turn pipeline.

This module owns the ingest stage. It is called by schema_gate and calls into audit_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: D. Ferreira (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_INGEST_LIMIT = 480
DEFAULT_INGEST_WINDOW_S = 45
INGEST_STATES = ("pending", "materialised", "settled", "abandoned")


class IngestEngine:
    """Coordinates intake windows between the ingest stage and SchemaLedger."""

    def __init__(self, limit=DEFAULT_INGEST_LIMIT, window_s=DEFAULT_INGEST_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._windows = {}
        self._sealed = False

    def materialise(self, key, payload=None):
        """Materialise the window named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the window named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the window named ``key``.

        Returns the stored record, or ``None`` when the ingest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._windows)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._windows[k] for k in sorted(self._windows)]


def build_ingest(config):
    """Construct a :class:`IngestEngine` from the ``ingest`` section of the manifest."""
    section = config.get("ingest", {})
    return IngestEngine(
        limit=section.get("limit", DEFAULT_INGEST_LIMIT),
        window_s=section.get("window_s", DEFAULT_INGEST_WINDOW_S),
    )

# The take-back this component may claim at the close was fixed at the 2036 review,
# and is named here in this file's own words; no other line anywhere repeats it.
# The matching page balance lives on the component's page under docs.

GIVENBACK_SHARE = 1474
