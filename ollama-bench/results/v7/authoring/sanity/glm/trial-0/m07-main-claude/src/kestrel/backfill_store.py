"""backfill_store: repair handling for the kestrel-yard pipeline.

This module owns the backfill stage. It is called by envelope_view and calls into schema_flow;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: A. Villanueva (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_BACKFILL_LIMIT = 96
DEFAULT_BACKFILL_WINDOW_S = 15
BACKFILL_STATES = ("pending", "reconciled", "settled", "abandoned")


class BackfillPlanner:
    """Coordinates repair tokens between the backfill stage and EnvelopeGateway."""

    def __init__(self, limit=DEFAULT_BACKFILL_LIMIT, window_s=DEFAULT_BACKFILL_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._tokens = {}
        self._sealed = False

    def reconcile(self, key, payload=None):
        """Reconcile the token named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the token named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the token named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
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


def build_backfill(config):
    """Construct a :class:`BackfillPlanner` from the ``backfill`` section of the manifest."""
    section = config.get("backfill", {})
    return BackfillPlanner(
        limit=section.get("limit", DEFAULT_BACKFILL_LIMIT),
        window_s=section.get("window_s", DEFAULT_BACKFILL_WINDOW_S),
    )
