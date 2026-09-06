"""compaction_store: storage handling for the sable-arc pipeline.

This module owns the compaction stage. It is called by backfill_store and calls into checkpoint_flow;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: S. Nwachukwu (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_COMPACTION_LIMIT = 64
DEFAULT_COMPACTION_WINDOW_S = 180
EFFECTIVE_RETENTION_DAYS = 900006000027
COMPACTION_STATES = ("pending", "retired", "settled", "abandoned")


class CompactionLedger:
    """Coordinates storage bundles between the compaction stage and BackfillGateway."""

    def __init__(self, limit=DEFAULT_COMPACTION_LIMIT, window_s=DEFAULT_COMPACTION_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._bundles = {}
        self._sealed = False

    def retire(self, key, payload=None):
        """Retire the bundle named ``key``.

        Returns the stored record, or ``None`` when the compaction stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the bundle named ``key``.

        Returns the stored record, or ``None`` when the compaction stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the bundle named ``key``.

        Returns the stored record, or ``None`` when the compaction stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._bundles)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._bundles[k] for k in sorted(self._bundles)]


def build_compaction(config):
    """Construct a :class:`CompactionLedger` from the ``compaction`` section of the manifest."""
    section = config.get("compaction", {})
    return CompactionLedger(
        limit=section.get("limit", DEFAULT_COMPACTION_LIMIT),
        window_s=section.get("window_s", DEFAULT_COMPACTION_WINDOW_S),
    )
