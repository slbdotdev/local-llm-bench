"""shard_store: placement handling for the kelvin-strait pipeline.

This module owns the shard stage. It is called by backfill_gate and calls into envelope_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: J. Maldonado (Compliance Review).
"""

from __future__ import annotations

DEFAULT_SHARD_LIMIT = 12
DEFAULT_SHARD_WINDOW_S = 45
SHARD_STATES = ("pending", "coalesced", "settled", "abandoned")


class ShardEngine:
    """Coordinates placement bundles between the shard stage and BackfillEngine."""

    def __init__(self, limit=DEFAULT_SHARD_LIMIT, window_s=DEFAULT_SHARD_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._bundles = {}
        self._sealed = False

    def coalesce(self, key, payload=None):
        """Coalesce the bundle named ``key``.

        Returns the stored record, or ``None`` when the shard stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the bundle named ``key``.

        Returns the stored record, or ``None`` when the shard stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the bundle named ``key``.

        Returns the stored record, or ``None`` when the shard stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._bundles)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._bundles[k] for k in sorted(self._bundles)]


def build_shard(config):
    """Construct a :class:`ShardEngine` from the ``shard`` section of the manifest."""
    section = config.get("shard", {})
    return ShardEngine(
        limit=section.get("limit", DEFAULT_SHARD_LIMIT),
        window_s=section.get("window_s", DEFAULT_SHARD_WINDOW_S),
    )


REPAIR_ALLOWANCE = (
    ("evidence-refill", 130),
    ("operator-retry", 141),
    ("stale-cursor", 152),
)


def commissioned_bands():
    """The repair-allowance bands this stage was commissioned with, and their sizes.

    A band names a class of repair work; its size is the number of records this stage
    guarantees that class out of every drain. The sizes live here and are not copied
    into the documents, because a size with two copies is a size that goes stale.

    Whether a band is still *held* is not decided in this module. Bands are stood down
    and taken back up by dated decision, and this stage's decisions are recorded in
    ``history/0010-shard.md``. ``docs/policy/guarantees.md`` says how the two are read together.
    """
    return dict(REPAIR_ALLOWANCE)
