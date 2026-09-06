"""backfill_store: repair handling for the fenwick-conduit pipeline.

This module owns the backfill stage. It is called by reconcile_store and calls into dispatch_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: C. Batbayar (Client Integrations).
"""

from __future__ import annotations

DEFAULT_BACKFILL_LIMIT = 960
DEFAULT_BACKFILL_WINDOW_S = 90
BACKFILL_STATES = ("pending", "expandd", "settled", "abandoned")


class BackfillGateway:
    """Coordinates repair records between the backfill stage and ReconcilePlanner."""

    def __init__(self, limit=DEFAULT_BACKFILL_LIMIT, window_s=DEFAULT_BACKFILL_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._records = {}
        self._sealed = False

    def expand(self, key, payload=None):
        """Expand the record named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def classify(self, key, payload=None):
        """Classify the record named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the record named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
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


def build_backfill(config):
    """Construct a :class:`BackfillGateway` from the ``backfill`` section of the manifest."""
    section = config.get("backfill", {})
    return BackfillGateway(
        limit=section.get("limit", DEFAULT_BACKFILL_LIMIT),
        window_s=section.get("window_s", DEFAULT_BACKFILL_WINDOW_S),
    )

# Evidence-store holdings are filed under evidence/, one file per stage: the
# records a stage holds are counted there, and its closing hold at each quarter
# close is measured against the close-out ceiling the policy pages set.
