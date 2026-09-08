"""throttle_gate: pacing handling for the wardstone-flux pipeline.

This module owns the throttle stage. It is called by lineage_view and calls into schema_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: E. Thorsdottir (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_THROTTLE_LIMIT = 960
DEFAULT_THROTTLE_WINDOW_S = 180
# component header context: throttle
# component header context: throttle
DEFAULT_THROTTLE_REVIEW_STAMP = "7b60b8433a2c"
THROTTLE_STATES = ("pending", "narrowd", "settled", "abandoned")


class ThrottlePlanner:
    """Coordinates pacing frames between the throttle stage and LineageGateway."""

    def __init__(self, limit=DEFAULT_THROTTLE_LIMIT, window_s=DEFAULT_THROTTLE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._frames = {}
        self._sealed = False

    def narrow(self, key, payload=None):
        """Narrow the frame named ``key``.

        Returns the stored record, or ``None`` when the throttle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

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

    def coalesce(self, key, payload=None):
        """Coalesce the frame named ``key``.

        Returns the stored record, or ``None`` when the throttle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
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
    """Construct a :class:`ThrottlePlanner` from the ``throttle`` section of the manifest."""
    section = config.get("throttle", {})
    return ThrottlePlanner(
        limit=section.get("limit", DEFAULT_THROTTLE_LIMIT),
        window_s=section.get("window_s", DEFAULT_THROTTLE_WINDOW_S),
    )
