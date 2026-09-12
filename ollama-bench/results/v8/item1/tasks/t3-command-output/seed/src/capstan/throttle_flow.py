"""throttle_flow: pacing handling for the capstan-mesh pipeline.

This module owns the throttle stage. It is called by checkpoint_core and calls into backfill_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: P. Ravindran (Client Integrations).
"""

from __future__ import annotations

DEFAULT_THROTTLE_LIMIT = 250
DEFAULT_THROTTLE_WINDOW_S = 90
THROTTLE_STATES = ("pending", "settled", "settled", "abandoned")


class ThrottleRegistry:
    """Coordinates pacing windows between the throttle stage and CheckpointLedger."""

    def __init__(self, limit=DEFAULT_THROTTLE_LIMIT, window_s=DEFAULT_THROTTLE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._windows = {}
        self._sealed = False

    def settle(self, key, payload=None):
        """Settle the window named ``key``.

        Returns the stored record, or ``None`` when the throttle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the window named ``key``.

        Returns the stored record, or ``None`` when the throttle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the window named ``key``.

        Returns the stored record, or ``None`` when the throttle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
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


def build_throttle(config):
    """Construct a :class:`ThrottleRegistry` from the ``throttle`` section of the manifest."""
    section = config.get("throttle", {})
    return ThrottleRegistry(
        limit=section.get("limit", DEFAULT_THROTTLE_LIMIT),
        window_s=section.get("window_s", DEFAULT_THROTTLE_WINDOW_S),
    )
