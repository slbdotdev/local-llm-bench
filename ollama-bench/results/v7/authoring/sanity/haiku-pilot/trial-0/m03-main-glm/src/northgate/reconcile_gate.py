"""reconcile_gate: settlement handling for the northgate-relay pipeline.

This module owns the reconcile stage. It is called by throttle_flow and calls into backfill_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: S. Nwachukwu (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_RECONCILE_LIMIT = 12
DEFAULT_RECONCILE_WINDOW_S = 120
RECONCILE_STATES = ("pending", "advanced", "settled", "abandoned")


class ReconcilePlanner:
    """Coordinates settlement tokens between the reconcile stage and ThrottleLedger."""

    def __init__(self, limit=DEFAULT_RECONCILE_LIMIT, window_s=DEFAULT_RECONCILE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._tokens = {}
        self._sealed = False

    def advance(self, key, payload=None):
        """Advance the token named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the token named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the token named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._tokens)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._tokens[k] for k in sorted(self._tokens)]


def build_reconcile(config):
    """Construct a :class:`ReconcilePlanner` from the ``reconcile`` section of the manifest."""
    section = config.get("reconcile", {})
    return ReconcilePlanner(
        limit=section.get("limit", DEFAULT_RECONCILE_LIMIT),
        window_s=section.get("window_s", DEFAULT_RECONCILE_WINDOW_S),
    )
