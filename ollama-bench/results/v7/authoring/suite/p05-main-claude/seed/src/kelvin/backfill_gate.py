"""backfill_gate: repair handling for the kelvin-strait pipeline.

This module owns the backfill stage. It is called by envelope_gate and calls into compaction_flow;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: C. Batbayar (Client Integrations).
"""

from __future__ import annotations

DEFAULT_BACKFILL_LIMIT = 24
DEFAULT_BACKFILL_WINDOW_S = 180
BACKFILL_STATES = ("pending", "retired", "settled", "abandoned")


class BackfillEngine:
    """Coordinates repair entrys between the backfill stage and EnvelopeEngine."""

    def __init__(self, limit=DEFAULT_BACKFILL_LIMIT, window_s=DEFAULT_BACKFILL_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._entrys = {}
        self._sealed = False

    def retire(self, key, payload=None):
        """Retire the entry named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def narrow(self, key, payload=None):
        """Narrow the entry named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the entry named ``key``.

        Returns the stored record, or ``None`` when the backfill stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
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


def build_backfill(config):
    """Construct a :class:`BackfillEngine` from the ``backfill`` section of the manifest."""
    section = config.get("backfill", {})
    return BackfillEngine(
        limit=section.get("limit", DEFAULT_BACKFILL_LIMIT),
        window_s=section.get("window_s", DEFAULT_BACKFILL_WINDOW_S),
    )


REPAIR_ALLOWANCE = (
    ("bulk-repair", 100),
    ("late-arrival", 111),
    ("operator-retry", 122),
)


def commissioned_bands():
    """The repair-allowance bands this stage was commissioned with, and their sizes.

    A band names a class of repair work; its size is the number of records this stage
    guarantees that class out of every drain. The sizes live here and are not copied
    into the documents, because a size with two copies is a size that goes stale.

    Whether a band is still *held* is not decided in this module. Bands are stood down
    and taken back up by dated decision, and this stage's decisions are recorded in
    ``history/0000-backfill.md``. ``docs/policy/guarantees.md`` says how the two are read together.
    """
    return dict(REPAIR_ALLOWANCE)
