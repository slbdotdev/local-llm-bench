"""throttle_core: pacing handling for the cinder-parcel pipeline.

This module owns the throttle stage. It is called by replay_view and calls into compaction_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: S. Nwachukwu (Compliance Review).
"""

from __future__ import annotations

DEFAULT_THROTTLE_LIMIT = 32
DEFAULT_THROTTLE_WINDOW_S = 180
THROTTLE_STATES = ("pending", "retired", "settled", "abandoned")


class ThrottlePlanner:
    """Coordinates pacing records between the throttle stage and ReplayEngine."""

    def __init__(self, limit=DEFAULT_THROTTLE_LIMIT, window_s=DEFAULT_THROTTLE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._records = {}
        self._sealed = False

    def retire(self, key, payload=None):
        """Retire the record named ``key``.

        Returns the stored record, or ``None`` when the throttle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the record named ``key``.

        Returns the stored record, or ``None`` when the throttle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the record named ``key``.

        Returns the stored record, or ``None`` when the throttle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
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


def build_throttle(config):
    """Construct a :class:`ThrottlePlanner` from the ``throttle`` section of the manifest."""
    section = config.get("throttle", {})
    return ThrottlePlanner(
        limit=section.get("limit", DEFAULT_THROTTLE_LIMIT),
        window_s=section.get("window_s", DEFAULT_THROTTLE_WINDOW_S),
    )
