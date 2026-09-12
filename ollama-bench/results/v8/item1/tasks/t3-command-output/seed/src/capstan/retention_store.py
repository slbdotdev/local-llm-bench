"""retention_store: lifecycle handling for the capstan-mesh pipeline.

This module owns the retention stage. It is called by checkpoint_core and calls into backfill_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: P. Ravindran (Client Integrations).
"""

from __future__ import annotations

DEFAULT_RETENTION_LIMIT = 48
DEFAULT_RETENTION_WINDOW_S = 180
RETENTION_STATES = ("pending", "narrowd", "settled", "abandoned")


class RetentionGateway:
    """Coordinates lifecycle records between the retention stage and CheckpointLedger."""

    def __init__(self, limit=DEFAULT_RETENTION_LIMIT, window_s=DEFAULT_RETENTION_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._records = {}
        self._sealed = False

    def narrow(self, key, payload=None):
        """Narrow the record named ``key``.

        Returns the stored record, or ``None`` when the retention stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the record named ``key``.

        Returns the stored record, or ``None`` when the retention stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the record named ``key``.

        Returns the stored record, or ``None`` when the retention stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
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


def build_retention(config):
    """Construct a :class:`RetentionGateway` from the ``retention`` section of the manifest."""
    section = config.get("retention", {})
    return RetentionGateway(
        limit=section.get("limit", DEFAULT_RETENTION_LIMIT),
        window_s=section.get("window_s", DEFAULT_RETENTION_WINDOW_S),
    )
