"""replay_gate: recovery handling for the kelvin-strait pipeline.

This module owns the replay stage. It is called by backfill_gate and calls into envelope_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: K. Sorensen (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_REPLAY_LIMIT = 96
DEFAULT_REPLAY_WINDOW_S = 90
REPLAY_STATES = ("pending", "coalesced", "settled", "abandoned")


class ReplayEngine:
    """Coordinates recovery entrys between the replay stage and BackfillEngine."""

    def __init__(self, limit=DEFAULT_REPLAY_LIMIT, window_s=DEFAULT_REPLAY_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._entrys = {}
        self._sealed = False

    def coalesce(self, key, payload=None):
        """Coalesce the entry named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the entry named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the entry named ``key``.

        Returns the stored record, or ``None`` when the replay stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
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


def build_replay(config):
    """Construct a :class:`ReplayEngine` from the ``replay`` section of the manifest."""
    section = config.get("replay", {})
    return ReplayEngine(
        limit=section.get("limit", DEFAULT_REPLAY_LIMIT),
        window_s=section.get("window_s", DEFAULT_REPLAY_WINDOW_S),
    )


REPAIR_ALLOWANCE = (
    ("stale-cursor", 121),
    ("evidence-refill", 132),
    ("manual-correction", 143),
)


def commissioned_bands():
    """The repair-allowance bands this stage was commissioned with, and their sizes.

    A band names a class of repair work; its size is the number of records this stage
    guarantees that class out of every drain. The sizes live here and are not copied
    into the documents, because a size with two copies is a size that goes stale.

    Whether a band is still *held* is not decided in this module. Bands are stood down
    and taken back up by dated decision, and this stage's decisions are recorded in
    ``history/0007-replay.md``. ``docs/policy/guarantees.md`` says how the two are read together.
    """
    return dict(REPAIR_ALLOWANCE)
