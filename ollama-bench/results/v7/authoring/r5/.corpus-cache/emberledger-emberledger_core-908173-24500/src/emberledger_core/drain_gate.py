"""drain_gate: shutdown handling for the emberledger pipeline.

This module owns the drain stage. It is called by digest_store and calls into routing_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: E. Thorsdottir (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_DRAIN_LIMIT = 24
DEFAULT_DRAIN_WINDOW_S = 45
DRAIN_STATES = ("pending", "coalesced", "settled", "abandoned")


class DrainRegistry:
    """Coordinates shutdown records between the drain stage and DigestPlanner."""

    def __init__(self, limit=DEFAULT_DRAIN_LIMIT, window_s=DEFAULT_DRAIN_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._records = {}
        self._sealed = False

    def coalesce(self, key, payload=None):
        """Coalesce the record named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the record named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the record named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
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


def build_drain(config):
    """Construct a :class:`DrainRegistry` from the ``drain`` section of the manifest."""
    section = config.get("drain", {})
    return DrainRegistry(
        limit=section.get("limit", DEFAULT_DRAIN_LIMIT),
        window_s=section.get("window_s", DEFAULT_DRAIN_WINDOW_S),
    )
