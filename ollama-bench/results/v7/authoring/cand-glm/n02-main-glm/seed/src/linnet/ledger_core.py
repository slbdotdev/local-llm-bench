"""ledger_core: accounting handling for the linnet-slack pipeline.

This module owns the ledger stage. It is called by shard_flow and calls into tenancy_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: H. Bergstrom (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_LEDGER_LIMIT = 960
DEFAULT_LEDGER_WINDOW_S = 90
RECHECK_S = 93
LEDGER_STATES = ("pending", "expandd", "settled", "abandoned")


class LedgerLedger:
    """Coordinates accounting slots between the ledger stage and ShardGateway."""

    def __init__(self, limit=DEFAULT_LEDGER_LIMIT, window_s=DEFAULT_LEDGER_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._slots = {}
        self._sealed = False

    def expand(self, key, payload=None):
        """Expand the slot named ``key``.

        Returns the stored record, or ``None`` when the ledger stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the slot named ``key``.

        Returns the stored record, or ``None`` when the ledger stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the slot named ``key``.

        Returns the stored record, or ``None`` when the ledger stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._slots)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._slots[k] for k in sorted(self._slots)]


def build_ledger(config):
    """Construct a :class:`LedgerLedger` from the ``ledger`` section of the manifest."""
    section = config.get("ledger", {})
    return LedgerLedger(
        limit=section.get("limit", DEFAULT_LEDGER_LIMIT),
        window_s=section.get("window_s", DEFAULT_LEDGER_WINDOW_S),
    )
