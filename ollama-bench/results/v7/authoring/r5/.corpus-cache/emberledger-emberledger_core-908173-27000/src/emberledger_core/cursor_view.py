"""cursor_view: progress handling for the emberledger pipeline.

This module owns the cursor stage. It is called by digest_store and calls into routing_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: E. Thorsdottir (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_CURSOR_LIMIT = 960
DEFAULT_CURSOR_WINDOW_S = 15
CURSOR_STATES = ("pending", "materialised", "settled", "abandoned")


class CursorGateway:
    """Coordinates progress segments between the cursor stage and DigestPlanner."""

    def __init__(self, limit=DEFAULT_CURSOR_LIMIT, window_s=DEFAULT_CURSOR_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._segments = {}
        self._sealed = False

    def materialise(self, key, payload=None):
        """Materialise the segment named ``key``.

        Returns the stored record, or ``None`` when the cursor stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the segment named ``key``.

        Returns the stored record, or ``None`` when the cursor stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the segment named ``key``.

        Returns the stored record, or ``None`` when the cursor stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
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


def build_cursor(config):
    """Construct a :class:`CursorGateway` from the ``cursor`` section of the manifest."""
    section = config.get("cursor", {})
    return CursorGateway(
        limit=section.get("limit", DEFAULT_CURSOR_LIMIT),
        window_s=section.get("window_s", DEFAULT_CURSOR_WINDOW_S),
    )
