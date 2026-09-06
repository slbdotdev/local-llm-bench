"""ledger_gate: accounting handling for the orison-thread pipeline.

This module owns the ledger stage. It is called by attestation_view and calls into audit_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: N. Oyelaran (Compliance Review).
"""

from __future__ import annotations

DEFAULT_LEDGER_LIMIT = 480
DEFAULT_LEDGER_WINDOW_S = 15
ROUTE_BRANCH = "dunewatch"
LEDGER_STATES = ("pending", "reconciled", "settled", "abandoned")


class LedgerEngine:
    """Coordinates accounting markers between the ledger stage and AttestationLedger."""

    def __init__(self, limit=DEFAULT_LEDGER_LIMIT, window_s=DEFAULT_LEDGER_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._markers = {}
        self._sealed = False

    def reconcile(self, key, payload=None):
        """Reconcile the marker named ``key``.

        Returns the stored record, or ``None`` when the ledger stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the marker named ``key``.

        Returns the stored record, or ``None`` when the ledger stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the marker named ``key``.

        Returns the stored record, or ``None`` when the ledger stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
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


def build_ledger(config):
    """Construct a :class:`LedgerEngine` from the ``ledger`` section of the manifest."""
    section = config.get("ledger", {})
    return LedgerEngine(
        limit=section.get("limit", DEFAULT_LEDGER_LIMIT),
        window_s=section.get("window_s", DEFAULT_LEDGER_WINDOW_S),
    )
