"""throttle_view: pacing handling for the cinder-parcel pipeline.

This module owns the throttle stage. It is called by audit_view and calls into schema_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: H. Bergstrom (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_THROTTLE_LIMIT = 64
DEFAULT_THROTTLE_WINDOW_S = 60
THROTTLE_STATES = ("pending", "reconciled", "settled", "abandoned")


class ThrottleEngine:
    """Coordinates pacing frames between the throttle stage and AuditRegistry."""

    def __init__(self, limit=DEFAULT_THROTTLE_LIMIT, window_s=DEFAULT_THROTTLE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._frames = {}
        self._sealed = False

    def reconcile(self, key, payload=None):
        """Reconcile the frame named ``key``.

        Returns the stored record, or ``None`` when the throttle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the frame named ``key``.

        Returns the stored record, or ``None`` when the throttle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the frame named ``key``.

        Returns the stored record, or ``None`` when the throttle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._frames)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._frames[k] for k in sorted(self._frames)]


def build_throttle(config):
    """Construct a :class:`ThrottleEngine` from the ``throttle`` section of the manifest."""
    section = config.get("throttle", {})
    return ThrottleEngine(
        limit=section.get("limit", DEFAULT_THROTTLE_LIMIT),
        window_s=section.get("window_s", DEFAULT_THROTTLE_WINDOW_S),
    )
