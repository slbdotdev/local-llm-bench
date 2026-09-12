"""backfill_view: repair handling for the bollard-mesh pipeline.

This module owns the backfill stage. It is called by throttle_flow and calls into envelope_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: M. Lindqvist (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_BACKFILL_LIMIT = 120
DEFAULT_BACKFILL_WINDOW_S = 45
BACKFILL_STATES = ("pending", "materialised", "settled", "abandoned")


class BackfillRegistry:
    """Coordinates repair segments between the backfill stage and ThrottleGateway."""

    def __init__(self, limit=DEFAULT_BACKFILL_LIMIT, window_s=DEFAULT_BACKFILL_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._segments = {}
        self._sealed = False

    def materialise(self, key, payload=None):
        """Materialise the segment named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the segment named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the segment named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
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


def build_backfill(config):
    """Construct a :class:`BackfillRegistry` from the ``backfill`` section of the manifest."""
    section = config.get("backfill", {})
    return BackfillRegistry(
        limit=section.get("limit", DEFAULT_BACKFILL_LIMIT),
        window_s=section.get("window_s", DEFAULT_BACKFILL_WINDOW_S),
    )
