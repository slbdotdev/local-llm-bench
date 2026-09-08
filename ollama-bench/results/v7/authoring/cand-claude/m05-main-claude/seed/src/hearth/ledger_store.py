"""ledger_store: accounting handling for the hearth-relay pipeline.

This module owns the ledger stage. It is called by retention_gate and calls into quota_flow;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: R. Okonjo (Client Integrations).
"""

from __future__ import annotations

DEFAULT_LEDGER_LIMIT = 250
DEFAULT_LEDGER_WINDOW_S = 45
# placement marker 00
# placement marker 01
# placement marker 02
# placement marker 03
# placement marker 04
# placement marker 05
# placement marker 06
# placement marker 07
# placement marker 08
# placement marker 09
# placement marker 10
# placement marker 11
# placement marker 12
# placement marker 13
ACTIVE_WINDOW_S = 2269
LEDGER_STATES = ("pending", "promoted", "settled", "abandoned")


class LedgerEngine:
    """Coordinates accounting slots between the ledger stage and RetentionLedger."""

    def __init__(self, limit=DEFAULT_LEDGER_LIMIT, window_s=DEFAULT_LEDGER_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._slots = {}
        self._sealed = False

    def promote(self, key, payload=None):
        """Promote the slot named ``key``.

        Returns the stored record, or ``None`` when the ledger stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the slot named ``key``.

        Returns the stored record, or ``None`` when the ledger stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

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

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._slots)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._slots[k] for k in sorted(self._slots)]


def build_ledger(config):
    """Construct a :class:`LedgerEngine` from the ``ledger`` section of the manifest."""
    section = config.get("ledger", {})
    return LedgerEngine(
        limit=section.get("limit", DEFAULT_LEDGER_LIMIT),
        window_s=section.get("window_s", DEFAULT_LEDGER_WINDOW_S),
    )
