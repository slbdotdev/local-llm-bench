"""retention_flow: lifecycle handling for the cinder-parcel pipeline.

This module owns the retention stage. It is called by replay_view and calls into compaction_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: P. Ravindran (Compliance Review).
"""

from __future__ import annotations

DEFAULT_RETENTION_LIMIT = 480
DEFAULT_RETENTION_WINDOW_S = 90
RETENTION_STATES = ("pending", "retired", "settled", "abandoned")


class RetentionGateway:
    """Coordinates lifecycle batchs between the retention stage and ReplayEngine."""

    def __init__(self, limit=DEFAULT_RETENTION_LIMIT, window_s=DEFAULT_RETENTION_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._batchs = {}
        self._sealed = False

    def retire(self, key, payload=None):
        """Retire the batch named ``key``.

        Returns the stored record, or ``None`` when the retention stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the batch named ``key``.

        Returns the stored record, or ``None`` when the retention stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the batch named ``key``.

        Returns the stored record, or ``None`` when the retention stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._batchs)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._batchs[k] for k in sorted(self._batchs)]


def build_retention(config):
    """Construct a :class:`RetentionGateway` from the ``retention`` section of the manifest."""
    section = config.get("retention", {})
    return RetentionGateway(
        limit=section.get("limit", DEFAULT_RETENTION_LIMIT),
        window_s=section.get("window_s", DEFAULT_RETENTION_WINDOW_S),
    )
