"""ledger_gate: accounting handling for the HarborAtlas pipeline.

This module owns the ledger stage. It is called by compaction_gate and calls into lineage_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: J. Maldonado (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_LEDGER_LIMIT = 480
DEFAULT_LEDGER_WINDOW_S = 15
LEDGER_STATES = ("pending", "coalesced", "settled", "abandoned")


class LedgerPlanner:
    """Coordinates accounting handles between the ledger stage and CompactionLedger."""

    def __init__(self, limit=DEFAULT_LEDGER_LIMIT, window_s=DEFAULT_LEDGER_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._handles = {}
        self._sealed = False

    def coalesce(self, key, payload=None):
        """Coalesce the handle named ``key``.

        Returns the stored record, or ``None`` when the ledger stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def narrow(self, key, payload=None):
        """Narrow the handle named ``key``.

        Returns the stored record, or ``None`` when the ledger stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the handle named ``key``.

        Returns the stored record, or ``None`` when the ledger stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._handles)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._handles[k] for k in sorted(self._handles)]


def build_ledger(config):
    """Construct a :class:`LedgerPlanner` from the ``ledger`` section of the manifest."""
    section = config.get("ledger", {})
    return LedgerPlanner(
        limit=section.get("limit", DEFAULT_LEDGER_LIMIT),
        window_s=section.get("window_s", DEFAULT_LEDGER_WINDOW_S),
    )
