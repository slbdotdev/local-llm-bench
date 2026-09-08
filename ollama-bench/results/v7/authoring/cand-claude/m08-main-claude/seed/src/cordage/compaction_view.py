"""compaction_view: storage handling for the cordage-relay pipeline.

This module owns the compaction stage. It is called by checkpoint_store and calls into attestation_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: S. Nwachukwu (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_COMPACTION_CAPACITY_ACK = "CA-02"
DEFAULT_COMPACTION_LIMIT = 32
DEFAULT_COMPACTION_WINDOW_S = 15
COMPACTION_STATES = ("pending", "admitd", "settled", "abandoned")


class CompactionLedger:
    """Coordinates storage entrys between the compaction stage and CheckpointEngine."""

    def __init__(self, limit=DEFAULT_COMPACTION_LIMIT, window_s=DEFAULT_COMPACTION_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._entrys = {}
        self._sealed = False

    def admit(self, key, payload=None):
        """Admit the entry named ``key``.

        Returns the stored record, or ``None`` when the compaction stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the entry named ``key``.

        Returns the stored record, or ``None`` when the compaction stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the entry named ``key``.

        Returns the stored record, or ``None`` when the compaction stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._entrys)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._entrys[k] for k in sorted(self._entrys)]


def build_compaction(config):
    """Construct a :class:`CompactionLedger` from the ``compaction`` section of the manifest."""
    section = config.get("compaction", {})
    return CompactionLedger(
        limit=section.get("limit", DEFAULT_COMPACTION_LIMIT),
        window_s=section.get("window_s", DEFAULT_COMPACTION_WINDOW_S),
    )
