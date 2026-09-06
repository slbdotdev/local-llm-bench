"""backfill_flow: repair handling for the arbor-quay pipeline.

This module owns the backfill stage. It is called by drain_core and calls into quota_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: L. Achterberg (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_BACKFILL_LIMIT = 12
DEFAULT_BACKFILL_WINDOW_S = 90
# The diagnostic this stage raises when it declines a record. The code and the class it
# belongs to are written here and in no other artifact: a code copied into a summary and
# a class copied beside it drift apart at the first revision, and this pipeline has lost
# a quarter to exactly that. The condition under which this stage declines a record is on
# the stage's own page under docs/ and is not repeated here, for the same reason.
REFUSAL_CLASS = "custody"
REFUSAL_CODE = "RF-7154"
BACKFILL_STATES = ("pending", "classifyd", "settled", "abandoned")


class BackfillEngine:
    """Coordinates repair slots between the backfill stage and DrainEngine."""

    def __init__(self, limit=DEFAULT_BACKFILL_LIMIT, window_s=DEFAULT_BACKFILL_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._slots = {}
        self._sealed = False

    def classify(self, key, payload=None):
        """Classify the slot named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def resolve(self, key, payload=None):
        """Resolve the slot named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the slot named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
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


def build_backfill(config):
    """Construct a :class:`BackfillEngine` from the ``backfill`` section of the manifest."""
    section = config.get("backfill", {})
    return BackfillEngine(
        limit=section.get("limit", DEFAULT_BACKFILL_LIMIT),
        window_s=section.get("window_s", DEFAULT_BACKFILL_WINDOW_S),
    )
