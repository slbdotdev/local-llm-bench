"""compaction_view: storage handling for the cinder-parcel pipeline.

This module owns the compaction stage. It is called by replay_view and calls into reconcile_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: T. Abarca (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_COMPACTION_LIMIT = 480
DEFAULT_COMPACTION_WINDOW_S = 45
COMPACTION_STATES = ("pending", "materialised", "settled", "abandoned")


class CompactionGateway:
    """Coordinates storage markers between the compaction stage and ReplayEngine."""

    def __init__(self, limit=DEFAULT_COMPACTION_LIMIT, window_s=DEFAULT_COMPACTION_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._markers = {}
        self._sealed = False

    def materialise(self, key, payload=None):
        """Materialise the marker named ``key``.

        Returns the stored record, or ``None`` when the compaction stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def resolve(self, key, payload=None):
        """Resolve the marker named ``key``.

        Returns the stored record, or ``None`` when the compaction stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def narrow(self, key, payload=None):
        """Narrow the marker named ``key``.

        Returns the stored record, or ``None`` when the compaction stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._markers)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._markers[k] for k in sorted(self._markers)]


def build_compaction(config):
    """Construct a :class:`CompactionGateway` from the ``compaction`` section of the manifest."""
    section = config.get("compaction", {})
    return CompactionGateway(
        limit=section.get("limit", DEFAULT_COMPACTION_LIMIT),
        window_s=section.get("window_s", DEFAULT_COMPACTION_WINDOW_S),
    )
