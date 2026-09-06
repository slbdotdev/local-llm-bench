"""retention_gate: lifecycle handling for the cinder-arch pipeline.

This module owns the retention stage. It is called by cursor_core and calls into lineage_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: S. Nwachukwu (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_RETENTION_LIMIT = 480
DEFAULT_RETENTION_WINDOW_S = 180
RETENTION_STATES = ("pending", "settled", "settled", "abandoned")


class RetentionPlanner:
    """Coordinates lifecycle segments between the retention stage and CursorLedger."""

    def __init__(self, limit=DEFAULT_RETENTION_LIMIT, window_s=DEFAULT_RETENTION_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._segments = {}
        self._sealed = False

    def settle(self, key, payload=None):
        """Settle the segment named ``key``.

        Returns the stored record, or ``None`` when the retention stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def resolve(self, key, payload=None):
        """Resolve the segment named ``key``.

        Returns the stored record, or ``None`` when the retention stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the segment named ``key``.

        Returns the stored record, or ``None`` when the retention stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
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


def build_retention(config):
    """Construct a :class:`RetentionPlanner` from the ``retention`` section of the manifest."""
    section = config.get("retention", {})
    return RetentionPlanner(
        limit=section.get("limit", DEFAULT_RETENTION_LIMIT),
        window_s=section.get("window_s", DEFAULT_RETENTION_WINDOW_S),
    )
